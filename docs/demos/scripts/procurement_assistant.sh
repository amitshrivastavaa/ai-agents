#!/usr/bin/env bash
# Demo: procurement_assistant.
#
# Record with:
#     asciinema rec docs/demos/casts/procurement_assistant.cast \
#         -c "bash docs/demos/scripts/procurement_assistant.sh"
#
# Or run directly to dry-run before recording:
#     bash docs/demos/scripts/procurement_assistant.sh

source "$(dirname "$0")/_demo.sh"
require_env
require_repo_root

clear
header "procurement_assistant — buyer turns natural language into a cart"

step "Buyer asks for metformin, lowest price. Agent searches the catalog, compares suppliers, and adds the cheapest fulfillable offer to the cart." \
    "python -m agents.procurement_assistant.agent --tenant t_acme --formulary form_default 'I need 500 units of metformin 500mg, looking for the lowest price'"
