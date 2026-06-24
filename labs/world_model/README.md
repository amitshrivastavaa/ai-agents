# world_model — plan by simulating before you act

> Three agents share one model of a grid world and decide what to do very
> differently: one **reacts**, one **imagines** rollouts, one **searches**. Watch
> the reflex agent walk into the lava while the planner finds the safe path.

A small, fully-offline take on the "world models + reasoning" idea: an agent
that thinks ahead by simulating consequences in an internal model instead of
acting greedily. Deterministic (rollouts are seeded).

## Quick start

```sh
python -m labs.world_model.demo                       # compare across all maps
python -m labs.world_model.cli compare                # the planner × map table
python -m labs.world_model.cli run --map lava_gap --planner lookahead --watch
python -m labs.world_model.cli run --map river --planner reactive --watch
python -m labs.world_model.cli list
```

## The three planners (reflex → sampling → search)

| Planner | How it decides | 
| --- | --- |
| `reactive` | greedy — take the move that most reduces distance to the goal, with **no lookahead**. Walks into lava the moment that's the closest-looking move. |
| `rollout` | **simulate before acting** — for each candidate move, run many imagined, lava-avoiding rollouts in the model and pick the move with the best *average* outcome (Monte-Carlo / MPC). |
| `lookahead` | **search** the model (BFS) for the optimal *safe* path and take its first step. |

## What you'll see — and the honest takeaway

```
map        reactive     lookahead    rollout
lava_gap   DIED 🔥      goal  8st    goal  8st
maze       trapped 🌀   goal 14st    trapped 🌀
river      DIED 🔥      goal 10st    trapped 🌀
open       goal  6st    goal  6st    goal  6st
```

- **Reflex fails on hazards.** Greedy distance-reduction marches straight into
  the lava (`lava_gap`, `river`).
- **Imagination clears *local* hazards.** Simulating rollouts lets `rollout`
  avoid the immediate lava and match the optimal path on `lava_gap` — strictly
  better than reacting.
- **…but sampling isn't a silver bullet.** With a myopic, distance-following
  rollout policy, `rollout` still gets **trapped** by the wall-blocked topology
  of `maze` and `river` — its rollouts rarely reach the goal, so it can't tell
  good moves from bad. This is a real, well-known limitation, shown honestly.
- **Search is reliable.** Only `lookahead` (full search over the model) reaches
  the goal optimally on every solvable map.

That spectrum — reflex, sampling, search — is the whole point: *how much you
simulate before you act* trades compute for competence.

## The world

Maps are ASCII: `#` wall · `.` floor · `S` start · `G` goal · `L` lava.
Stepping into a wall is a no-op that still costs a step; lava ends the episode
(`-100`); the goal ends it (`+100`); every step costs `-1`. Add your own map to
`env.py` and all three planners pick it up.

## Tests

```sh
python -m unittest labs.world_model.tests.test_world_model -v
```
