"""Example agents and the workloads that wire them into task graphs.

Each workload is a set of handlers plus the seed task(s) to drop on the kernel.
The handlers are deterministic so the whole run reproduces — including the
parallel fan-out, the retry, and the cancellation cascade.
"""
from __future__ import annotations

from dataclasses import dataclass

from .._kernel import keywords
from .kernel import Handler, Outcome, Task

# ----------------------------------------------------------------------------
# Workload: research report (plan -> fan-out research -> synthesize -> write)
# ----------------------------------------------------------------------------
_ANGLES = ("history", "how it works", "applications", "risks")

_FACT_TEMPLATES = {
    "history": (
        "{kw} emerged from a line of earlier attempts that mostly didn't stick.",
        "The breakthrough in {kw} came once the surrounding tooling matured.",
    ),
    "how it works": (
        "At its core, {kw} works by decomposing the problem into smaller steps.",
        "{kw} leans on a feedback loop that corrects its own mistakes.",
    ),
    "applications": (
        "Teams use {kw} to automate work that used to need a human in the loop.",
        "The most durable wins for {kw} are narrow, well-scoped tasks.",
    ),
    "risks": (
        "A key risk with {kw} is over-trusting confident-but-wrong output.",
        "{kw} can fail quietly, so guardrails and evals matter more than demos.",
    ),
}


def _kw_of(goal: str) -> str:
    kws = keywords(goal, limit=3)
    return kws[0] if kws else "the topic"


def handle_plan(ctx) -> Outcome:
    goal = ctx.task.goal
    ctx.write("plan", list(_ANGLES))
    research_ids = []
    for i, angle in enumerate(_ANGLES):
        tid = f"research:{i}"
        research_ids.append(tid)
        ctx.spawn(Task(tid, "research", goal=goal, priority=5,
                       payload={"angle": angle}))
    ctx.spawn(Task("synthesize", "synthesize", goal=goal, priority=3,
                   deps=frozenset(research_ids)))
    ctx.spawn(Task("write", "write", goal=goal, priority=1,
                   deps=frozenset({"synthesize"})))
    return Outcome(ok=True, detail=f"planned {len(_ANGLES)} research threads")


def handle_research(ctx) -> Outcome:
    angle = ctx.task.payload["angle"]
    kw = _kw_of(ctx.task.goal)
    facts = [t.format(kw=kw) for t in _FACT_TEMPLATES[angle]]
    ctx.write(f"facts:{angle}", facts)
    return Outcome(ok=True, detail=f"gathered {len(facts)} facts on '{angle}'")


def handle_synthesize(ctx) -> Outcome:
    facts = ctx.bb.match("facts:")
    outline = []
    for angle in _ANGLES:  # deterministic ordering
        key = f"facts:{angle}"
        if key in facts:
            outline.append({"section": angle, "points": facts[key]})
    ctx.write("outline", outline)
    return Outcome(ok=True, detail=f"outlined {len(outline)} sections")


def handle_write(ctx) -> Outcome:
    outline = ctx.read("outline", [])
    goal = ctx.task.goal
    lines = [f"# {goal.strip().rstrip('?')}", ""]
    for sec in outline:
        lines.append(f"## {sec['section'].title()}")
        lines += [f"- {p}" for p in sec["points"]]
        lines.append("")
    ctx.write("report", "\n".join(lines).strip())
    return Outcome(ok=True, detail="wrote report")


# ----------------------------------------------------------------------------
# Workload: CI pipeline (checkout -> build -> test[flaky] -> deploy)
# ----------------------------------------------------------------------------
def handle_checkout(ctx) -> Outcome:
    ctx.write("repo", "checked out @ main")
    return Outcome(ok=True, detail="source ready")


def handle_build(ctx) -> Outcome:
    if ctx.task.payload.get("break"):
        return Outcome(ok=False, detail="compilation error (injected)")
    ctx.write("artifact", "app.bin")
    return Outcome(ok=True, detail="built app.bin")


def handle_test(ctx) -> Outcome:
    # flaky: fails the first attempt, passes on retry
    if ctx.task.attempts < 2:
        return Outcome(ok=False, retry=True, detail="flaky test failed — retrying")
    ctx.write("tests", "passed")
    return Outcome(ok=True, detail="tests green on retry")


def handle_deploy(ctx) -> Outcome:
    ctx.write("deploy", "released to prod")
    return Outcome(ok=True, detail="deployed")


_REPORT_HANDLERS: dict[str, Handler] = {
    "plan": handle_plan, "research": handle_research,
    "synthesize": handle_synthesize, "write": handle_write,
}
_CI_HANDLERS: dict[str, Handler] = {
    "checkout": handle_checkout, "build": handle_build,
    "test": handle_test, "deploy": handle_deploy,
}


@dataclass
class Workload:
    name: str
    description: str
    handlers: dict[str, Handler]
    seeds: list[Task]


def build_report(goal: str | None = None) -> Workload:
    goal = goal or "What are autonomous AI agents and where do they actually help?"
    return Workload(
        name="report",
        description="Plan → fan-out research → synthesize → write a report.",
        handlers=_REPORT_HANDLERS,
        seeds=[Task("plan", "plan", goal=goal, priority=10)],
    )


def _ci_seeds(break_build: bool = False) -> list[Task]:
    return [
        Task("checkout", "checkout", priority=10),
        Task("build", "build", priority=8, deps=frozenset({"checkout"}),
             payload={"break": break_build}),
        Task("test", "test", priority=6, deps=frozenset({"build"}), max_attempts=2),
        Task("deploy", "deploy", priority=4, deps=frozenset({"test"})),
    ]


def build_ci(goal: str | None = None) -> Workload:
    return Workload(
        name="ci",
        description="checkout → build → test (flaky, retries) → deploy.",
        handlers=_CI_HANDLERS,
        seeds=_ci_seeds(break_build=False),
    )


def build_ci_broken(goal: str | None = None) -> Workload:
    return Workload(
        name="ci_broken",
        description="Same pipeline, but the build fails — watch test & deploy cancel.",
        handlers=_CI_HANDLERS,
        seeds=_ci_seeds(break_build=True),
    )


WORKLOADS = {
    "report": build_report,
    "ci": build_ci,
    "ci_broken": build_ci_broken,
}


def get_workload(name: str, goal: str | None = None) -> Workload:
    try:
        return WORKLOADS[name](goal)
    except KeyError:
        raise KeyError(f"unknown workload {name!r}; choose from {sorted(WORKLOADS)}") from None
