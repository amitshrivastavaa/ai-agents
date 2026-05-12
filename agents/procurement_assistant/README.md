# procurement-assistant

Conversational catalog & cart-building agent for buyers on the pharma
procurement platform. A pharmacist or hospital procurement officer describes
what they need; the agent searches the catalog, compares supplier offers, and
builds a draft cart — all scoped to the tenant's formulary.

## Demo

<!--
After recording, replace the line below with:
[![asciicast](https://asciinema.org/a/<ID>.svg)](https://asciinema.org/a/<ID>)

Recording command:
    asciinema rec docs/demos/casts/procurement_assistant.cast \
        -c "bash docs/demos/scripts/procurement_assistant.sh"
    asciinema upload docs/demos/casts/procurement_assistant.cast
-->

> _Demo recording — TBD. See [`docs/demos/scripts/procurement_assistant.sh`](../../docs/demos/scripts/procurement_assistant.sh) for the recording command._

## Use

```sh
# Single turn
python -m agents.procurement_assistant.agent \
    --tenant t_acme --formulary form_default \
    "I need 500 units of metformin 500mg, lowest price"

# Multi-turn REPL
python -m agents.procurement_assistant.agent \
    --tenant t_acme --interactive
```

## Capabilities

| Tool | What it does |
| --- | --- |
| `search_catalog` | Free-text search across generic name, brand, strength, NDC. Optional formulary filter. |
| `get_product_details` | Single SKU lookup. |
| `compare_suppliers` | Returns supplier offers for a SKU at the requested quantity, filtered to fulfillable offers (in-stock, MOQ-met). |
| `add_to_cart` | Adds a confirmed line to the buyer's draft cart. |
| `view_cart` | Returns the running cart state. |

## Production wiring

`stubs.py` ships in-memory `CatalogService`, `SupplierService`, and
`CartService` with a small sample data set. Replacing each with the real
backend client is a one-class swap — the `ProcurementTools` glue in
`tools.py` is the only thing the agent sees.

The platform is responsible for:

- Hydrating `TenantContext` from the authenticated session (the agent never
  takes `tenant_id` from the model).
- Persisting the cart ID across turns (the agent treats it as opaque).
- Running the [compliance-checker](../compliance_checker/) on the draft cart
  before checkout.

## How it works

- Claude Opus 4.7 with adaptive thinking and prompt caching on the system
  prompt.
- Tool loop driven by `lib/llm.run_tool_loop`.
- Structured logs (`lib/logging`) carry `tenant_id`, `cart_id`, and tool
  metadata for audit.
