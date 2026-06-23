"""Panels and personas for the deliberation engine.

A :class:`Persona` is a deliberating agent with a *lens* (how it reads the
world), a *bias* (its resting lean, for+ / against-), a *sensitivity* (how much
the topic's signal moves it — negative for contrarians who lean against the
obvious read), and *priorities* (concern keywords that flavor its arguments).

A :class:`Panel` bundles personas with a verdict scale, so the same engine can
run a trading desk, a hiring committee, an architecture board, a product
council, or an investment committee.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Persona:
    id: str
    name: str
    role: str
    lens: str
    bias: float          # resting lean in [-1, 1]
    sensitivity: float   # how strongly topic signal moves stance (sign matters)
    priorities: tuple[str, ...]
    flavor: tuple[str, ...] = ()


@dataclass(frozen=True)
class Panel:
    id: str
    title: str
    question_hint: str
    for_word: str        # e.g. "go long", "hire", "adopt"
    against_word: str    # e.g. "stay short", "pass", "hold off"
    personas: tuple[Persona, ...]
    # verdict buckets: (min_weighted_score, label), highest threshold first
    verdicts: tuple[tuple[float, str], ...]

    def verdict_for(self, score: float) -> str:
        for threshold, label in self.verdicts:
            if score >= threshold:
                return label
        return self.verdicts[-1][1]


def _five(for_label: str, lean_for: str, hold: str, lean_against: str, against: str):
    return (
        (0.45, for_label),
        (0.12, lean_for),
        (-0.12, hold),
        (-0.45, lean_against),
        (-1.01, against),
    )


TRADING = Panel(
    id="trading",
    title="Trading Desk",
    question_hint="a position to take, e.g. 'Go long NVDA into earnings?'",
    for_word="go long",
    against_word="stay short / sell",
    personas=(
        Persona("fund", "Dana", "Fundamental Analyst", "fundamentals",
                bias=0.10, sensitivity=0.65,
                priorities=("valuation", "margins", "cash flow", "moat"),
                flavor=("the multiple", "unit economics", "the balance sheet")),
        Persona("mom", "Theo", "Technical / Momentum Trader", "momentum",
                bias=0.05, sensitivity=0.85,
                priorities=("trend", "volume", "breakout", "the tape"),
                flavor=("the chart", "relative strength", "the moving average")),
        Persona("sent", "Mira", "Sentiment Analyst", "sentiment",
                bias=0.05, sensitivity=0.75,
                priorities=("positioning", "the narrative", "retail flow", "social buzz"),
                flavor=("the crowd", "headline tone", "the options skew")),
        Persona("risk", "Raj", "Risk Manager", "risk",
                bias=-0.30, sensitivity=0.45,
                priorities=("drawdown", "tail risk", "liquidity", "position sizing"),
                flavor=("the downside", "stop levels", "correlation")),
        Persona("macro", "Lena", "Macro Strategist", "macro",
                bias=0.00, sensitivity=0.35,
                priorities=("rates", "the cycle", "the dollar", "policy"),
                flavor=("the regime", "the curve", "liquidity conditions")),
        Persona("short", "Cole", "Contrarian Short-Seller", "contrarian",
                bias=-0.10, sensitivity=-0.70,
                priorities=("the bear case", "crowded longs", "what's priced in", "froth"),
                flavor=("consensus", "the pain trade", "the short interest")),
    ),
    verdicts=_five("STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"),
)

HIRING = Panel(
    id="hiring",
    title="Hiring Committee",
    question_hint="a candidate decision, e.g. 'Hire the senior backend candidate?'",
    for_word="extend an offer",
    against_word="pass",
    personas=(
        Persona("hm", "Priya", "Hiring Manager", "growth",
                bias=0.20, sensitivity=0.55,
                priorities=("the gap on the team", "ramp time", "ownership", "delivery"),
                flavor=("the role", "the team's needs", "velocity")),
        Persona("bar", "Sven", "Bar Raiser", "skeptic",
                bias=-0.25, sensitivity=0.40,
                priorities=("the bar", "depth vs. breadth", "red flags", "consistency"),
                flavor=("the signal", "evidence", "the rubric")),
        Persona("peer", "Iris", "Peer Engineer", "peer",
                bias=0.05, sensitivity=0.60,
                priorities=("collaboration", "code quality", "pairing", "curiosity"),
                flavor=("the take-home", "the design round", "how they think")),
        Persona("lead", "Marcus", "Team Lead", "ops",
                bias=0.00, sensitivity=0.50,
                priorities=("on-call readiness", "communication", "autonomy", "scope"),
                flavor=("the system-design round", "real-world judgment", "trade-offs")),
        Persona("rec", "Nora", "Recruiter", "operator",
                bias=0.25, sensitivity=0.45,
                priorities=("competing offers", "comp expectations", "timeline", "close risk"),
                flavor=("the market", "the candidate's momentum", "the pipeline")),
    ),
    verdicts=_five("STRONG HIRE", "HIRE", "NO DECISION", "LEAN NO-HIRE", "NO HIRE"),
)

ARCHITECTURE = Panel(
    id="architecture",
    title="Architecture Review Board",
    question_hint="a tech choice, e.g. 'Adopt event sourcing for the orders service?'",
    for_word="adopt",
    against_word="hold off",
    personas=(
        Persona("inno", "Ada", "Early Adopter", "innovator",
                bias=0.40, sensitivity=0.55,
                priorities=("leverage", "developer experience", "ceiling", "future-proofing"),
                flavor=("the new capability", "where the ecosystem is heading", "the upside")),
        Persona("prag", "Bjorn", "Pragmatist Staff Engineer", "pragmatist",
                bias=0.00, sensitivity=0.45,
                priorities=("complexity budget", "team familiarity", "migration cost", "reversibility"),
                flavor=("the blast radius", "the boring option", "total cost of ownership")),
        Persona("sec", "Yara", "Security Engineer", "security",
                bias=-0.20, sensitivity=0.40,
                priorities=("attack surface", "secrets handling", "supply chain", "auditability"),
                flavor=("the threat model", "least privilege", "the dependency tree")),
        Persona("sre", "Quinn", "SRE / Ops", "ops",
                bias=-0.10, sensitivity=0.50,
                priorities=("operability", "observability", "failure modes", "on-call load"),
                flavor=("the 3am page", "the runbook", "the SLO")),
        Persona("data", "Omar", "Data Architect", "data",
                bias=0.05, sensitivity=0.45,
                priorities=("consistency", "schema evolution", "throughput", "lineage"),
                flavor=("the write path", "eventual consistency", "the hot partition")),
    ),
    verdicts=(
        (0.40, "ADOPT"),
        (0.12, "TRIAL"),
        (-0.20, "ASSESS"),
        (-1.01, "HOLD"),
    ),
)

PRODUCT = Panel(
    id="product",
    title="Product Council",
    question_hint="a product bet, e.g. 'Ship the AI inbox auto-reply feature?'",
    for_word="ship it",
    against_word="kill it",
    personas=(
        Persona("pm", "Tess", "Product Manager", "growth",
                bias=0.20, sensitivity=0.60,
                priorities=("the wedge", "activation", "retention", "the roadmap")),
        Persona("des", "Kai", "Design Lead", "design",
                bias=0.05, sensitivity=0.55,
                priorities=("the core flow", "cognitive load", "trust", "delight")),
        Persona("growth", "Vee", "Growth / Data", "data",
                bias=0.10, sensitivity=0.65,
                priorities=("the funnel", "the metric that matters", "experiment power", "cannibalization")),
        Persona("eng", "Ravi", "Engineering Lead", "ops",
                bias=-0.05, sensitivity=0.45,
                priorities=("scope", "maintenance load", "edge cases", "time-to-ship")),
        Persona("supp", "Mei", "Voice of Support", "skeptic",
                bias=-0.15, sensitivity=0.50,
                priorities=("the long tail of confusion", "abuse", "refunds", "the angry ticket")),
    ),
    verdicts=_five("SHIP", "SHIP (GUARDED)", "ITERATE", "PIVOT", "KILL"),
)

VC = Panel(
    id="vc",
    title="Investment Committee",
    question_hint="a deal, e.g. 'Lead the seed round in the dev-tools startup?'",
    for_word="invest",
    against_word="pass",
    personas=(
        Persona("gp", "Sloane", "General Partner", "growth",
                bias=0.20, sensitivity=0.60,
                priorities=("the founder", "the market size", "the wedge", "the why-now")),
        Persona("lp", "Dmitri", "LP-Minded Skeptic", "skeptic",
                bias=-0.30, sensitivity=0.45,
                priorities=("the burn", "defensibility", "the cap table", "downside protection")),
        Persona("mkt", "Hana", "Market Analyst", "market",
                bias=0.00, sensitivity=0.55,
                priorities=("TAM", "incumbents", "timing", "the wedge to platform")),
        Persona("dd", "Felix", "Technical Diligence", "innovator",
                bias=0.05, sensitivity=0.50,
                priorities=("the moat", "the demo vs. the truth", "scalability", "the team's slope")),
        Persona("op", "Greta", "Operator-in-Residence", "operator",
                bias=0.05, sensitivity=0.50,
                priorities=("go-to-market", "unit economics", "hiring plan", "the next 18 months")),
    ),
    verdicts=(
        (0.35, "INVEST — LEAD"),
        (0.10, "INVEST — FOLLOW"),
        (-0.25, "DEEPER DILIGENCE"),
        (-1.01, "PASS"),
    ),
)

PANELS: dict[str, Panel] = {
    p.id: p for p in (TRADING, HIRING, ARCHITECTURE, PRODUCT, VC)
}


def get_panel(panel_id: str) -> Panel:
    try:
        return PANELS[panel_id]
    except KeyError:
        raise KeyError(
            f"unknown panel {panel_id!r}; choose from {sorted(PANELS)}"
        ) from None
