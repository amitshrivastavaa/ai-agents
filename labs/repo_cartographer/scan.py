"""Walk a directory, parse each module with ``ast``, and resolve its imports.

No code is executed — we only parse. Import resolution understands absolute
imports, ``import a.b.c``, and relative imports (``from ..pkg import x``),
mapping each to a *module within the scanned set* (an internal edge) or marking
it external (stdlib / third-party).
"""
from __future__ import annotations

import ast
import os

from .graph import CodeGraph, Module

_SKIP_DIRS = {"__pycache__", "node_modules", ".git", ".venv", "venv",
              ".mypy_cache", ".pytest_cache", ".tox", "build", "dist"}


def _module_name(path: str, base: str) -> tuple[str, bool]:
    rel = os.path.relpath(path, base).replace(os.sep, "/")
    parts = rel.split("/")
    parts[-1] = parts[-1][:-3]  # strip .py
    is_pkg = parts[-1] == "__init__"
    if is_pkg:
        parts = parts[:-1]
    return ".".join(parts), is_pkg


def _longest_known(dotted: str, known: set[str]) -> str | None:
    parts = dotted.split(".")
    for i in range(len(parts), 0, -1):
        cand = ".".join(parts[:i])
        if cand in known:
            return cand
    return None


def _anchor(module: Module, node: ast.ImportFrom) -> str:
    """Resolve an ImportFrom to an absolute dotted target (handles relatives)."""
    if node.level and node.level > 0:
        pkg = module.name if module.is_package else module.name.rpartition(".")[0]
        for _ in range(node.level - 1):
            pkg = pkg.rpartition(".")[0]
        if node.module:
            return f"{pkg}.{node.module}" if pkg else node.module
        return pkg
    return node.module or ""


def _add_internal(module: Module, target: str) -> None:
    if target and target != module.name:
        module.imports_internal.add(target)


def _resolve_import(dotted: str, known: set[str], module: Module) -> None:
    hit = _longest_known(dotted, known)
    if hit:
        _add_internal(module, hit)
    else:
        module.imports_external.add(dotted.split(".")[0])


def _resolve_from(target: str, names: list[str], known: set[str], module: Module) -> None:
    if not target:
        return
    base = _longest_known(target, known)
    if base:
        sub_hits = [f"{target}.{nm}" for nm in names if f"{target}.{nm}" in known]
        # `from pkg import submodule` is a dependency on the *submodule*, not the
        # re-exporting package __init__ — attributing it to __init__ invents
        # spurious cycles. Only keep the package edge when at least one imported
        # name isn't a submodule (i.e. it's a symbol defined in the __init__).
        if sub_hits and base == target and len(sub_hits) == len(names):
            for cand in sub_hits:
                _add_internal(module, cand)
        else:
            _add_internal(module, base)
            for cand in sub_hits:
                _add_internal(module, cand)
        return
    # target itself isn't internal, but `from target import submodule` might be
    added = False
    for nm in names:
        cand = f"{target}.{nm}"
        if cand in known:
            _add_internal(module, cand)
            added = True
    if not added:
        module.imports_external.add(target.split(".")[0])


def scan(root: str, *, base: str | None = None) -> CodeGraph:
    """Build a :class:`CodeGraph` for the Python package/dir at ``root``."""
    root = os.path.abspath(root)
    if base is None:
        is_pkg_root = os.path.exists(os.path.join(root, "__init__.py"))
        base = os.path.dirname(root) if is_pkg_root else root
    base = os.path.abspath(base)

    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".")]
        files += [os.path.join(dirpath, f) for f in filenames if f.endswith(".py")]

    graph = CodeGraph()
    parsed: dict[str, tuple[Module, ast.Module]] = {}
    for path in sorted(files):
        name, is_pkg = _module_name(path, base)
        if not name:
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            tree = ast.parse(src, filename=path)
        except (SyntaxError, UnicodeDecodeError):
            continue
        module = Module(
            name=name,
            path=os.path.relpath(path, base),
            is_package=is_pkg,
            classes=[n.name for n in tree.body if isinstance(n, ast.ClassDef)],
            functions=[n.name for n in tree.body
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))],
            loc=src.count("\n") + 1,
        )
        graph.add(module)
        parsed[name] = (module, tree)

    known = set(graph.modules)
    for _, (module, tree) in parsed.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    _resolve_import(alias.name, known, module)
            elif isinstance(node, ast.ImportFrom):
                target = _anchor(module, node)
                _resolve_from(target, [a.name for a in node.names], known, module)
    return graph
