"""The grid world: a tiny deterministic environment and its dynamics.

Map legend: ``#`` wall · ``.`` floor · ``S`` start · ``G`` goal · ``L`` lava.
Actions are the four cardinal moves. Stepping into a wall is a no-op (you stay
put and pay the step cost); lava ends the episode badly; the goal ends it well.
"""
from __future__ import annotations

from dataclasses import dataclass

ACTIONS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

STEP_COST = -1.0
LAVA_REWARD = -100.0
GOAL_REWARD = 100.0


@dataclass(frozen=True)
class GridWorld:
    width: int
    height: int
    walls: frozenset[tuple[int, int]]
    lava: frozenset[tuple[int, int]]
    start: tuple[int, int]
    goal: tuple[int, int]

    @classmethod
    def parse(cls, text: str) -> "GridWorld":
        walls, lava = set(), set()
        start = goal = None
        rows = [r for r in text.strip("\n").splitlines()]
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                cell = (x, y)
                if ch == "#":
                    walls.add(cell)
                elif ch == "L":
                    lava.add(cell)
                elif ch == "S":
                    start = cell
                elif ch == "G":
                    goal = cell
        if start is None or goal is None:
            raise ValueError("map must contain a start (S) and goal (G)")
        return cls(
            width=max(len(r) for r in rows), height=len(rows),
            walls=frozenset(walls), lava=frozenset(lava), start=start, goal=goal,
        )

    def in_bounds(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, pos: tuple[int, int]) -> bool:
        return self.in_bounds(pos) and pos not in self.walls

    def step(self, pos: tuple[int, int], action: str):
        """Return (next_pos, reward, done) for taking ``action`` at ``pos``."""
        dx, dy = ACTIONS[action]
        nxt = (pos[0] + dx, pos[1] + dy)
        if not self.passable(nxt):
            nxt = pos  # bumped a wall: stay put, still pay the step cost
        if nxt in self.lava:
            return nxt, LAVA_REWARD, True
        if nxt == self.goal:
            return nxt, GOAL_REWARD, True
        return nxt, STEP_COST, False

    def render(self, pos=None, path=None) -> str:
        path = set(path or ())
        lines = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = (x, y)
                if cell == pos:
                    row.append("@")
                elif cell == self.start:
                    row.append("S")
                elif cell == self.goal:
                    row.append("G")
                elif cell in self.walls:
                    row.append("#")
                elif cell in self.lava:
                    row.append("L")
                elif cell in path:
                    row.append("*")
                else:
                    row.append(".")
            lines.append("".join(row))
        return "\n".join(lines)


_MAPS_RAW = {
    # greedy gradient points straight into the lava; a detour exists below
    "lava_gap": """
#######
#S.L.G#
#...#.#
#.....#
#######
""",
    # a winding maze — reactive oscillates, planners solve it
    "maze": """
#########
#S..#...#
#.#.#.#.#
#.#...#.#
#.#####.#
#.....#G#
#.###.#.#
#...#...#
#########
""",
    # two rooms split by a lava river with a single safe crossing
    "river": """
#########
#S......#
#.......#
#LLLL.LL#
#.......#
#......G#
#########
""",
    # open room, no hazards — everyone should solve this
    "open": """
#######
#S....#
#.....#
#....G#
#######
""",
}

MAPS = {name: GridWorld.parse(text) for name, text in _MAPS_RAW.items()}


def get_map(name: str) -> GridWorld:
    try:
        return MAPS[name]
    except KeyError:
        raise KeyError(f"unknown map {name!r}; choose from {sorted(MAPS)}") from None
