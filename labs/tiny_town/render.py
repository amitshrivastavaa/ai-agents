"""Text rendering for the town: the live "who's where" board and summaries."""
from __future__ import annotations

from .sim import Simulation, rel_label
from .world import LOCATIONS


def board_text(day: int, phase: str, occupants: dict[str, list[str]]) -> str:
    lines = [f"— Day {day}, {phase} —"]
    for name, loc in LOCATIONS.items():
        here = occupants.get(name, [])
        who = ", ".join(here) if here else "·"
        flag = "  «meetup»" if len(here) >= 2 else ""
        lines.append(f"  {loc.glyph} {name:<8} {who}{flag}")
    return "\n".join(lines)


def chronicle_text(sim: Simulation, *, include_reflections: bool = True) -> str:
    lines = []
    last_day = None
    for ev in sim.chronicle:
        if ev.kind == "reflect" and not include_reflections:
            continue
        if ev.day != last_day:
            lines.append(f"\n=== Day {ev.day} ===")
            last_day = ev.day
        tag = "  ✦" if ev.kind == "reflect" else f"  [{ev.phase}]"
        lines.append(f"{tag} {ev.text}")
    return "\n".join(lines)


def summary_text(sim: Simulation) -> str:
    lines = ["", "════════ Town summary after "
             f"{sim.days} day(s) ════════", ""]
    for a in sim.agents:
        lines.append(f"{a.name}  ({', '.join(sorted(a.traits))})")
        lines.append(f"  was seen at: {', '.join(sorted(a.visited))}")
        rels = sorted(a.relationships.items(), key=lambda kv: kv[1], reverse=True)
        for other, score in rels:
            met = a.met_counts.get(other, 0)
            lines.append(f"  ↔ {other:<6} {rel_label(score):<16} "
                         f"(bond {score:+.2f}, met {met}×)")
        lines.append("")
    bond = sim.strongest_bond()
    if bond:
        lines.append(f"🤝 Strongest bond: {bond[0]} & {bond[1]} "
                     f"— {rel_label(bond[2])} (bond {bond[2]:+.2f})")
    return "\n".join(lines)
