"""The deliberation engine: rounds, persuasion, and moderator synthesis.

Offline, each persona's stance is a transparent function of its bias, its
sensitivity to the topic's *signal* (a lightweight sentiment read of the
question), and small deterministic jitter — so the same question always
produces the same debate, and you can explain every vote. When a real model is
available the same :class:`Argument` shape is filled by the LLM instead, with a
silent fallback to the offline path on any error.

Rounds:

1. **Opening** — every persona states a stance, a thesis, and supporting points.
2. **Cross-examination** — each persona critiques two others (agree / rebut).
3. **Revision** — personas update confidence (and drift slightly) under the
   weight of the critiques they received — a small model of persuasion.
4. **Vote & synthesis** — the moderator computes a weighted score, maps it to
   the panel's verdict scale, and reports confidence, consensus, and dissent.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from .._kernel import keywords, mode, pick, rng
from .personas import Panel, Persona

# --- a small sentiment lexicon so stances correlate with the actual wording ---
_POS = frozenset("""
    growth growing record strong beat beats surge upside momentum breakout demand
    expanding profitable margin moat leader winning tailwind opportunity launch
    accelerating durable proven traction undervalued cheap rerate catalyst adopt
    robust resilient scalable elegant clean fast loved delight retention
""".split())
_NEG = frozenset("""
    risk risky lawsuit decline declining miss misses weak weakening crash dump
    overvalued expensive bubble froth crowded competition saturated churn debt
    burn dilution layoffs slowdown headwind fragile brittle complex legacy outage
    breach vulnerability incident regression confusing abuse refund angry tail
""".split())


def _topic_signal(topic: str) -> float:
    """A reproducible sentiment read of the question in [-1, 1].

    Combines cue-word counts with a small seeded base so that two differently
    worded but equally neutral questions still differ slightly.
    """
    kws = keywords(topic, limit=40)
    pos = sum(1 for k in kws if k in _POS)
    neg = sum(1 for k in kws if k in _NEG)
    cue = 0.0
    if pos or neg:
        cue = (pos - neg) / (pos + neg)
    base = (rng("signal", topic.lower()).random() - 0.5) * 0.3
    return max(-1.0, min(1.0, 0.75 * cue + base))


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


# ----------------------------- data structures -------------------------------
@dataclass
class Argument:
    persona: Persona
    stance: float        # [-1, 1]
    confidence: float    # [0, 1]
    thesis: str
    points: list[str]

    @property
    def lean(self) -> str:
        if self.stance >= 0.45:
            return "strongly for"
        if self.stance >= 0.12:
            return "leans for"
        if self.stance <= -0.45:
            return "strongly against"
        if self.stance <= -0.12:
            return "leans against"
        return "on the fence"


@dataclass
class Critique:
    src: Persona
    dst: Persona
    agree: bool
    note: str


@dataclass
class Vote:
    persona: Persona
    stance: float
    confidence: float


@dataclass
class Decision:
    verdict: str
    score: float
    confidence: float
    consensus: float
    rationale: str
    key_points: list[str]
    tensions: list[str]
    votes: list[Vote]


@dataclass
class Deliberation:
    panel: Panel
    topic: str
    mode: str
    signal: float
    openings: list[Argument]
    critiques: list[Critique]
    revised: list[Argument]
    decision: Decision

    def transcript_md(self) -> str:
        return _render_markdown(self)

    def record(self) -> dict:
        d = self.decision
        return {
            "panel": self.panel.id,
            "topic": self.topic,
            "mode": self.mode,
            "verdict": d.verdict,
            "score": round(d.score, 3),
            "confidence": round(d.confidence, 3),
            "consensus": round(d.consensus, 3),
            "rationale": d.rationale,
            "key_points": d.key_points,
            "tensions": d.tensions,
            "votes": [
                {
                    "persona": v.persona.name,
                    "role": v.persona.role,
                    "stance": round(v.stance, 3),
                    "confidence": round(v.confidence, 3),
                }
                for v in d.votes
            ],
        }


# ------------------------------- templates -----------------------------------
_OPEN_FOR = (
    "On balance I'm for it — {priority} lines up and the {kw} angle is doing the work.",
    "I come down in favor. The case rests on {priority}; '{kw}' is the part that convinces me.",
    "Count me a yes. Through the lens of {priority}, the {kw} story holds together.",
    "I'd back this. {priority} is the load-bearing reason, and '{kw}' reinforces it.",
)
_OPEN_AGAINST = (
    "I'm against. {priority} is where this breaks, and '{kw}' makes it worse, not better.",
    "My read is no. Weigh {priority} honestly and the {kw} angle stops looking attractive.",
    "I'd hold off. The {kw} framing ignores {priority}, which is the thing that bites you.",
    "Count me skeptical. {priority} isn't addressed, and '{kw}' is doing a lot of hand-waving.",
)
_OPEN_NEUTRAL = (
    "I'm genuinely split. {priority} cuts one way, '{kw}' the other.",
    "Too close to call for me yet — it hinges on {priority} and how '{kw}' actually plays out.",
    "I can argue this either way; the deciding factor is {priority}, not the '{kw}' headline.",
)

_POINT_FOR = (
    "On {priority}, the asymmetry favors acting — the upside on '{kw}' outweighs what we'd give up.",
    "If {priority} holds, '{kw}' compounds in our favor over the next few moves.",
    "I keep coming back to {priority}: it's the part that's hard to replicate, and '{kw}' leans on it.",
    "The {kw} signal is corroborated when I stress-test {priority}.",
)
_POINT_AGAINST = (
    "{priority} is underwritten on hope here; '{kw}' doesn't survive a second look.",
    "Run the downside on {priority} and '{kw}' turns from a feature into a liability.",
    "We're paying full price on '{kw}' for {priority} that isn't actually proven.",
    "The failure mode around {priority} is exactly the one '{kw}' makes more likely.",
)
_POINT_NEUTRAL = (
    "I'd want one more data point on {priority} before '{kw}' moves me.",
    "There's a version of {priority} where '{kw}' is great and one where it's a trap.",
    "Whether '{kw}' matters comes down entirely to how {priority} resolves.",
)

_CRIT_AGREE = (
    "Building on {dst}: yes — and {priority} is the under-appreciated half of that.",
    "{dst} is right. From a {src_lens} seat, '{kw}' looks the same way.",
    "I'll co-sign {dst}'s read; {priority} is the second leg of the same argument.",
)
_CRIT_DISAGREE = (
    "I have to push back on {dst}: that read skips {priority}, which is where I live.",
    "Respectfully, {dst} is over-indexing on '{kw}' and under-weighting {priority}.",
    "{dst}, I don't buy it — from a {src_lens} angle the '{kw}' case is thinner than it sounds.",
    "Counter to {dst}: {priority} pulls the opposite direction once you size it properly.",
)


def _stance_bank(stance: float, for_b, against_b, neutral_b):
    if stance >= 0.12:
        return for_b
    if stance <= -0.12:
        return against_b
    return neutral_b


# --------------------------- offline reasoning -------------------------------
def _offline_argument(p: Persona, topic: str, signal: float) -> Argument:
    jitter = (rng("stance", p.id, topic.lower()).random() - 0.5) * 0.25
    stance = _clamp(p.bias + p.sensitivity * signal + jitter)
    # confidence grows with conviction (|stance|) and a per-persona temperament.
    temperament = 0.45 + 0.4 * rng("temper", p.id).random()
    confidence = _clamp(0.35 + 0.55 * abs(stance) * temperament + 0.1 * rng("c", p.id, topic).random(), 0.1, 0.98)

    kws = keywords(topic, limit=6) or ["the proposal"]
    pri = list(p.priorities)

    def fill(template: str, i: int) -> str:
        r = rng(p.id, topic.lower(), template, i)
        return template.format(
            priority=pri[r.randrange(len(pri))],
            kw=kws[r.randrange(len(kws))],
            dst="", src_lens=p.lens,
        )

    thesis = fill(pick(_stance_bank(stance, _OPEN_FOR, _OPEN_AGAINST, _OPEN_NEUTRAL),
                       p.id, topic, "thesis"), 0)
    bank = _stance_bank(stance, _POINT_FOR, _POINT_AGAINST, _POINT_NEUTRAL)
    n_points = 2 + (1 if confidence > 0.6 else 0)
    chosen, used = [], set()
    r = rng("points", p.id, topic.lower())
    while len(chosen) < n_points and len(used) < len(bank):
        idx = r.randrange(len(bank))
        if idx in used:
            continue
        used.add(idx)
        chosen.append(fill(bank[idx], idx + 1))
    return Argument(persona=p, stance=stance, confidence=confidence, thesis=thesis, points=chosen)


def _offline_critique(src_arg: Argument, dst_arg: Argument, topic: str) -> Critique:
    src, dst = src_arg.persona, dst_arg.persona
    # Agree when their *actual stances on this topic* point the same way and
    # aren't wildly far apart — not their resting bias.
    same_sign = (src_arg.stance >= 0) == (dst_arg.stance >= 0)
    close = abs(src_arg.stance - dst_arg.stance) < 0.7
    agree = same_sign and close
    kws = keywords(topic, limit=6) or ["the proposal"]
    r = rng("crit", src.id, dst.id, topic.lower())
    template = pick(_CRIT_AGREE if agree else _CRIT_DISAGREE, src.id, dst.id, topic)
    note = template.format(
        dst=dst.name,
        priority=src.priorities[r.randrange(len(src.priorities))],
        kw=kws[r.randrange(len(kws))],
        src_lens=src.lens,
    )
    return Critique(src=src, dst=dst, agree=agree, note=note)


# ------------------------------- LLM path ------------------------------------
def _llm_argument(brain, p: Persona, topic: str, panel: Panel) -> Argument:
    system = (
        f"You are {p.name}, the {p.role} on a {panel.title}. You reason through "
        f"the lens of {p.lens} and care most about: {', '.join(p.priorities)}. "
        "You are decisive but honest about uncertainty."
    )
    prompt = (
        f"The panel is deciding: {topic!r}.\n"
        f"To '{panel.for_word}' is the FOR side; to '{panel.against_word}' is the AGAINST side.\n"
        "Respond ONLY with a JSON object: "
        '{"stance": <float -1..1, negative=against>, "confidence": <float 0..1>, '
        '"thesis": <one sentence>, "points": [<two or three short sentences>]}'
    )
    data = brain.complete_json(prompt, system=system, temperature=0.6)
    return Argument(
        persona=p,
        stance=_clamp(float(data["stance"])),
        confidence=_clamp(float(data.get("confidence", 0.6)), 0.1, 0.98),
        thesis=str(data["thesis"]).strip(),
        points=[str(x).strip() for x in data.get("points", [])][:3],
    )


# ------------------------------- orchestration -------------------------------
def deliberate(panel: Panel, topic: str, *, brain=None) -> Deliberation:
    """Run the full multi-round deliberation and synthesize a decision."""
    signal = _topic_signal(topic)
    run_mode = "online" if brain is not None else mode()

    # Round 1 — opening statements.
    openings: list[Argument] = []
    for p in panel.personas:
        if brain is not None:
            try:
                openings.append(_llm_argument(brain, p, topic, panel))
                continue
            except Exception:
                pass  # fall back to offline for this persona
        openings.append(_offline_argument(p, topic, signal))

    by_id = {a.persona.id: a for a in openings}

    # Round 2 — cross-examination: each persona challenges its furthest
    # opponent and reinforces its closest ally — the two most telling exchanges.
    critiques: list[Critique] = []
    for a in openings:
        ordered = sorted(
            (o for o in openings if o.persona.id != a.persona.id),
            key=lambda o: abs(o.stance - a.stance),
            reverse=True,
        )
        targets = [ordered[0], ordered[-1]] if len(ordered) > 1 else ordered[:1]
        for target in targets:
            critiques.append(_offline_critique(a, target, topic))

    # Round 3 — revision under pressure: confidence and stance drift with the
    # net agreement each persona received.
    revised: list[Argument] = []
    for a in openings:
        received = [c for c in critiques if c.dst.id == a.persona.id]
        agrees = sum(1 for c in received if c.agree)
        rebuts = sum(1 for c in received if not c.agree)
        net = agrees - rebuts
        new_conf = _clamp(a.confidence + 0.06 * net, 0.1, 0.98)
        # A rebutted persona drifts a touch toward the room's center of mass.
        center = statistics.fmean([o.stance for o in openings])
        pull = 0.08 * rebuts * (1 if center > a.stance else -1)
        new_stance = _clamp(a.stance + pull)
        revised.append(Argument(a.persona, new_stance, new_conf, a.thesis, a.points))

    decision = _synthesize(panel, revised)
    return Deliberation(
        panel=panel, topic=topic, mode=run_mode, signal=signal,
        openings=openings, critiques=critiques, revised=revised, decision=decision,
    )


def _synthesize(panel: Panel, args: list[Argument]) -> Decision:
    stances = [a.stance for a in args]
    weights = [a.confidence for a in args]
    wsum = sum(weights) or 1.0
    score = sum(s * w for s, w in zip(stances, weights)) / wsum

    spread = statistics.pstdev(stances) if len(stances) > 1 else 0.0
    consensus = _clamp(1.0 - spread, 0.0, 1.0)
    confidence = _clamp(statistics.fmean(weights) * (0.55 + 0.45 * consensus), 0.0, 1.0)
    verdict = panel.verdict_for(score)

    sign = 1 if score >= 0 else -1
    aligned = sorted(
        (a for a in args if (a.stance >= 0) == (sign >= 0) and abs(a.stance) > 0.05),
        key=lambda a: a.confidence,
        reverse=True,
    )
    key_points: list[str] = []
    for a in aligned:
        if a.points:
            key_points.append(f"{a.persona.name} ({a.persona.role}): {a.points[0]}")
        if len(key_points) >= 4:
            break

    dissenters = sorted(
        (a for a in args if (a.stance >= 0) != (sign >= 0) and abs(a.stance) > 0.15),
        key=lambda a: abs(a.stance) * a.confidence,
        reverse=True,
    )
    tensions = [
        f"{a.persona.name} ({a.persona.role}) dissents — {a.thesis}"
        for a in dissenters[:3]
    ]

    direction = panel.for_word if score >= 0 else panel.against_word
    rationale = (
        f"Weighted across {len(args)} voices, the room {('leans toward' if abs(score) < 0.3 else 'comes down clearly on')} "
        f"'{direction}' (score {score:+.2f}). "
        + (f"Consensus is {'high' if consensus > 0.7 else 'moderate' if consensus > 0.45 else 'low'}; "
           f"{'few hold-outs' if not tensions else str(len(tensions)) + ' notable dissent(s) on record'}.")
    )

    votes = [Vote(a.persona, a.stance, a.confidence) for a in args]
    return Decision(
        verdict=verdict, score=score, confidence=confidence, consensus=consensus,
        rationale=rationale, key_points=key_points, tensions=tensions, votes=votes,
    )


# ------------------------------- rendering -----------------------------------
def _bar(stance: float, width: int = 21) -> str:
    """An ASCII opinion meter from against (left) to for (right)."""
    mid = width // 2
    pos = int(round((stance + 1) / 2 * (width - 1)))
    cells = ["·"] * width
    cells[mid] = "│"
    cells[pos] = "●"
    return "".join(cells)


def _render_markdown(d: Deliberation) -> str:
    dec = d.decision
    lines: list[str] = []
    lines.append(f"# {d.panel.title} — Deliberation")
    lines.append("")
    lines.append(f"**Question:** {d.topic}")
    lines.append("")
    lines.append(
        f"**Verdict: `{dec.verdict}`**  ·  score `{dec.score:+.2f}`  ·  "
        f"confidence `{dec.confidence:.0%}`  ·  consensus `{dec.consensus:.0%}`  ·  "
        f"_mode: {d.mode}_"
    )
    lines.append("")
    lines.append(f"> {dec.rationale}")
    lines.append("")

    lines.append("## Round 1 — Opening statements")
    lines.append("")
    for a in d.openings:
        lines.append(f"**{a.persona.name}** · _{a.persona.role}_ — {a.lean} "
                     f"`{_bar(a.stance)}`  (conf {a.confidence:.0%})")
        lines.append(f"> {a.thesis}")
        for pt in a.points:
            lines.append(f"> - {pt}")
        lines.append("")

    lines.append("## Round 2 — Cross-examination")
    lines.append("")
    for c in d.critiques:
        mark = "🤝" if c.agree else "⚔️"
        lines.append(f"- {mark} **{c.src.name}** → **{c.dst.name}**: {c.note}")
    lines.append("")

    lines.append("## Round 3 — Revised vote")
    lines.append("")
    lines.append("| Persona | Role | Stance | Confidence |")
    lines.append("| --- | --- | :---: | :---: |")
    for v in sorted(dec.votes, key=lambda v: v.stance, reverse=True):
        lines.append(f"| {v.persona.name} | {v.persona.role} | "
                     f"`{_bar(v.stance, 15)}` {v.stance:+.2f} | {v.confidence:.0%} |")
    lines.append("")

    lines.append("## Moderator synthesis")
    lines.append("")
    if dec.key_points:
        lines.append("**What carried the decision:**")
        for kp in dec.key_points:
            lines.append(f"- {kp}")
        lines.append("")
    if dec.tensions:
        lines.append("**Live dissent (don't ignore these):**")
        for t in dec.tensions:
            lines.append(f"- {t}")
        lines.append("")
    return "\n".join(lines)
