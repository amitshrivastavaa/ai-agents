# agent_os — a micro operating system for agents

> A tiny but real runtime for multi-agent work: a dependency-aware, priority
> **scheduler** dispatches tasks to **agents** with configurable parallelism;
> agents coordinate through a shared **blackboard**, **spawn** sub-tasks at
> runtime, and **retry** or **fail** — with failures cancelling everything
> downstream. A step budget guarantees it terminates.

Inspired by agent-runtime platforms (AutoGPT & friends). Fully offline — the
example agents are deterministic, so you can watch a goal get planned, fanned
out, synthesized, and written purely from the scheduler.

## Quick start

```sh
python -m labs.agent_os.demo                                   # all three workloads
python -m labs.agent_os.cli run --workload report --goal "Will agents replace SaaS?"
python -m labs.agent_os.cli run --workload ci --trace          # see the retry
python -m labs.agent_os.cli run --workload ci_broken           # see the cancel cascade
python -m labs.agent_os.cli list
```

## What the kernel does

On each **step** the scheduler finds every *runnable* task (all dependencies
`done`), takes up to `max_workers` of them **by priority**, and dispatches each
to its registered handler. Same-step tasks ran concurrently — so the schedule
doubles as a parallelism view:

```
  │ step  1: plan
  ║ step  2: research:0, research:1, research:2     ← 3 workers in parallel
  │ step  3: research:3
  │ step  4: synthesize
  │ step  5: write
```

Agents get a `Context` with:

- **blackboard** — `ctx.write(k, v)` / `ctx.read(k)` / `ctx.bb.match(prefix)`:
  the shared memory agents pass results through.
- **spawn** — `ctx.spawn(Task(...))`: add new tasks at runtime (dynamic
  decomposition); the planner uses this to fan out research and wire up the
  `synthesize`→`write` dependencies.
- **rng** — a deterministic, per-task RNG.

A handler returns an `Outcome`: success, `retry=True` (re-queued until
`max_attempts`), or failure. **Failure cancels every task transitively
depending on it**, and dependency **cycles are detected and cancelled** rather
than hanging.

## The example workloads

| Workload | Shows off |
| --- | --- |
| `report` | runtime task-graph growth: plan → **fan-out** 4 research agents → synthesize → write a real report artifact onto the blackboard |
| `ci` | **retry**: `checkout → build → test (flaky, passes on 2nd try) → deploy`, with `deploy` gated on `test` going green |
| `ci_broken` | **cancellation cascade**: the build fails, so `test` and `deploy` are cancelled, not run |

## Build your own

Register handlers for your task `kind`s and seed the kernel:

```python
from labs.agent_os import Kernel, Task, Outcome

k = Kernel(max_workers=3)
k.register("greet", lambda ctx: ctx.write("msg", f"hi {ctx.task.payload['who']}") or Outcome())
k.add(Task("t1", "greet", payload={"who": "world"}))
report = k.run()
print(report.blackboard["msg"])
```

## Tests

```sh
python -m unittest labs.agent_os.tests.test_kernel -v
```
