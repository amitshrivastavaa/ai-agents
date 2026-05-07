# Demo runbook — procurement_assistant

**Goal:** show a buyer building a cart in one turn — the agent searches
catalog, compares suppliers, picks the cheapest fulfillable offer, and adds
it to the cart.

**Length:** ~45 seconds.

## Pre-record setup

```sh
export ANTHROPIC_API_KEY=sk-ant-...
export LOG_LEVEL=WARNING   # quieter demo
clear
```

## Single-turn version (recommended for demo reels)

```sh
python -m agents.procurement_assistant.agent \
    --tenant t_acme \
    --formulary form_default \
    "I need 500 units of metformin 500mg, looking for the lowest price"
```

What the viewer should see:

1. The agent prints a short plan ("I'll search the catalog for metformin
   500mg…").
2. Tool call: `search_catalog` — model picks `SKU-METF-500-100`.
3. Tool call: `compare_suppliers` for that SKU at qty=500.
4. The agent presents 2–3 supplier offers ranked by price.
5. Tool call: `add_to_cart` with the cheapest fulfillable offer.
6. A short confirmation: "Added 500 × Metformin HCl 500mg from Cardinal
   Health at $4.62/unit. Cart total: $2,310.00."

## Multi-turn version (interactive REPL)

```sh
python -m agents.procurement_assistant.agent \
    --tenant t_acme --formulary form_default --interactive
```

Then type, pausing between lines:

```
> I need lisinopril 10mg, 180 units
> add the cheapest one
> show me my cart
```

This shows the agent maintaining cart state across turns and confirming
choices.

## Variants worth recording

- **Formulary filter.** Search for a non-formulary item with
  `--formulary form_default` (which excludes the Schedule II oxycodone
  SKU); the agent finds nothing and explains why.
- **Controlled substance.** Run with `--formulary form_acute_care` and ask
  for "oxycodone 5mg, 100 units"; the agent surfaces the Schedule II
  status and reminds the buyer about the compliance check at checkout.

## Embedding

```md
![procurement_assistant demo](docs/demos/casts/procurement_assistant.cast)
```
