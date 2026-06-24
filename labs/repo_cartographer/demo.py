"""Demo: the cartographer maps its own home — the labs/ package.

    python -m labs.repo_cartographer.demo
"""
from __future__ import annotations

import os

from .graph import CodeGraph
from .scan import scan


def main() -> int:
    target = "labs" if os.path.isdir("labs") else os.path.dirname(os.path.dirname(__file__))
    g = scan(target)
    s = g.stats()

    print(f"Mapping {target!r} — the lab maps itself:\n")
    print(f"  {s['modules']} modules · {s['internal_edges']} edges · {s['classes']} classes "
          f"· {s['functions']} functions · {s['loc']} LOC · {s['cycles']} cycles\n")

    print("Most depended-on modules (the load-bearing ones):")
    for name, fin in g.central(6):
        print(f"  {fin:>2} ← {name}")

    print("\nBlast radius if you change the shared kernel text utils:")
    impacted = g.impact_of("labs._kernel.text")
    print(f"  {len(impacted)} modules would be affected.")

    print("\nMVP packages and what each leans on:")
    for pkg in ("agent_swarm", "agent_memory", "jailbreak_gauntlet",
                "prompt_evolver", "tiny_town", "agent_os"):
        name = f"labs.{pkg}"
        deps = {d for d in g.dependencies_of(f"{name}.{_engine_of(g, name)}")
                if d.startswith("labs._kernel") or "agent_memory" in d}
        print(f"  {pkg:<20} reuses: {', '.join(sorted(deps)) or '(self-contained)'}")

    print("\nImport cycles:", g.cycles() or "none 🎉")
    return 0


def _engine_of(g: CodeGraph, pkg: str) -> str:
    """Pick a representative core module of a package for the dep readout."""
    for cand in ("engine", "memory", "guard", "evolve", "sim", "kernel"):
        if f"{pkg}.{cand}" in g.modules:
            return cand
    return "__init__"


if __name__ == "__main__":
    raise SystemExit(main())
