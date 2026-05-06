# ai-agents

A collection of production-grade AI agents that ship as components of a
multi-tenant pharma procurement e-commerce platform. Each agent owns one
slice of the procurement workflow — search & ordering, document
normalization, regulatory checks, spend analytics — and is independently
runnable from the CLI for development and CI use.

All agents are built on the Anthropic API (Claude Opus 4.7) with adaptive
thinking, prompt caching, and structured outputs where applicable.

## Platform context

The platform serves pharmacies, hospital systems, and distributors as
tenants. Every agent invocation carries a `TenantContext`
([`lib/tenant.py`](lib/tenant.py)) hydrated from the platform's auth/session
layer — `tenant_id`, `user_id` (for audit), the tenant's license IDs, and
the formulary they buy from. Agents never accept tenant identifiers from
model output; scoping is enforced platform-side.

## Agents

| Agent | Role in the platform |
| --- | --- |
| [`procurement_assistant`](agents/procurement_assistant/) | Conversational catalog & cart-building agent. Buyers describe what they need; the agent searches the catalog, compares supplier offers, and builds a draft cart scoped to the tenant's formulary. |
| [`po_extractor`](agents/po_extractor/) | Extracts a structured `PurchaseOrder` from any inbound PO document (PDFs, scans, photos). Drives auto-vs-review routing via a self-reported confidence score. |
| [`compliance_checker`](agents/compliance_checker/) | Pre-checkout regulatory guardrail. Validates each cart line against DEA scheduling, license coverage, formulary rules, and lot expiry. Returns a typed `ComplianceReport` with `pass` / `warn` / `block` status. |
| [`spend_analyzer`](agents/spend_analyzer/) | Monthly spend analytics per tenant. Uploads purchase history to the Anthropic code-execution sandbox, surfaces top spend, supplier concentration, anomalies, and savings recommendations with charts. |
| [`review`](agents/review/) | Internal-use code-review agent for git diffs. Used by the platform team in CI / pre-merge. |

## Layout

```
agents/<name>/   # one directory per agent (CLI entry, tools, schemas, README)
lib/             # shared building blocks reused across agents
  config.py        # env-based config (model, API key, log level)
  tenant.py        # TenantContext — multi-tenant scoping
  logging.py       # JSON structured logging
  llm.py           # cached_system() helper + run_tool_loop()
  tools.py         # shared tool definitions (read_file, sandboxed)
  repo.py          # git helpers
```

## Install

```sh
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
# Optional overrides:
export CLAUDE_MODEL=claude-opus-4-7
export LOG_LEVEL=INFO
```

## Run

From the repo root:

```sh
python -m agents.<name>.agent [args...]
```

See each agent's README for its CLI. Common flags: `--tenant <id>`, plus
agent-specific inputs.

## Conventions

- **One directory per agent.** `agent.py` is the entry point. Agent-specific
  tool definitions, schemas, and stub backends live alongside it.
- **Shared lib over duplication.** `lib/` holds the tool-loop runner, system-
  prompt cache helper, tenant context, config, and logging. New agents
  should reuse them.
- **Stubs are clearly labeled.** `stubs.py` modules ship in-memory
  placeholders that mirror the interface of the real platform service.
  Replacing each is a one-class swap.
- **Multi-tenant scoping is enforced platform-side.** Agents never read
  `tenant_id` from model output; it's bound at construction time.
- **Structured outputs where applicable.** Pydantic models in `schema.py`
  are the canonical contract; the agent uses `output_config.format` (or
  `messages.parse()`) to constrain the model.
- **Default model**: `claude-opus-4-7` with adaptive thinking and prompt
  caching on the system prompt. Model is overridable per environment via
  `CLAUDE_MODEL`.
