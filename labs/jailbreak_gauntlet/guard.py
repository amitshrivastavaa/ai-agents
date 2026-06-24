"""A heuristic guardrail policy and the verdict it produces.

The :class:`Guard` layers detectors for each attack class, plus a
*decode-and-rescan* step that base64/ROT13-decodes embedded payloads and
re-runs the keyword detectors on the result — catching obfuscated injections a
flat keyword filter would miss.

It is deliberately *not* perfect: it normalizes whitespace and case but not
Unicode confusables/zero-width characters, and it keys on surface patterns, so
indirect or homoglyph-obfuscated attacks slip past. That's the point — the
harness measures exactly where a given guard is strong and where it leaks, so
you can improve it and lock the gain in with a regression test.
"""
from __future__ import annotations

import base64
import codecs
import re
from dataclasses import dataclass, field

from . import probes as P


@dataclass
class Verdict:
    blocked: bool
    category: str | None       # primary (highest-weight) category that fired
    score: int                 # summed severity weight of fired detectors
    reasons: list[str] = field(default_factory=list)
    fired: list[tuple[str, int]] = field(default_factory=list)  # (category, weight)


def _rx(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)


# (category, weight, pattern) — surface detectors run on normalized text.
_CORE = [
    # instruction override
    (P.OVERRIDE, 4, _rx(r"\b(ignore|disregard|forget|override|bypass)\b[^.\n]{0,40}"
                        r"\b(previous|prior|above|earlier|all|your|the)\b[^.\n]{0,24}"
                        r"\b(instruction|instructions|rule|rules|prompt|directive|"
                        r"direction|configuration|policy|guardrail|guardrails)\b")),
    (P.OVERRIDE, 4, _rx(r"\bforget (everything|all|what)\b")),
    (P.OVERRIDE, 3, _rx(r"\bno (restrictions|rules|limits|guardrails|filter|filters)\b")),
    (P.OVERRIDE, 3, _rx(r"\bfrom now on\b[^.\n]{0,30}\b(no longer|ignore|unrestricted|"
                        r"no rules|no restrictions|comply)\b")),
    (P.OVERRIDE, 4, _rx(r"\bnew (directive|instructions?)\b\s*:")),
    (P.OVERRIDE, 4, _rx(r"\bsystem update\b")),
    (P.OVERRIDE, 4, _rx(r"\b(previous|prior) (configuration|instructions?) (is|are) void\b")),
    # system prompt leak
    (P.LEAK, 4, _rx(r"\b(reveal|show|print|repeat|output|display|tell me|give me)\b"
                    r"[^.\n]{0,30}\b(system )?(prompt|instructions|directive|rules)\b")),
    (P.LEAK, 4, _rx(r"\b(repeat|print|output) the words above\b")),
    (P.LEAK, 3, _rx(r"\bword for word\b|\bverbatim\b")),
    (P.LEAK, 4, _rx(r"\bwhat are your (exact )?(system )?(instructions|rules|prompt)\b")),
    (P.LEAK, 4, _rx(r"\bhidden (system )?prompt\b")),
    # delimiter / fake-role injection
    (P.DELIMITER, 5, _rx(r"<\|?\s*(system|im_start|im_end|end)\s*\|?>")),
    (P.DELIMITER, 4, _rx(r"```+\s*system")),
    (P.DELIMITER, 4, _rx(r"#{2,}\s*system")),
    (P.DELIMITER, 4, _rx(r"\[\s*system\s*\]")),
    (P.DELIMITER, 3, _rx(r"(^|\n)\s*(assistant|system)\s*:")),
    # tool / privilege escalation
    (P.TOOL, 5, _rx(r"\brm\s+-rf\b|--no-preserve-root")),
    (P.TOOL, 5, _rx(r"\bdrop\s+table\b")),
    (P.TOOL, 5, _rx(r"\bos\.system\b|\bsubprocess\b|\beval\(|\bexec\(")),
    (P.TOOL, 4, _rx(r"\bcurl\s+https?://|\|\s*sh\b|\bwget\s+https?://")),
    (P.TOOL, 5, _rx(r"\bwire transfer\b|\btransfer (of )?\$?\d")),
    # data exfiltration
    (P.EXFIL, 5, _rx(r"/etc/passwd|\benv(ironment)? vars?\b|\benvironment variables\b")),
    (P.EXFIL, 5, _rx(r"\bapi[_ ]?keys?\b|\bsecret keys?\b|sk-[a-z0-9]{8,}")),
    (P.EXFIL, 4, _rx(r"\bpost\b[^.\n]{0,40}https?://|\bsend\b[^.\n]{0,30}\bto https?://")),
    (P.EXFIL, 4, _rx(r"\bssn\b|\bsocial security\b|\bcredit card\b")),
    (P.EXFIL, 4, _rx(r"https?://(evil|attacker|exfil|malicious)\b")),
    # roleplay smuggling
    (P.ROLEPLAY, 4, _rx(r"\byou are (now )?(dan\b|an? (unrestricted|jailbroken|unfiltered))")),
    (P.ROLEPLAY, 3, _rx(r"\bstay in character\b|\bdeveloper mode\b")),
    (P.ROLEPLAY, 3, _rx(r"\bpretend (you are|to be)\b|\bact as\b|\brole-?play\b")),
    (P.ROLEPLAY, 3, _rx(r"\bfor a (fictional|movie|story|hypothetical)\b[^.\n]{0,80}"
                        r"\b(hack|disable|bypass|exploit|firewall|malware|weapon)")),
]

_B64 = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")


@dataclass
class Guard:
    """A configurable guardrail. ``strict`` blocks on any hit; otherwise it
    blocks only once summed severity reaches ``threshold``."""

    strict: bool = True
    threshold: int = 4
    decode_payloads: bool = True

    @staticmethod
    def normalize(text: str) -> str:
        # lowercase + collapse whitespace. Intentionally does NOT strip Unicode
        # confusables / zero-width chars — a known, measurable gap.
        return re.sub(r"\s+", " ", text.lower())

    def _surface_scan(self, text: str) -> list[tuple[str, int, str]]:
        hits: list[tuple[str, int, str]] = []
        for category, weight, pattern in _CORE:
            if pattern.search(text):
                hits.append((category, weight, f"{category}: matched /{pattern.pattern[:48]}/"))
        return hits

    def _decode_scan(self, raw: str, norm: str) -> list[tuple[str, int, str]]:
        hits: list[tuple[str, int, str]] = []
        # base64 blobs → decode → re-scan
        for blob in _B64.findall(raw):
            padded = blob + "=" * (-len(blob) % 4)
            try:
                decoded = base64.b64decode(padded, validate=False).decode("utf-8", "ignore")
            except Exception:
                continue
            if len(decoded) < 4 or not re.search(r"[a-zA-Z]", decoded):
                continue
            inner = self._surface_scan(self.normalize(decoded))
            if inner:
                kinds = ",".join(sorted({c for c, _, _ in inner}))
                hits.append((P.ENCODED, 5, f"encoded_payload: base64 decoded to [{kinds}]"))
        # rot13 the whole message → re-scan
        rot = codecs.decode(norm, "rot_13")
        if self._surface_scan(rot):
            hits.append((P.ENCODED, 4, "encoded_payload: rot13 decoded to an injection"))
        # explicit obfuscation cues
        if re.search(r"\b(base64|rot13|hex|decode (this|the following))\b", norm):
            hits.append((P.ENCODED, 3, "encoded_payload: explicit decode instruction"))
        return hits

    def inspect(self, text: str) -> Verdict:
        norm = self.normalize(text)
        hits = self._surface_scan(norm)
        if self.decode_payloads:
            hits += self._decode_scan(text, norm)
        return self._verdict(hits)

    def inspect_output(self, text: str, secrets: tuple[str, ...] = ()) -> Verdict:
        """Output-side guard: catch leaked secrets / system-prompt markers."""
        hits: list[tuple[str, int, str]] = []
        low = text.lower()
        for secret in secrets:
            if secret and secret.lower() in low:
                hits.append((P.EXFIL, 5, "data_exfiltration: response contains a secret canary"))
        if re.search(r"sk-[a-z0-9]{8,}", low):
            hits.append((P.EXFIL, 5, "data_exfiltration: response contains an API-key-like token"))
        if re.search(r"\byou are (a|an|the)\b.*\b(assistant|model)\b", low) and "system prompt" in low:
            hits.append((P.LEAK, 4, "system_prompt_leak: response echoes the system prompt"))
        return self._verdict(hits)

    def _verdict(self, hits: list[tuple[str, int, str]]) -> Verdict:
        if not hits:
            return Verdict(blocked=False, category=None, score=0)
        # dedupe identical reasons, keep highest weight per category
        score = sum(w for _, w, _ in hits)
        top_cat = max(hits, key=lambda h: h[1])[0]
        reasons = list(dict.fromkeys(r for _, _, r in hits))
        fired = [(c, w) for c, w, _ in hits]
        blocked = True if self.strict else score >= self.threshold
        return Verdict(blocked=blocked, category=top_cat, score=score,
                       reasons=reasons, fired=fired)
