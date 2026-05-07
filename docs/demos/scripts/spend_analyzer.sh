#!/usr/bin/env bash
# Demo: spend_analyzer — code execution sandbox over purchase history.
#
# Record with:
#     asciinema rec docs/demos/casts/spend_analyzer.cast \
#         -c "bash docs/demos/scripts/spend_analyzer.sh"
#
# This demo runs longer than the others (~60-90s) because the model executes
# Python in the sandbox: load the CSV, compute spend rollups, generate a
# chart. Worth the runtime — the saved PNG is the "wow" moment.

source "$(dirname "$0")/_demo.sh"
require_env
require_repo_root

clear
mkdir -p reports/t_acme

header "spend_analyzer — monthly tenant analytics via code execution"

step "Upload a 30-row purchase history CSV (planted signals: Metformin price spike on Cardinal, Amoxicillin single-sourced from McKesson). Claude runs pandas + matplotlib in the sandbox and writes a chart PNG back to disk." \
    "python -m agents.spend_analyzer.agent --tenant t_acme --csv docs/demos/fixtures/history_sample.csv --output-dir reports/t_acme"

header "Generated artifacts"
step "List the chart files the agent saved." \
    "ls -lh reports/t_acme/"
