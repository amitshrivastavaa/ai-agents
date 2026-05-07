# compliance-checker

Pre-checkout regulatory guardrail. Takes a draft cart plus the tenant's
license context and produces a typed `ComplianceReport`. Wires into the
checkout pipeline as a gate: status `block` halts checkout, `warn` requires
acknowledgment, `pass` proceeds.

## Use

```sh
python -m agents.compliance_checker.agent \
    --tenant t_acme \
    --license lic_dea_acme --license lic_state_acme \
    --formulary form_acute_care \
    --cart cart.json
```

`cart.json` shape (see [`schema.py`](./schema.py) — `CartForReview`):

```json
{
  "cart_id": "cart_demo",
  "tenant_id": "t_acme",
  "lines": [
    {"sku": "SKU-OXYC-5-100", "qty": 4, "supplier_id": "sup_amerisource", "unit_price": 22.10}
  ]
}
```

The agent prints a `ComplianceReport` JSON to stdout and exits with
`0` (pass / warn) or `2` (block) so it composes naturally with shell pipelines
and CI gates.

## Rules

| Rule | Severity | Citation |
| --- | --- | --- |
| `unknown-drug` | BLOCKER | — |
| `controlled-substance-license` | BLOCKER | 21 CFR 1301.74 |
| `no-state-license` | BLOCKER | — |
| `formulary-not-approved` | WARNING | — |
| `expiry-30-days` | BLOCKER | — |
| `expiry-90-days` | WARNING | — |
| `cold-chain-required` | INFO | — |

Add new rules in `agent.py`'s system prompt and (if they need data) in
`tools.py` / `stubs.py`. The output schema is open-ended on `rule_id` — new
slugs require no schema change.

## How it works

- Claude Opus 4.7 with adaptive thinking and prompt caching on the system
  prompt.
- Tool loop driven by `lib/llm.run_tool_loop`. Tools query the drug master,
  license registry, and inventory service.
- `output_config.format` constrains the final response to the
  `ComplianceReport` JSON Schema; the agent validates with Pydantic before
  returning.
- Structured logs emit one line per tool call (`tenant_id`, `cart_id`, tool
  name, args) for audit.
