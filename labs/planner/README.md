# planner — a classical STRIPS planner (it solves the Sussman anomaly)

> The other half of AI from the from-scratch ML in this lab: **symbolic,
> goal-directed planning**. A world is a set of true facts; an action has
> preconditions and add/delete effects; a plan is a sequence of actions that
> turns the start state into one satisfying the goal. The planner finds it by
> searching — and solves the famous **Sussman anomaly** that trips up naive
> goal-by-goal planners.

Fully offline, deterministic; renders the block towers and the plan in ASCII.

## Quick start

```sh
python -m labs.planner.demo
python -m labs.planner.cli solve --problem sussman --trace
python -m labs.planner.cli solve --problem reverse --astar
python -m labs.planner.cli list
```

```
start:               goal: A on B, B on C       optimal plan (6 actions):
[C]                                                1. unstack(C,A)
[A] [B]                                            2. putdown(C)        [A]
─── ───                                            3. pickup(B)         [B]
hand: empty                                        4. stack(B,C)        [C]
                                                   5. pickup(A)         ───
                                                   6. stack(A,B)
```

## STRIPS, from scratch

- A **fact** is a tuple like `("on", "A", "B")`; a **state** is a frozenset of
  facts (`strips.py`).
- An **action** is `(preconditions, add-effects, delete-effects)`. It's
  *applicable* when its preconditions hold; applying it removes the deletes and
  adds the adds. Blocks world grounds four operators — `pickup`, `putdown`,
  `stack`, `unstack` — over the blocks (`blocksworld.py`).
- A **plan** is found by state-space search (`search.py`): **breadth-first** for
  a guaranteed shortest plan, or **A\*** with the goal-count heuristic
  `h(s) = |goal − s|` for speed. Both return optimal plans on these problems.

## The Sussman anomaly

Start: `C` on `A`, with `A` and `B` on the table. Goal: `A on B` **and** `B on
C`. A planner that achieves one subgoal then the other keeps undoing its own
work — the subgoals interfere. A complete search doesn't care: it finds the
6-action plan `unstack(C,A) → putdown(C) → pickup(B) → stack(B,C) → pickup(A) →
stack(A,B)`. Run with `--trace` to watch the towers rearrange step by step.

This is classical AI (GOFAI): no learning, no probabilities — just facts,
actions, and search over their consequences.

## Tests

```sh
python -m unittest labs.planner.tests.test_planner -v
```
