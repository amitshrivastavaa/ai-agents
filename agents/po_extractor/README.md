# po-extractor

Extracts a structured `PurchaseOrder` from any inbound PO document — clean
PDFs from an ERP, scanned faxes, photos taken on a phone — so downstream
services (catalog matching, compliance, AP) can work against a single typed
shape.

## Use

```sh
python -m agents.po_extractor.agent --tenant t_acme --pdf invoice.pdf
python -m agents.po_extractor.agent --tenant t_acme --image scan.png
```

The agent prints a JSON-encoded `PurchaseOrder` to stdout. Pipe it into the
next stage of the procurement pipeline.

## Schema

See [`schema.py`](./schema.py). Fields include `po_number`, `issue_date`,
vendor / buyer info, `line_items[]` (with optional `sku` / `ndc`), totals
breakdown, payment terms, and an `extraction_confidence` enum.

## Confidence routing

Every extraction reports `extraction_confidence`:

- **high** — auto-process.
- **medium** — auto-process but log for spot-check.
- **low** — route to the human-review queue. The model also fills `notes`
  with what it was unsure about.

This is the platform's primary lever for trading off automation vs.
review burden.

## How it works

- Claude Opus 4.7's vision support handles both clean PDFs and scanned/
  photographed pages.
- `client.messages.parse(output_format=PurchaseOrder)` enforces the schema
  at the API boundary; `parsed_output` arrives validated.
- System prompt is cached so repeat extractions on the same model+schema
  pay only the schema-compile cost on the first call (~24h cache).
