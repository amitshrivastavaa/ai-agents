#!/usr/bin/env bash
# Demo: po_extractor — PDF -> typed PurchaseOrder.
#
# Pre-record (one-time):
#     pip install reportlab
#     python docs/demos/scripts/generate_sample_po.py
#
# Record with:
#     asciinema rec docs/demos/casts/po_extractor.cast \
#         -c "bash docs/demos/scripts/po_extractor.sh"

source "$(dirname "$0")/_demo.sh"
require_env
require_repo_root

PDF="docs/demos/fixtures/sample_po.pdf"
if [ ! -f "$PDF" ]; then
    echo "Error: $PDF not found." >&2
    echo "Generate it first:" >&2
    echo "    pip install reportlab" >&2
    echo "    python docs/demos/scripts/generate_sample_po.py" >&2
    exit 1
fi

# jq is optional but produces a much cleaner highlight at the end.
HAS_JQ=0
if command -v jq >/dev/null 2>&1; then
    HAS_JQ=1
fi

clear
header "po_extractor — PDF to typed PurchaseOrder"

step "Extract a sample PO PDF. Output is a JSON-encoded PurchaseOrder validated against a Pydantic schema." \
    "python -m agents.po_extractor.agent --tenant t_acme --pdf $PDF | tee /tmp/po.json"

if [ "$HAS_JQ" -eq 1 ]; then
    header "Headline fields"
    step "Pull out the fields a downstream service cares about, plus the self-reported extraction_confidence." \
        "jq '{po_number, vendor_name, line_items, total, extraction_confidence, notes}' /tmp/po.json"
fi
