"""Demo: tournament, replicator dynamics, and the two faces of co-evolution.

    python -m labs.evo_arena.demo
"""
from __future__ import annotations

from .arena import coevolve_memory1, replicator, tournament
from .cli import _spark
from .strategies import DETERMINISTIC


def main() -> int:
    print("=" * 66)
    print("1) Axelrod tournament — who wins when everyone plays everyone?\n")
    for r in tournament(rounds=100)[:5]:
        print(f"   {r['name']:<12} avg/round {r['avg_per_round']:.2f}  coop {r['coop_rate']:.0%}")
    print("   … Always-Defect finishes last.")

    print("\n" + "=" * 66)
    print("2) Replicator dynamics — a population's strategy mix evolves:\n")
    hist = replicator(generations=50, rounds=80)
    for n in DETERMINISTIC:
        traj = [g[n] for g in hist]
        print(f"   {n:<12} {_spark(traj)}  {traj[0]:.0%} → {traj[-1]:.0%}")
    print("   → Always-Defect goes extinct; reciprocity stabilizes cooperation.")

    print("\n" + "=" * 66)
    print("3) Memory-1 co-evolution from RANDOM genomes — path-dependent:\n")
    for label, seed in (("emergence", "s"), ("tragedy", "tragedy")):
        h = coevolve_memory1(generations=24, rounds=80, seed=seed)
        coop = [r["avg_coop"] for r in h]
        print(f"   seed '{seed}' ({label}):  {_spark(coop)}  "
              f"{coop[0]:.0%} → {coop[-1]:.0%}  (~{h[-1]['nearest']})")
    print("\n   Same rules, different histories: cooperation can bloom or collapse.")
    print("   Reciprocity needs a foothold — that's the whole lesson of the arena.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
