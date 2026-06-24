"""Principles: each is a rule with a detector and a deterministic fix.

A principle's ``detect`` returns a list of human-readable violation notes (empty
== compliant), and its ``revise`` returns text with those violations removed.
Keeping the two in lock-step is what lets the refine loop actually converge.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

_ACRONYMS = {"AI", "API", "ML", "LLM", "USA", "UK", "EU", "FAQ", "CEO", "CTO",
             "ID", "OK", "PR", "CI", "URL", "HTTP", "JSON", "PDF", "SQL", "GPU",
             "EMAIL", "PHONE", "SSN", "CARD"}  # PII redaction tags, not shouting


@dataclass(frozen=True)
class Principle:
    id: str
    description: str
    severity: int
    detect: Callable[[str], list[str]]
    revise: Callable[[str], str]


def _tidy(text: str) -> str:
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text.strip()


def _word_map_principle(pid: str, desc: str, severity: int,
                        mapping: dict[str, str]) -> Principle:
    patterns = {w: re.compile(rf"\b{re.escape(w)}\b", re.IGNORECASE) for w in mapping}

    def detect(text: str) -> list[str]:
        notes = []
        for w, pat in patterns.items():
            if pat.search(text):
                notes.append(f"'{w}' → '{mapping[w]}'")
        return notes

    def revise(text: str) -> str:
        for w, pat in patterns.items():
            text = pat.sub(mapping[w], text)
        return _tidy(text)

    return Principle(pid, desc, severity, detect, revise)


# --- shouting ---------------------------------------------------------------
_CAPS = re.compile(r"\b[A-Z]{3,}\b")


def _detect_shout(text: str) -> list[str]:
    bad = [w for w in _CAPS.findall(text) if w not in _ACRONYMS]
    return [f"shouting: {w!r}" for w in bad]


def _revise_shout(text: str) -> str:
    return _CAPS.sub(lambda m: m.group() if m.group() in _ACRONYMS else m.group().lower(), text)


NO_SHOUTING = Principle("no_shouting", "Don't shout in all-caps.", 2,
                        _detect_shout, _revise_shout)

# --- exclamation spam -------------------------------------------------------
_EXCL = re.compile(r"([!?]){2,}")
NO_EXCLAIM = Principle(
    "no_exclaim", "Avoid runs of exclamation/question marks.", 1,
    lambda t: [f"punctuation spam: {m.group()!r}" for m in _EXCL.finditer(t)],
    lambda t: _tidy(_EXCL.sub(r"\1", t)),
)

# --- filler / wordiness -----------------------------------------------------
_FILLER = ["just", "very", "really", "actually", "basically", "literally",
           "simply", "totally", "honestly", "sort of", "kind of"]
_FILLER_PAT = re.compile(r"\b(" + "|".join(_FILLER) + r")\b", re.IGNORECASE)
NO_FILLER = Principle(
    "no_filler", "Cut filler / hedging words; be concise.", 1,
    lambda t: sorted({f"filler: {m.group().lower()!r}" for m in _FILLER_PAT.finditer(t)}),
    lambda t: _tidy(_FILLER_PAT.sub("", t)),
)

# --- word-map principles ----------------------------------------------------
NO_INSULTS = _word_map_principle(
    "no_insults", "Be respectful — no insults.", 4,
    {"stupid": "unwise", "idiot": "amateur", "idiots": "amateurs", "dumb": "unclear",
     "moron": "amateur", "morons": "amateurs", "useless": "unhelpful",
     "sucks": "is lacking", "crap": "poor", "trash": "weak"},
)

INCLUSIVE = _word_map_principle(
    "inclusive", "Prefer inclusive, neutral language.", 2,
    {"guys": "everyone", "blacklist": "blocklist", "whitelist": "allowlist",
     "manpower": "workforce", "mankind": "humankind", "sanity check": "quick check"},
)

NO_OVERCLAIM = _word_map_principle(
    "no_overclaim", "Don't overclaim or state absolutes.", 3,
    {"guaranteed": "likely", "always": "usually", "never": "rarely",
     "obviously": "arguably", "definitely": "probably", "impossible": "hard"},
)

# --- PII redaction ----------------------------------------------------------
_PII = [
    (re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"), "[CARD]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    (re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"), "[PHONE]"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[EMAIL]"),
]


def _detect_pii(text: str) -> list[str]:
    notes = []
    for pat, tag in _PII:
        for m in pat.finditer(text):
            notes.append(f"PII {tag}: {m.group()!r}")
    return notes


def _revise_pii(text: str) -> str:
    for pat, tag in _PII:
        text = pat.sub(tag, text)
    return text


REDACT_PII = Principle("redact_pii", "Redact personal data (email, phone, SSN, card).",
                       5, _detect_pii, _revise_pii)


ALL_PRINCIPLES = [NO_SHOUTING, NO_EXCLAIM, NO_FILLER, NO_INSULTS,
                  INCLUSIVE, NO_OVERCLAIM, REDACT_PII]

PRESETS: dict[str, list[Principle]] = {
    "professional": [NO_SHOUTING, NO_EXCLAIM, NO_FILLER, NO_INSULTS, INCLUSIVE, NO_OVERCLAIM],
    "safety": [NO_INSULTS, REDACT_PII, NO_OVERCLAIM],
    "all": ALL_PRINCIPLES,
}


def get_constitution(name: str) -> list[Principle]:
    try:
        return PRESETS[name]
    except KeyError:
        raise KeyError(f"unknown constitution {name!r}; choose from {sorted(PRESETS)}") from None
