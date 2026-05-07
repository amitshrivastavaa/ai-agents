# Demo runbook — compliance_checker

**Goal:** show the agent **blocking** a checkout because the tenant's
license doesn't cover a Schedule II drug. This is the highest-impact
scenario — it demonstrates the agent doing real work, not just summarizing.

**Length:** ~40 seconds.

## Three scenarios to record

The fixtures in this directory cover the three outcomes:

| Fixture | Tenant | Licenses | Outcome |
| --- | --- | --- | --- |
| `cart_block.json` | `t_acme` | `lic_dea_basic` (covers III–V only) + `lic_state_acme` | **block** — Schedule II oxycodone with no covering license |
| `cart_warn.json` | `t_acme` | `lic_dea_acme` + `lic_state_acme` | **warn** — insulin (60 days to expiry) + cold-chain INFO |
| `cart_pass.json` | `t_acme` | `lic_dea_acme` + `lic_state_acme` | **pass** — metformin only (no findings) |

## Pre-record setup

```sh
export ANTHROPIC_API_KEY=sk-ant-...
export LOG_LEVEL=WARNING
clear
```

## The "block" recording (lead with this)

```sh
python -m agents.compliance_checker.agent \
    --tenant t_acme \
    --license lic_dea_basic \
    --license lic_state_acme \
    --formulary form_acute_care \
    --cart docs/demos/fixtures/cart_block.json
echo "exit code: $?"
```

What the viewer should see:

1. Agent runs the tool loop (`lookup_drug`, `check_license_coverage`,
   `check_lot_expiry`).
2. Final JSON `ComplianceReport` with `overall_status: "block"` and a
   `BLOCKER` finding citing **21 CFR 1301.74**.
3. Exit code `2` — pipeline-friendly.

## The "warn" recording (optional)

```sh
python -m agents.compliance_checker.agent \
    --tenant t_acme \
    --license lic_dea_acme \
    --license lic_state_acme \
    --formulary form_acute_care \
    --cart docs/demos/fixtures/cart_warn.json
echo "exit code: $?"
```

Shows `overall_status: "warn"` with a 90-day-window expiry WARNING and an
INFO finding for cold-chain shipping. Exit code `0` so the pipeline
proceeds with acknowledgment.

## The "pass" recording (optional)

```sh
python -m agents.compliance_checker.agent \
    --tenant t_acme \
    --license lic_dea_acme \
    --license lic_state_acme \
    --formulary form_default \
    --cart docs/demos/fixtures/cart_pass.json
```

Shows a clean pass with no findings.

## Embedding

```md
![compliance_checker demo](docs/demos/casts/compliance_checker.cast)
```
