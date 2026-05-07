# Demo recordings

Each agent has a runbook in this directory. The runbook is what you run
*while* the screen is being recorded — the exact commands, the inputs to
type, and what the viewer should see.

## Tooling (pick one)

- **[asciinema](https://asciinema.org/)** — `asciinema rec demo.cast`. Free,
  embeddable in the README via SVG, plays back as real text (selectable,
  searchable). Recommended.
- **[terminalizer](https://terminalizer.com/)** — `terminalizer record`.
  Produces a GIF, larger but works anywhere images render.
- **OS screen recorder** — fine for a one-off, but loses the text fidelity
  of a terminal recording.

## Setup before you record

```sh
export ANTHROPIC_API_KEY=sk-ant-...
pip install -r requirements.txt

# Optional: lower the log level so demo logs don't dominate the screen.
export LOG_LEVEL=WARNING
```

Run from the repo root.

## Tips

- **Resize your terminal to ~110 cols × 30 rows.** GitHub renders embedded
  recordings in a fixed width; wider terminals get cut off.
- **Clear the screen before each recording** (`clear`) so the cast starts
  from a blank canvas.
- **Type the command, pause for half a second, then run.** Viewers need a
  beat to read the command before the output rushes in.
- **Keep each demo to 30–60 seconds.** Long demos lose attention. If a
  scenario is naturally longer (compliance with multiple findings), split
  it into two casts.

## Per-agent runbooks

| Agent | Runbook | What it shows |
| --- | --- | --- |
| `procurement_assistant` | [procurement_assistant.md](procurement_assistant.md) | Buyer asks for metformin → search → compare suppliers → add to cart. |
| `po_extractor` | [po_extractor.md](po_extractor.md) | Drop a PO PDF → typed JSON output → confidence routing. |
| `compliance_checker` | [compliance_checker.md](compliance_checker.md) | Cart with a Schedule II SKU + insufficient license → `BLOCKER` + exit code 2. |
| `spend_analyzer` | [spend_analyzer.md](spend_analyzer.md) | Tiny purchase-history CSV → analysis + saved chart PNG. |

## Embedding in the README

Once you have a `.cast` (asciinema) or `.gif` file, link it from the
agent's README:

```md
![demo](docs/demos/casts/procurement_assistant.cast)
```

asciinema recordings render as a player; GIFs render inline.
