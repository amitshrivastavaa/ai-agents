# Demo recordings

Each agent has a one-command demo script in [`scripts/`](scripts/). Record
once, upload, paste the resulting URL into the agent's README. The whole
flow takes about 20 minutes for all four agents.

## Tooling

[asciinema](https://asciinema.org/) is recommended — free, embeddable in
GitHub READMEs as an SVG badge that opens a real terminal player.

```sh
# macOS
brew install asciinema

# Linux
pip install asciinema
```

## One-time setup

```sh
export ANTHROPIC_API_KEY=sk-ant-...

# Optional: only needed for the po_extractor demo. Generates a synthetic
# sample PO PDF (the file is gitignored — real vendor POs contain PII).
pip install reportlab
python docs/demos/scripts/generate_sample_po.py
```

Resize your terminal to ~110 cols × 30 rows before recording. GitHub's
embedded player has a fixed width and wider terminals get clipped.

## Record each agent (one command per agent)

```sh
mkdir -p docs/demos/casts

# 1. procurement_assistant
asciinema rec docs/demos/casts/procurement_assistant.cast \
    -c "bash docs/demos/scripts/procurement_assistant.sh"

# 2. po_extractor
asciinema rec docs/demos/casts/po_extractor.cast \
    -c "bash docs/demos/scripts/po_extractor.sh"

# 3. compliance_checker (hero clip — runs pass/warn/block in sequence)
asciinema rec docs/demos/casts/compliance_checker.cast \
    -c "bash docs/demos/scripts/compliance_checker.sh"

# 4. spend_analyzer (longer — ~60-90s — model runs Python in the sandbox)
asciinema rec docs/demos/casts/spend_analyzer.cast \
    -c "bash docs/demos/scripts/spend_analyzer.sh"
```

Each script handles `clear`, fake-typing the commands so the viewer can
read them, and pacing between steps. You don't type anything during the
recording — start the recording, run the script, walk away.

## Upload and embed

```sh
asciinema upload docs/demos/casts/procurement_assistant.cast
# Prints: https://asciinema.org/a/12345
```

Open the agent's README (e.g. `agents/procurement_assistant/README.md`) and
replace the `_Demo recording — TBD._` placeholder block with:

```md
[![asciicast](https://asciinema.org/a/12345.svg)](https://asciinema.org/a/12345)
```

The HTML comment block right above the placeholder shows the exact
recording + upload commands for that agent — keep it as a runbook.

Repeat for the other three agents.

## What each demo shows

| Agent | Script | Length | The point |
| --- | --- | --- | --- |
| `procurement_assistant` | [`scripts/procurement_assistant.sh`](scripts/procurement_assistant.sh) | ~30s | Buyer asks in natural language → catalog search → supplier comparison → cart line added. Tool loop visible. |
| `po_extractor` | [`scripts/po_extractor.sh`](scripts/po_extractor.sh) | ~20s | A PDF in, a typed `PurchaseOrder` JSON out, with `extraction_confidence` driving auto-vs-review routing. |
| `compliance_checker` | [`scripts/compliance_checker.sh`](scripts/compliance_checker.sh) | ~50s | **Hero clip.** Cycles pass → warn → block. The block scenario cites 21 CFR 1301.74 and exits non-zero. |
| `spend_analyzer` | [`scripts/spend_analyzer.sh`](scripts/spend_analyzer.sh) | ~90s | Code-execution sandbox: pandas + matplotlib over a 30-row CSV, generates and saves a chart PNG. |

## Recording tips

- **Run the script once dry** before recording, just to sanity-check your
  API key and that the agent output looks the way you want.
- **Keep a single recording short.** One agent, one script. Don't try to
  splice multiple agents into one cast.
- **The compliance_checker block scenario is your best 30 seconds.** Lead
  your portfolio / LinkedIn post with that one if you can only record one.
- **If a recording goes badly, just delete the `.cast` and re-run.** The
  files are gitignored — no harm done.

## Fixtures

See [`fixtures/README.md`](fixtures/README.md) for what's in each cart JSON
and the planted signals in the history CSV.
