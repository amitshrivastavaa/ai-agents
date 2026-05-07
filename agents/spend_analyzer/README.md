# spend-analyzer

Code-execution-driven analysis of a tenant's purchase history. Uploads a CSV
to the Anthropic code sandbox and asks Claude to produce a spend summary,
flag anomalies, recommend savings, and generate charts. Designed to run on a
schedule (e.g. monthly) per tenant.

## Demo

<!--
After recording, replace the line below with:
[![asciicast](https://asciinema.org/a/<ID>.svg)](https://asciinema.org/a/<ID>)

Recording command:
    asciinema rec docs/demos/casts/spend_analyzer.cast \
        -c "bash docs/demos/scripts/spend_analyzer.sh"
    asciinema upload docs/demos/casts/spend_analyzer.cast
-->

> _Demo recording — TBD. See [`docs/demos/scripts/spend_analyzer.sh`](../../docs/demos/scripts/spend_analyzer.sh) for the recording command. Uses a 30-row history CSV with planted signals: a +19% Metformin price spike on `sup_cardinal` and an Amoxicillin single-source dependency on `sup_mckesson`._

## Use

```sh
python -m agents.spend_analyzer.agent \
    --tenant t_acme \
    --csv history.csv \
    --output-dir ./reports/t_acme
```

`history.csv` is the tenant's purchase history. Suggested columns:

```
po_date,sku,generic_name,qty,unit_price,supplier_id,dea_schedule
2026-01-04,SKU-METF-500-100,Metformin HCl,500,4.78,sup_mckesson,
2026-01-04,SKU-LISI-10-90,Lisinopril,180,3.10,sup_amerisource,
...
```

Output:

- A markdown analysis streamed to stdout (top spend, supplier concentration,
  anomalies, savings recommendations, summary).
- Generated chart PNGs saved to `--output-dir` (sanitized filenames).
- Structured logs to stderr with input/output token counts per run.

## What it analyzes

- **Top spend**: top 10 SKUs by total spend.
- **Supplier concentration**: share of spend per supplier; flags 100%-single-
  source SKUs as a risk.
- **Price drift**: same SKU+supplier with >15% unit-price increase in the
  trailing window.
- **Outliers**: unit prices that deviate from the tenant median for that SKU.
- **Savings**: concrete actions (e.g. "consolidate to supplier X at $4.62
  unit, save ~$580 annual"), each with the math shown.

## How it works

- Claude Opus 4.7 with the server-side `code_execution_20260120` tool.
- CSV uploaded via the Files API (beta header `files-api-2025-04-14`) and
  referenced as a `container_upload` block — the sandbox sees it as a real
  file.
- Sandbox has pandas, numpy, matplotlib pre-installed; the agent saves
  PNG charts to the working directory and emits them as
  `bash_code_execution_output` blocks, which the agent then downloads.
- Filenames are sanitized with `os.path.basename` before writing to disk.
