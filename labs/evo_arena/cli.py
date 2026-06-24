"""CLI for the evolutionary IPD arena.

    python -m labs.evo_arena.cli tournament
    python -m labs.evo_arena.cli replicator
    python -m labs.evo_arena.cli coevolve --seed s          # cooperation emerges
    python -m labs.evo_arena.cli coevolve --seed tragedy    # cooperation collapses
"""
from __future__ import annotations

import argparse
import sys

from .arena import coevolve_memory1, replicator, tournament
from .strategies import DETERMINISTIC

_SPARK = "▁▂▃▄▅▆▇█"


def _spark(values, lo=0.0, hi=1.0) -> str:
    span = (hi - lo) or 1.0
    return "".join(_SPARK[min(7, max(0, int((v - lo) / span * 7)))] for v in values)


def _cmd_tournament(args) -> int:
    rows = tournament(rounds=args.rounds)
    print(f"Axelrod round-robin · {args.rounds} rounds/match\n")
    print(f"  {'strategy':<12} {'avg/round':>9} {'cooperation':>12}")
    for r in rows:
        print(f"  {r['name']:<12} {r['avg_per_round']:>9.2f} {r['coop_rate']:>11.0%}")
    print("\nReciprocators (Tit-for-Tat & kin) top the table; Always-Defect sinks.")
    return 0


def _cmd_replicator(args) -> int:
    hist = replicator(generations=args.generations, rounds=args.rounds)
    names = list(DETERMINISTIC)
    print(f"Replicator dynamics · {args.generations} generations\n")
    print("  share of the population over time:")
    for n in names:
        traj = [g[n] for g in hist]
        print(f"   {n:<12} {_spark(traj)}  {traj[0]:.0%} → {traj[-1]:.0%}")
    alld = hist[-1].get("AllD", 0.0)
    print(f"\nAlways-Defect ends at {alld:.0%} — reciprocity makes cooperation "
          "evolutionarily stable.")
    return 0


def _cmd_coevolve(args) -> int:
    hist = coevolve_memory1(pop_size=args.pop, generations=args.generations,
                            rounds=args.rounds, seed=args.seed)
    coop = [h["avg_coop"] for h in hist]
    print(f"Memory-1 co-evolution · pop {args.pop} · {args.rounds} rounds · seed '{args.seed}'\n")
    print(f"  cooperation over generations:  {_spark(coop)}  {coop[0]:.0%} → {coop[-1]:.0%}")
    print(f"  final dominant strategy:       genome {hist[-1]['best_genome']} "
          f"(~{hist[-1]['nearest']})")
    verdict = ("🌱 cooperation EMERGED" if coop[-1] > 0.55 else
               "💀 cooperation COLLAPSED to defection" if coop[-1] < 0.25 else
               "⚖️ a mixed, unstable world")
    print(f"\n  {verdict}")
    print("  (try --seed s for emergence, --seed tragedy for collapse; more --rounds"
          " lengthens the shadow of the future)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="evo_arena",
        description="Iterated Prisoner's Dilemma: tournaments and evolution.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("tournament"); p.add_argument("--rounds", type=int, default=100)
    p.set_defaults(func=_cmd_tournament)

    p = sub.add_parser("replicator")
    p.add_argument("--generations", type=int, default=50)
    p.add_argument("--rounds", type=int, default=80)
    p.set_defaults(func=_cmd_replicator)

    p = sub.add_parser("coevolve")
    p.add_argument("--seed", default="s")
    p.add_argument("--pop", type=int, default=30)
    p.add_argument("--generations", type=int, default=24)
    p.add_argument("--rounds", type=int, default=80)
    p.set_defaults(func=_cmd_coevolve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
