# Demo runbook — spend_analyzer

**Goal:** show the code-execution sandbox in action. Upload a small purchase
history CSV, watch Claude run pandas, and see a chart PNG drop into the
output directory.

**Length:** ~60–90 seconds.

## Pre-record setup

```sh
export ANTHROPIC_API_KEY=sk-ant-...
export LOG_LEVEL=WARNING
mkdir -p reports/t_acme
clear
```

A sample CSV ships at [`fixtures/history_sample.csv`](fixtures/history_sample.csv) —
small enough that the analysis fits on one screen, but large enough to
produce real signal (multiple suppliers, an obvious price spike, a single-
sourced SKU).

## Recording

```sh
python -m agents.spend_analyzer.agent \
    --tenant t_acme \
    --csv docs/demos/fixtures/history_sample.csv \
    --output-dir reports/t_acme

# After the agent finishes:
ls -lh reports/t_acme/
```

What the viewer should see:

1. CSV uploads to the sandbox.
2. Streamed analysis: column list, row count, top spend, supplier
   concentration, anomalies, savings recommendations.
3. A short markdown summary at the end.
4. `ls` shows one or two PNG charts saved to `reports/t_acme/`.

## Optional: open one of the charts

If you're recording with a screen recorder rather than a terminal recorder:

```sh
open reports/t_acme/top_spend.png       # macOS
xdg-open reports/t_acme/top_spend.png   # Linux
```

This is the "wow" moment — a chart the model generated end-to-end from a
CSV the viewer just saw.

## Variants worth recording

- **Anomaly detection.** Edit the CSV to inject an obvious 30% price spike
  on one SKU+supplier; the agent should call it out as an anomaly with
  the math.
- **Single-source risk.** Make one SKU 100% sourced from one supplier; the
  agent should flag it as concentration risk.

## Embedding

```md
![spend_analyzer demo](docs/demos/casts/spend_analyzer.cast)
```
