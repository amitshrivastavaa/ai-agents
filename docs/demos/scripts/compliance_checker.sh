#!/usr/bin/env bash
# Demo: compliance_checker — the hero clip.
#
# Three scenarios in one cast: pass, warn, block. The block scenario uses a
# tenant whose DEA license only covers Schedules III–V trying to buy a
# Schedule II drug, so the agent cites 21 CFR 1301.74 and the script exits
# non-zero — pipeline-friendly.
#
# Record with:
#     asciinema rec docs/demos/casts/compliance_checker.cast \
#         -c "bash docs/demos/scripts/compliance_checker.sh"

source "$(dirname "$0")/_demo.sh"
require_env
require_repo_root

clear

# We don't want `set -e` to abort the demo when the BLOCK scenario exits
# non-zero — that's the *point* of that scenario.
set +e

header "compliance_checker — pre-checkout regulatory gate"

header "1/3 — pass: clean cart, full licenses"
step "Metformin + Lisinopril, formulary-approved, full license set. Expect overall_status=pass and exit code 0." \
    "python -m agents.compliance_checker.agent --tenant t_acme --license lic_dea_acme --license lic_state_acme --formulary form_default --cart docs/demos/fixtures/cart_pass.json; echo \"exit=\$?\""

sleep 1

header "2/3 — warn: short-dated cold-chain item"
step "Insulin glargine: 60 days to expiry triggers expiry-90-days WARNING; cold-chain shipping is an INFO. Exit code 0 — checkout proceeds with acknowledgment." \
    "python -m agents.compliance_checker.agent --tenant t_acme --license lic_dea_acme --license lic_state_acme --formulary form_acute_care --cart docs/demos/fixtures/cart_warn.json; echo \"exit=\$?\""

sleep 1

header "3/3 — block: Schedule II without proper DEA license"
step "Oxycodone (Schedule II) attempted with lic_dea_basic, which only covers Schedules III-V. Expect a BLOCKER citing 21 CFR 1301.74 and exit code 2." \
    "python -m agents.compliance_checker.agent --tenant t_acme --license lic_dea_basic --license lic_state_acme --formulary form_acute_care --cart docs/demos/fixtures/cart_block.json; echo \"exit=\$?\""
