# repo_cartographer — map a Python codebase into a dependency graph

> Point it at a Python package; it parses every module with the standard-library
> `ast` (nothing is executed), resolves imports — relative ones included — into a
> module graph, and answers the questions you actually ask about code you don't
> know yet.

A pragmatic, fully-offline take on "code RAG" / repo understanding. No third-
party dependencies. It can even map its own `labs/` home.

## Quick start

```sh
python -m labs.repo_cartographer.demo                  # the lab maps itself
python -m labs.repo_cartographer.cli map               # overview of labs/
python -m labs.repo_cartographer.cli central --top 8   # most depended-on modules
python -m labs.repo_cartographer.cli impact labs._kernel.text   # blast radius
python -m labs.repo_cartographer.cli deps   labs.tiny_town.sim  # what it needs
python -m labs.repo_cartographer.cli cycles            # import cycles (Tarjan)
python -m labs.repo_cartographer.cli orphans           # what nobody imports
python -m labs.repo_cartographer.cli find Brain        # where is a symbol defined
python -m labs.repo_cartographer.cli mermaid --path labs/agent_os   # a graph
```

Point it anywhere with `--path` (defaults to `labs/`).

## The questions it answers

| Command | Question |
| --- | --- |
| `map` | How big is this, what's it made of, are there cycles, what does it depend on externally? |
| `central` | Which modules is *everything* leaning on? (fan-in ranking) |
| `impact <m>` | If I change `m`, what transitively breaks? (reverse reachability) |
| `deps <m>` | What does `m` need, directly and transitively? |
| `cycles` | Are there import cycles? (Tarjan strongly-connected components) |
| `orphans` | What does nobody import? (dead code / entry points) |
| `find <sym>` | Which module defines a class/function matching `<sym>`? |
| `mermaid` | Export the graph as a Mermaid diagram. |

## How it resolves imports

- **`import a.b.c`** → an edge to the longest known internal module/package
  prefix; otherwise tallied as an external dependency.
- **`from pkg import x`** → an edge to `pkg.x` when that's a submodule, or to
  `pkg` when `x` is a symbol it re-exports.
- **Relatives** (`from ..agent_memory import MemoryStore`) are resolved against
  the importing module's package and level.

One subtlety that matters: `from . import submodule` is attributed to the
**submodule**, not the re-exporting package `__init__` — otherwise every tidy
package with a re-exporting `__init__` would look like it has an import cycle.
Genuine module-level cycles are still caught.

## Try it on the lab

Running `map` on `labs/` reports ~54 modules with **zero cycles** and ranks
`labs._kernel` as the most depended-on module (everything leans on the shared
kernel) — and `impact labs._kernel.text` shows that touching the text utilities
ripples to ~28 modules. That's the tool earning its keep.

## Tests

```sh
python -m unittest labs.repo_cartographer.tests.test_cartographer -v
```
