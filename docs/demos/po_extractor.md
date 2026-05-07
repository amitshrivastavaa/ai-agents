# Demo runbook — po_extractor

**Goal:** drop a PO PDF (or scanned image) on the agent and show a typed
`PurchaseOrder` JSON come out the other side, with `extraction_confidence`
visible.

**Length:** ~30 seconds.

## Pre-record setup

You need a sample PO. Two easy options:

1. **Make one in 60 seconds.** Open Pages / Google Docs, type a fake PO
   (PO number, vendor name, 3–4 line items with NDCs, totals), export as
   PDF. Save as `docs/demos/fixtures/sample_po.pdf` (gitignored — see
   below).
2. **Use a public sample.** Search "purchase order template PDF" and use
   any free template; fill in pharma SKUs (metformin, lisinopril, etc.).

Sample SKUs / NDCs that match the rest of the repo:

| Generic name | NDC | Strength |
| --- | --- | --- |
| Metformin HCl | 00093-1048-01 | 500 mg tablet |
| Lisinopril | 68180-0513-09 | 10 mg tablet |
| Amoxicillin | 65862-0017-30 | 500 mg capsule |
| Insulin glargine | 00088-2220-33 | 100 U/mL vial |

## Recording

```sh
export ANTHROPIC_API_KEY=sk-ant-...
export LOG_LEVEL=WARNING
clear

python -m agents.po_extractor.agent \
    --tenant t_acme \
    --pdf docs/demos/fixtures/sample_po.pdf \
    | tee /tmp/po.json

# Then highlight the interesting fields:
jq '{po_number, vendor_name, line_items, total, extraction_confidence, notes}' /tmp/po.json
```

What the viewer should see:

1. Command runs, takes ~5–10s.
2. Full JSON streams to stdout.
3. The `jq` highlight pulls out the headline fields, including
   `extraction_confidence`.

## Variants worth recording

- **Low-confidence path.** Use a deliberately bad scan (rotated, blurry).
  The agent should produce `extraction_confidence: "low"` with a populated
  `notes` field explaining what was unreadable.
- **Image input.** Same flow but `--image scan.png` — shows the agent
  handles photos, not just clean PDFs.

## Embedding

```md
![po_extractor demo](docs/demos/casts/po_extractor.cast)
```

## Note on fixtures

Don't commit real vendor POs. The `.gitignore` at the repo root excludes
`docs/demos/fixtures/*.pdf` for this reason. If you want to commit a sample,
generate it from scratch and confirm it has no real vendor PII.
