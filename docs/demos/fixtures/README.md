# Demo fixtures

Sample inputs that map to the per-agent demo runbooks in the parent
directory. These are intentionally small and deterministic — they make for
quick recordings and predictable outcomes.

## Cart fixtures (compliance_checker)

| File | Outcome with `lic_dea_acme + lic_state_acme` | Outcome with `lic_dea_basic + lic_state_acme` |
| --- | --- | --- |
| `cart_block.json` | **block** (Schedule II oxycodone is covered) | **block** (controlled-substance-license — `lic_dea_basic` doesn't cover Schedule II, cited 21 CFR 1301.74) |
| `cart_warn.json` | **warn** (insulin: 60-day expiry WARNING + cold-chain INFO) | **warn** (same) |
| `cart_pass.json` | **pass** (no findings) | **pass** (no findings) |

The lead demo is `cart_block.json` with `lic_dea_basic` — that scenario is
the most visceral demonstration that the agent is doing real regulatory
work, not just summarizing.

## Spend history (spend_analyzer)

`history_sample.csv` is 30 rows of synthetic purchase history across 6
months and 5 SKUs. It contains three signals the agent should surface:

- **Price spike on Metformin from `sup_cardinal`** — went from $4.62 →
  $5.50 (+19%) starting in November. Same SKU is still available from
  `sup_mckesson` at $4.78.
- **Single-source dependency on Amoxicillin** — every Amoxicillin row is
  from `sup_mckesson`, which is a concentration-risk finding.
- **Schedule II purchases (Oxycodone)** — low-volume, controlled, present
  in the data so the agent can call out tighter governance.

If the analyzer doesn't flag these three, that's a regression — they're the
ground truth for this fixture.

## Not committed

Real vendor PDFs / scans / photos. The repo's `.gitignore` excludes
`*.pdf`, `*.png`, `*.jpg`, `*.jpeg` in this directory because those tend
to contain real PII (vendor names, addresses, DEA numbers, prices). Keep
your own samples local; if you need to ship a fixture publicly, generate
one from scratch with synthetic data.
