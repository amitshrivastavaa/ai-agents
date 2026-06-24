"""The critique → revise loop that turns a constitution into cleaner text."""
from __future__ import annotations

from dataclasses import dataclass, field

from .constitution import Principle, get_constitution


@dataclass
class Violation:
    principle_id: str
    description: str
    note: str
    severity: int


@dataclass
class Round:
    draft: str
    violations: list[Violation]


@dataclass
class Transcript:
    original: str
    rounds: list[Round]
    final: str
    final_violations: list[Violation]
    constitution: str

    @property
    def converged(self) -> bool:
        return not self.final_violations

    @property
    def num_rounds(self) -> int:
        return len(self.rounds)

    def to_dict(self) -> dict:
        return {
            "constitution": self.constitution,
            "original": self.original,
            "final": self.final,
            "rounds": self.num_rounds,
            "converged": self.converged,
            "initial_violations": len(self.rounds[0].violations) if self.rounds else 0,
            "final_violations": len(self.final_violations),
        }

    def markdown(self) -> str:
        L = [f"# Constitutional self-refine  ·  constitution: `{self.constitution}`", ""]
        L.append(f"**Original:** {self.original}")
        L.append("")
        for i, rnd in enumerate(self.rounds, 1):
            L.append(f"## Round {i} — critique ({len(rnd.violations)} issue(s))")
            if rnd.violations:
                for v in rnd.violations:
                    L.append(f"- ⚠️ _{v.principle_id}_ (sev {v.severity}): {v.note}")
            else:
                L.append("- ✅ no violations")
            L.append("")
        L.append(f"**Final:** {self.final}")
        L.append("")
        status = "✅ clean — all principles satisfied" if self.converged else \
            f"⚠️ {len(self.final_violations)} violation(s) remain after {self.num_rounds} rounds"
        L.append(f"_{status}_")
        return "\n".join(L)


def critique(text: str, constitution: list[Principle]) -> list[Violation]:
    out: list[Violation] = []
    for p in constitution:
        for note in p.detect(text):
            out.append(Violation(p.id, p.description, note, p.severity))
    out.sort(key=lambda v: -v.severity)
    return out


def revise(text: str, constitution: list[Principle],
           violated_ids: set[str] | None = None) -> str:
    for p in constitution:
        if violated_ids is None or p.id in violated_ids:
            if p.detect(text):  # only touch text the principle actually flags
                text = p.revise(text)
    return text


def refine(text: str, constitution: list[Principle] | str = "professional", *,
           max_rounds: int = 5, brain=None) -> Transcript:
    name = constitution if isinstance(constitution, str) else "custom"
    rules = get_constitution(constitution) if isinstance(constitution, str) else constitution

    rounds: list[Round] = []
    draft = text
    for _ in range(max_rounds):
        violations = critique(draft, rules)
        rounds.append(Round(draft, violations))
        if not violations:
            break
        violated = {v.principle_id for v in violations}
        draft = revise(draft, rules, violated)

    final_violations = critique(draft, rules)
    return Transcript(original=text, rounds=rounds, final=draft,
                      final_violations=final_violations, constitution=name)
