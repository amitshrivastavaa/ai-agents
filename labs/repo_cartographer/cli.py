"""CLI for the repo cartographer.

    python -m labs.repo_cartographer.cli map               # overview of labs/
    python -m labs.repo_cartographer.cli central --top 8
    python -m labs.repo_cartographer.cli impact labs._kernel.text
    python -m labs.repo_cartographer.cli deps  labs.tiny_town.sim
    python -m labs.repo_cartographer.cli cycles
    python -m labs.repo_cartographer.cli orphans
    python -m labs.repo_cartographer.cli find Brain
    python -m labs.repo_cartographer.cli mermaid --path labs/agent_os

Default target is the labs/ package; pass --path to point anywhere.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from .graph import CodeGraph
from .scan import scan


def _resolve(g: CodeGraph, query: str) -> str | None:
    if query in g.modules:
        return query
    matches = [n for n in g.modules if n.endswith("." + query) or n == query
               or n.endswith(query)]
    return matches[0] if len(matches) == 1 else (matches[0] if matches else None)


def _cmd_map(g, args) -> int:
    s = g.stats()
    print(f"# {args.path}")
    print(f"  {s['modules']} modules · {s['internal_edges']} internal import edges · "
          f"{s['classes']} classes · {s['functions']} functions · {s['loc']} LOC")
    print(f"  import cycles: {s['cycles']}")
    print(f"  top external deps: " + ", ".join(f"{k}×{v}" for k, v in s['top_external']))
    print("\n  most depended-on modules:")
    for name, fin in g.central(10):
        m = g.modules[name]
        print(f"   {fin:>2} ← {name:<34} ({len(m.classes)}c {len(m.functions)}f {m.loc}L)")
    return 0


def _cmd_central(g, args) -> int:
    for name, fin in g.central(args.top):
        bar = "█" * fin
        print(f"  {fin:>2} {bar:<12} {name}")
    return 0


def _cmd_deps(g, args) -> int:
    name = _resolve(g, args.module)
    if not name:
        print(f"no module matching {args.module!r}")
        return 1
    print(f"{name} directly imports:")
    for d in sorted(g.out_edges(name)):
        print(f"  → {d}")
    trans = g.dependencies_of(name) - g.out_edges(name)
    if trans:
        print("transitively also needs:")
        for d in sorted(trans):
            print(f"  ⤷ {d}")
    return 0


def _cmd_impact(g, args) -> int:
    name = _resolve(g, args.module)
    if not name:
        print(f"no module matching {args.module!r}")
        return 1
    impacted = g.impact_of(name)
    print(f"Changing {name} could affect {len(impacted)} module(s):")
    for d in sorted(impacted):
        direct = " (direct)" if name in g.out_edges(d) else ""
        print(f"  ⚠ {d}{direct}")
    return 0


def _cmd_cycles(g, args) -> int:
    cycles = g.cycles()
    if not cycles:
        print("✅ no import cycles found")
        return 0
    print(f"⚠️ {len(cycles)} import cycle(s):")
    for c in cycles:
        print("  ↻ " + " → ".join(c) + f" → {c[0]}")
    return 0


def _cmd_orphans(g, args) -> int:
    orphans = g.orphans()
    print(f"{len(orphans)} module(s) nobody imports "
          "(entry points like cli/demo/tests are expected here):")
    for o in orphans:
        print(f"  · {o}")
    return 0


def _cmd_find(g, args) -> int:
    hits = g.find_symbol(args.symbol)
    if not hits:
        print(f"no class/function matching {args.symbol!r}")
        return 1
    for sym, kind, module in hits:
        print(f"  {kind:<8} {sym:<24} in {module}")
    return 0


def _cmd_mermaid(g, args) -> int:
    print(g.to_mermaid())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="repo_cartographer",
        description="Map a Python codebase into a dependency graph and query it.",
    )
    default_path = "labs" if os.path.isdir("labs") else "."
    parser.add_argument("--path", default=default_path, help="dir/package to scan")
    parser.add_argument("--json", action="store_true", help="emit graph stats as JSON")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("map").set_defaults(func=_cmd_map)
    p = sub.add_parser("central"); p.add_argument("--top", type=int, default=12); p.set_defaults(func=_cmd_central)
    p = sub.add_parser("deps"); p.add_argument("module"); p.set_defaults(func=_cmd_deps)
    p = sub.add_parser("impact"); p.add_argument("module"); p.set_defaults(func=_cmd_impact)
    sub.add_parser("cycles").set_defaults(func=_cmd_cycles)
    sub.add_parser("orphans").set_defaults(func=_cmd_orphans)
    p = sub.add_parser("find"); p.add_argument("symbol"); p.set_defaults(func=_cmd_find)
    sub.add_parser("mermaid").set_defaults(func=_cmd_mermaid)

    args = parser.parse_args(argv)
    g = scan(args.path)
    if not g.modules:
        print(f"no Python modules found under {args.path!r}")
        return 1
    if args.json:
        print(json.dumps(g.stats(), indent=2, default=list))
        return 0
    return args.func(g, args)


if __name__ == "__main__":
    sys.exit(main())
