"""CLI for the persistent memory companion.

    python -m labs.agent_memory.cli observe "I met Sara at the climbing gym"
    python -m labs.agent_memory.cli recall "who likes the outdoors?"
    python -m labs.agent_memory.cli reflect
    python -m labs.agent_memory.cli stats
    python -m labs.agent_memory.cli dump

State persists to ~/.agent_memory/store.json (override with --store PATH), so
the memory genuinely grows across invocations. Offline by default.
"""
from __future__ import annotations

import argparse
import os
import sys

from .._kernel import get_brain, mode
from .memory import MemoryStore

DEFAULT_STORE = os.path.expanduser("~/.agent_memory/store.json")


def _store(args) -> MemoryStore:
    brain = get_brain() if mode() == "online" else None
    return MemoryStore(path=args.store, brain=brain)


def _cmd_observe(args) -> int:
    s = _store(args)
    m = s.observe(" ".join(args.text), importance=args.importance)
    s.save()
    print(f"remembered #{m.id} (importance {m.importance:.0f}/10): {m.text}")
    new = s.reflect()
    if new:
        s.save()
        print(f"\n…that triggered a reflection — {len(new)} new insight(s):")
        for ins in new:
            print(f"  ✦ {ins.text}")
    return 0


def _cmd_recall(args) -> int:
    s = _store(args)
    hits = s.recall(" ".join(args.query), k=args.k, touch=True)
    if not hits:
        print("(no memories yet — try `observe` first)")
        return 0
    s.save()  # persist refreshed recency
    print(f"top {len(hits)} for: {' '.join(args.query)!r}\n")
    for rank, h in enumerate(hits, 1):
        tag = "✦" if h.memory.kind == "semantic" else "·"
        print(f"{rank}. [{h.score:4.2f}] {tag} {h.memory.text}")
        print(f"      rel {h.relevance:.2f} · imp {h.importance:.2f} · rec {h.recency:.2f}")
    return 0


def _cmd_reflect(args) -> int:
    s = _store(args)
    new = s.reflect(force=args.force)
    s.save()
    if not new:
        st = s.stats()
        print(f"nothing to reflect yet ({st['since_reflect']}/{st['reflect_threshold']} "
              "importance accrued; use --force to override).")
        return 0
    print(f"distilled {len(new)} insight(s):")
    for ins in new:
        print(f"  ✦ {ins.text}")
    return 0


def _cmd_stats(args) -> int:
    s = _store(args)
    st = s.stats()
    print(f"store: {args.store}  (mode: {mode()})")
    for key in ("total", "episodic", "semantic", "tick", "since_reflect",
                "reflect_threshold", "ready_to_reflect"):
        print(f"  {key:18} {st[key]}")
    return 0


def _cmd_dump(args) -> int:
    s = _store(args)
    for m in s.all_memories():
        tag = "✦ semantic" if m.kind == "semantic" else "· episodic"
        print(f"#{m.id:<3} {tag}  imp {m.importance:4.1f}  t{m.created_tick:<4} {m.text}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent_memory",
                                     description="A persistent memory that grows with you.")
    parser.add_argument("--store", default=DEFAULT_STORE, help="path to the memory JSON")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("observe", help="record an observation")
    p.add_argument("text", nargs="+")
    p.add_argument("--importance", type=float, default=None, help="1..10 (auto if omitted)")
    p.set_defaults(func=_cmd_observe)

    p = sub.add_parser("recall", help="retrieve relevant memories")
    p.add_argument("query", nargs="+")
    p.add_argument("-k", type=int, default=5)
    p.set_defaults(func=_cmd_recall)

    p = sub.add_parser("reflect", help="distill insights from recent memories")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=_cmd_reflect)

    p = sub.add_parser("stats", help="show memory stats")
    p.set_defaults(func=_cmd_stats)

    p = sub.add_parser("dump", help="print all memories")
    p.set_defaults(func=_cmd_dump)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
