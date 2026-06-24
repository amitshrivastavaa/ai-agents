"""A small gridworld MDP.

Map legend: ``S`` start · ``G`` goal · ``#`` wall · ``X`` pit/cliff · ``.`` floor.
Every step costs ``-1``; reaching the goal pays ``+10`` and ends the episode;
falling in a pit pays ``-100`` and ends it. Walls are impassable (a bump keeps
you in place, still paying the step cost).
"""
from __future__ import annotations

from dataclasses import dataclass

ACTIONS = ("up", "down", "left", "right")
_DELTA = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

STEP_COST = -1.0
GOAL_REWARD = 10.0
PIT_REWARD = -100.0


@dataclass
class GridWorld:
    width: int
    height: int
    start: tuple[int, int]
    goal: tuple[int, int]
    walls: frozenset
    pits: frozenset

    @classmethod
    def parse(cls, text: str) -> "GridWorld":
        rows = [r for r in text.strip("\n").splitlines()]
        walls, pits = set(), set()
        start = goal = None
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == "#":
                    walls.add((x, y))
                elif ch == "X":
                    pits.add((x, y))
                elif ch == "S":
                    start = (x, y)
                elif ch == "G":
                    goal = (x, y)
        return cls(max(len(r) for r in rows), len(rows), start, goal,
                   frozenset(walls), frozenset(pits))

    def states(self):
        return [(x, y) for y in range(self.height) for x in range(self.width)
                if (x, y) not in self.walls]

    def is_terminal(self, s) -> bool:
        return s == self.goal or s in self.pits

    def step(self, s, action: str):
        """Return (next_state, reward, done)."""
        dx, dy = _DELTA[action]
        nxt = (s[0] + dx, s[1] + dy)
        if not (0 <= nxt[0] < self.width and 0 <= nxt[1] < self.height) or nxt in self.walls:
            nxt = s                       # bumped a wall: stay put
        if nxt in self.pits:
            return nxt, PIT_REWARD, True
        if nxt == self.goal:
            return nxt, GOAL_REWARD, True
        return nxt, STEP_COST, False


_MAPS_RAW = {
    # the classic cliff-walking task: a row of pits between start and goal
    "cliff": """
........
........
........
SXXXXXXG
""",
    # a maze with walls and one pit to avoid
    "maze": """
S.....
.####.
.#..#.
.#.X#.
.#..#.
....#G
""",
    # two rooms joined by a doorway
    "rooms": """
S....#....
.....#....
.....#....
..........
.....#....
.....#...G
.....#....
""",
}

MAPS = {name: GridWorld.parse(text) for name, text in _MAPS_RAW.items()}


def get_map(name: str) -> GridWorld:
    try:
        return MAPS[name]
    except KeyError:
        raise KeyError(f"unknown map {name!r}; choose from {sorted(MAPS)}") from None
