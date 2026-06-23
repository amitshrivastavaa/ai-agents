"""agent_os — a micro operating system for autonomous agents.

A tiny but real runtime for multi-agent work: a dependency-aware, priority
**scheduler** dispatches tasks to registered **agents** (handlers) with
configurable parallelism; agents coordinate through a shared **blackboard**, can
**spawn** sub-tasks at runtime (dynamic decomposition), and **retry** or **fail**
— with failures cancelling everything downstream. A step budget guarantees
termination.

Inspired by agent-runtime platforms (AutoGPT & friends). Fully offline: the
example agents are deterministic, so you can watch a goal get planned, fanned
out, synthesized, and written — purely from the scheduler.
"""
from .kernel import Blackboard, Context, Kernel, Outcome, Task, TaskState
from .workloads import WORKLOADS, get_workload

__all__ = [
    "Blackboard", "Context", "Kernel", "Outcome", "Task", "TaskState",
    "WORKLOADS", "get_workload",
]
