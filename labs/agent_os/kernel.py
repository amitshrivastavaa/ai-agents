"""The kernel: task graph, blackboard, and the scheduling loop.

The scheduler runs in steps. On each step it finds every *runnable* task (all
dependencies satisfied), takes up to ``max_workers`` of them by priority, and
dispatches each to its registered handler — modelling parallel workers. Handlers
read/write the blackboard and may spawn new tasks, so the graph grows at
runtime. Failures cancel everything downstream; a step budget guarantees the
loop terminates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from .._kernel import rng


class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    id: str
    kind: str
    goal: str = ""
    priority: int = 0
    deps: frozenset[str] = frozenset()
    payload: dict = field(default_factory=dict)
    max_attempts: int = 1
    # runtime state
    state: TaskState = TaskState.PENDING
    attempts: int = 0
    result: Any = None


@dataclass
class Outcome:
    ok: bool = True
    retry: bool = False
    detail: str = ""


@dataclass
class TraceEvent:
    step: int
    task_id: str
    kind: str
    action: str       # start | done | retry | fail | spawn | cancel
    detail: str = ""


class Blackboard:
    """A shared key/value store agents post results into and read from."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self.write_log: list[str] = []

    def write(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.write_log.append(key)

    def read(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def match(self, prefix: str) -> dict[str, Any]:
        return {k: v for k, v in self._data.items() if k.startswith(prefix)}

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)


class Context:
    """What a handler is given: its task, the blackboard, spawn + log."""

    def __init__(self, task: Task, kernel: "Kernel") -> None:
        self.task = task
        self.bb = kernel.blackboard
        self._kernel = kernel

    def write(self, key: str, value: Any) -> None:
        self.bb.write(key, value)

    def read(self, key: str, default: Any = None) -> Any:
        return self.bb.read(key, default)

    def spawn(self, task: Task) -> str:
        self._kernel.add(task)
        self._kernel._trace(self.task.id, self.task.kind, "spawn", task.id)
        return task.id

    @property
    def rng(self):
        return rng(self._kernel.seed, self.task.id, self.task.attempts)


Handler = Callable[[Context], Outcome]


@dataclass
class RunReport:
    steps: int
    timed_out: bool
    tasks: dict[str, Task]
    trace: list[TraceEvent]
    blackboard: dict[str, Any]
    schedule: list[list[str]]  # task ids dispatched per step (concurrency view)

    def counts(self) -> dict[str, int]:
        out = {s.value: 0 for s in TaskState}
        for t in self.tasks.values():
            out[t.state.value] += 1
        return out

    @property
    def succeeded(self) -> bool:
        return not self.timed_out and all(
            t.state == TaskState.DONE for t in self.tasks.values()
        )

    def to_dict(self) -> dict:
        return {
            "steps": self.steps,
            "succeeded": self.succeeded,
            "timed_out": self.timed_out,
            "counts": self.counts(),
            "schedule": self.schedule,
            "blackboard_keys": sorted(self.blackboard),
        }


class Kernel:
    def __init__(self, *, max_workers: int = 3, max_steps: int = 200, seed: str = "os") -> None:
        self.max_workers = max_workers
        self.max_steps = max_steps
        self.seed = seed
        self.tasks: dict[str, Task] = {}
        self.handlers: dict[str, Handler] = {}
        self.blackboard = Blackboard()
        self.trace: list[TraceEvent] = []
        self.schedule: list[list[str]] = []
        self._step = 0

    # -- setup --
    def register(self, kind: str, handler: Handler) -> None:
        self.handlers[kind] = handler

    def add(self, task: Task) -> str:
        if task.id in self.tasks:
            raise ValueError(f"duplicate task id: {task.id}")
        self.tasks[task.id] = task
        return task.id

    def _trace(self, task_id: str, kind: str, action: str, detail: str = "") -> None:
        self.trace.append(TraceEvent(self._step, task_id, kind, action, detail))

    # -- scheduling --
    def _runnable(self) -> list[Task]:
        out = []
        for t in self.tasks.values():
            if t.state != TaskState.PENDING:
                continue
            deps = [self.tasks.get(d) for d in t.deps]
            if all(d is not None and d.state == TaskState.DONE for d in deps):
                out.append(t)
        # highest priority first, then stable by id
        return sorted(out, key=lambda t: (-t.priority, t.id))

    def _dispatch(self, task: Task) -> None:
        task.attempts += 1
        task.state = TaskState.RUNNING
        self._trace(task.id, task.kind, "start", f"attempt {task.attempts}")
        handler = self.handlers.get(task.kind)
        if handler is None:
            task.state = TaskState.FAILED
            self._trace(task.id, task.kind, "fail", "no handler registered")
            return
        try:
            outcome = handler(Context(task, self))
        except Exception as exc:  # a crashing agent shouldn't take down the OS
            outcome = Outcome(ok=False, detail=f"{type(exc).__name__}: {exc}")
        if outcome.ok:
            task.state = TaskState.DONE
            self._trace(task.id, task.kind, "done", outcome.detail)
        elif outcome.retry and task.attempts < task.max_attempts:
            task.state = TaskState.PENDING
            self._trace(task.id, task.kind, "retry", outcome.detail)
        else:
            task.state = TaskState.FAILED
            self._trace(task.id, task.kind, "fail", outcome.detail)

    def _cancel_downstream(self) -> None:
        """Propagate cancellation to tasks blocked by failed/cancelled deps."""
        changed = True
        while changed:
            changed = False
            for t in self.tasks.values():
                if t.state != TaskState.PENDING:
                    continue
                blocked = any(
                    (self.tasks.get(d) is None) or
                    self.tasks[d].state in (TaskState.FAILED, TaskState.CANCELLED)
                    for d in t.deps
                )
                if blocked:
                    t.state = TaskState.CANCELLED
                    self._trace(t.id, t.kind, "cancel", "blocked by failed dependency")
                    changed = True

    def run(self) -> RunReport:
        timed_out = False
        while True:
            self._cancel_downstream()
            runnable = self._runnable()
            if not runnable:
                break
            if self._step >= self.max_steps:
                timed_out = True
                break
            self._step += 1
            batch = runnable[: self.max_workers]
            self.schedule.append([t.id for t in batch])
            for task in batch:
                self._dispatch(task)
        self._cancel_downstream()
        # anything still pending after the loop is deadlocked (dependency cycle)
        for t in self.tasks.values():
            if t.state == TaskState.PENDING and not timed_out:
                t.state = TaskState.CANCELLED
                self._trace(t.id, t.kind, "cancel", "deadlocked (dependency cycle)")
        return RunReport(
            steps=self._step, timed_out=timed_out, tasks=self.tasks,
            trace=self.trace, blackboard=self.blackboard.snapshot(),
            schedule=self.schedule,
        )
