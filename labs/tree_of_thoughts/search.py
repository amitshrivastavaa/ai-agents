"""Three ways to search the Game-of-24 thought space, and a comparison harness.

``tot_search`` is the star: a beam search over partial states where each
candidate "thought" is scored by a *Monte-Carlo value* (sampled look-ahead) and
only the most promising are kept — the test-time-compute idea made concrete.
"""
from __future__ import annotations

from dataclasses import dataclass

from .._kernel import rng
from .game24 import Step, exact_solve, expand, is_goal, to_state


@dataclass
class SearchResult:
    method: str
    solved: bool
    path: list[Step]
    nodes: int          # states examined (a proxy for work done)


# ----------------------------- value function --------------------------------
def mc_value(state, samples: int, r) -> float:
    """Estimate a state's promise by random play-outs that hit 24 (ToT's value)."""
    if is_goal(state):
        return 1.0
    if len(state) == 1:
        return 0.0
    hits = 0
    for _ in range(samples):
        cur = state
        while len(cur) > 1:
            children = [c for c, _ in expand(cur)]
            cur = children[r.randrange(len(children))]
        if cur[0] == 24:
            hits += 1
    return hits / samples


# ----------------------------- the searchers ---------------------------------
def tot_search(numbers, *, beam_width: int = 12, samples: int = 16,
               seed: str = "tot") -> SearchResult:
    start = to_state(numbers)
    r = rng(seed, start)
    beam = [(start, [])]
    nodes = 0
    depth = 0
    while beam:
        candidates: list[tuple] = []
        for state, path in beam:
            for child, step in expand(state):
                nodes += 1
                new_path = path + [step]
                if is_goal(child):
                    return SearchResult("tree_of_thoughts", True, new_path, nodes)
                if len(child) > 1:
                    candidates.append((child, new_path))
        if not candidates:
            break
        # keep only the most promising thoughts — this is the deliberation
        candidates.sort(key=lambda cp: mc_value(cp[0], samples, r), reverse=True)
        beam = candidates[:beam_width]
        depth += 1
        if depth > len(start):
            break
    return SearchResult("tree_of_thoughts", False, [], nodes)


def random_search(numbers, *, tries: int = 200, seed: str = "rand") -> SearchResult:
    start = to_state(numbers)
    r = rng(seed, start)
    nodes = 0
    for _ in range(tries):
        cur, path = start, []
        while len(cur) > 1:
            children = list(expand(cur))
            nodes += 1
            cur, step = children[r.randrange(len(children))]
            path.append(step)
        if is_goal(cur):
            return SearchResult("random", True, path, nodes)
    return SearchResult("random", False, [], nodes)


def brute_force(numbers) -> SearchResult:
    counter = {"n": 0}
    start = to_state(numbers)

    def dfs(state, path):
        if is_goal(state):
            return path
        if len(state) == 1:
            return None
        for child, step in expand(state):
            counter["n"] += 1
            got = dfs(child, path + [step])
            if got is not None:
                return got
        return None

    path = dfs(start, [])
    return SearchResult("brute_force", path is not None, path or [], counter["n"])


# ------------------------------- comparison ----------------------------------
PUZZLES = [
    (4, 6, 8, 2),
    (1, 2, 3, 4),
    (3, 3, 8, 8),     # the famously hard one: 8 / (3 - 8/3) = 24
    (4, 7, 8, 8),
    (5, 5, 5, 1),     # 5 * (5 - 1/5) = 24
    (2, 3, 5, 12),    # 12 / (3 - 5/2) = 24
    (1, 5, 5, 5),
    (4, 4, 10, 1),
    (1, 1, 1, 1),     # genuinely unsolvable
    (11, 11, 11, 11), # genuinely unsolvable
]


def compare(puzzles=None, *, beam_width: int = 12, samples: int = 16,
            tries: int = 200) -> dict:
    puzzles = puzzles or PUZZLES
    methods = {"random": [], "tree_of_thoughts": [], "brute_force": []}
    truth = []
    for p in puzzles:
        solvable = exact_solve(p) is not None
        truth.append(solvable)
        methods["random"].append(random_search(p, tries=tries))
        methods["tree_of_thoughts"].append(tot_search(p, beam_width=beam_width, samples=samples))
        methods["brute_force"].append(brute_force(p))
    out = {"n": len(puzzles), "solvable": sum(truth)}
    for m, results in methods.items():
        # only count "solved" on puzzles that are actually solvable
        solved = sum(1 for r, t in zip(results, truth) if t and r.solved)
        out[m] = {
            "solved": solved,
            "avg_nodes": round(sum(r.nodes for r in results) / len(results), 1),
        }
    return out
