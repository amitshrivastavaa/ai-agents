"""The code graph: data model plus the queries that make it useful.

Pure graph algorithms over an in-memory module graph — no I/O, no parsing (that
lives in ``scan.py``), so this is trivial to unit-test with synthetic graphs.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class Module:
    name: str
    path: str
    is_package: bool = False
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    loc: int = 0
    imports_internal: set[str] = field(default_factory=set)
    imports_external: set[str] = field(default_factory=set)


class CodeGraph:
    def __init__(self) -> None:
        self.modules: dict[str, Module] = {}

    # -- construction --
    def add(self, module: Module) -> None:
        self.modules[module.name] = module

    # -- basic accessors --
    def names(self) -> list[str]:
        return sorted(self.modules)

    def out_edges(self, name: str) -> set[str]:
        m = self.modules.get(name)
        return set(m.imports_internal) if m else set()

    def in_edges(self, name: str) -> set[str]:
        return {n for n, m in self.modules.items() if name in m.imports_internal}

    def _reverse_index(self) -> dict[str, set[str]]:
        rev: dict[str, set[str]] = {n: set() for n in self.modules}
        for n, m in self.modules.items():
            for dep in m.imports_internal:
                rev.setdefault(dep, set()).add(n)
        return rev

    # -- reachability --
    def _closure(self, start: str, edge_fn) -> set[str]:
        seen: set[str] = set()
        q = deque(edge_fn(start))
        while q:
            n = q.popleft()
            if n in seen or n == start:
                continue
            seen.add(n)
            q.extend(edge_fn(n))
        return seen

    def dependencies_of(self, name: str) -> set[str]:
        """Everything ``name`` needs, transitively."""
        return self._closure(name, self.out_edges)

    def impact_of(self, name: str) -> set[str]:
        """Everything that transitively imports ``name`` — its blast radius."""
        rev = self._reverse_index()
        return self._closure(name, lambda n: rev.get(n, set()))

    # -- rankings --
    def fan_in(self) -> dict[str, int]:
        rev = self._reverse_index()
        return {n: len(rev.get(n, set())) for n in self.modules}

    def central(self, top: int | None = None) -> list[tuple[str, int]]:
        ranked = sorted(self.fan_in().items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:top] if top else ranked

    def orphans(self) -> list[str]:
        rev = self._reverse_index()
        return sorted(n for n in self.modules if not rev.get(n))

    # -- cycles (Tarjan's strongly-connected components) --
    def sccs(self) -> list[list[str]]:
        index: dict[str, int] = {}
        low: dict[str, int] = {}
        on_stack: set[str] = set()
        stack: list[str] = []
        result: list[list[str]] = []
        counter = [0]

        def strongconnect(v: str) -> None:
            # iterative Tarjan to avoid recursion limits on big repos
            work = [(v, iter(sorted(self.out_edges(v))))]
            index[v] = low[v] = counter[0]
            counter[0] += 1
            stack.append(v)
            on_stack.add(v)
            while work:
                node, it = work[-1]
                advanced = False
                for w in it:
                    if w not in self.modules:
                        continue
                    if w not in index:
                        index[w] = low[w] = counter[0]
                        counter[0] += 1
                        stack.append(w)
                        on_stack.add(w)
                        work.append((w, iter(sorted(self.out_edges(w)))))
                        advanced = True
                        break
                    if w in on_stack:
                        low[node] = min(low[node], index[w])
                if advanced:
                    continue
                work.pop()
                if work:
                    parent = work[-1][0]
                    low[parent] = min(low[parent], low[node])
                if low[node] == index[node]:
                    comp = []
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        comp.append(w)
                        if w == node:
                            break
                    result.append(sorted(comp))

        for v in sorted(self.modules):
            if v not in index:
                strongconnect(v)
        return result

    def cycles(self) -> list[list[str]]:
        """SCCs of size > 1, plus any self-import."""
        out = [c for c in self.sccs() if len(c) > 1]
        out += [[n] for n, m in self.modules.items() if n in m.imports_internal]
        return out

    # -- symbols --
    def find_symbol(self, query: str) -> list[tuple[str, str, str]]:
        q = query.lower()
        hits: list[tuple[str, str, str]] = []
        for n, m in self.modules.items():
            for c in m.classes:
                if q in c.lower():
                    hits.append((c, "class", n))
            for f in m.functions:
                if q in f.lower():
                    hits.append((f, "function", n))
        return sorted(hits)

    # -- summaries --
    def stats(self) -> dict:
        edges = sum(len(m.imports_internal) for m in self.modules.values())
        external: dict[str, int] = {}
        for m in self.modules.values():
            for ext in m.imports_external:
                top = ext.split(".")[0]
                external[top] = external.get(top, 0) + 1
        return {
            "modules": len(self.modules),
            "internal_edges": edges,
            "classes": sum(len(m.classes) for m in self.modules.values()),
            "functions": sum(len(m.functions) for m in self.modules.values()),
            "loc": sum(m.loc for m in self.modules.values()),
            "cycles": len(self.cycles()),
            "top_external": sorted(external.items(), key=lambda kv: -kv[1])[:8],
        }

    def to_mermaid(self) -> str:
        alias = {n: f"m{i}" for i, n in enumerate(self.names())}
        lines = ["flowchart LR"]
        for n in self.names():
            lines.append(f'    {alias[n]}["{n}"]')
        for n in self.names():
            for dep in sorted(self.out_edges(n)):
                if dep in alias:
                    lines.append(f"    {alias[n]} --> {alias[dep]}")
        return "\n".join(lines)
