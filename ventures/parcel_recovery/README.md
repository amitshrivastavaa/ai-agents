# Parcel Recovery — find the money carriers owe back

> A deterministic audit engine that scans parcel/freight invoices for recoverable
> money and produces a ready-to-file claim pack. Sold on **contingency: no recovery,
> no fee.** No LLM required — so it doesn't go stale when a new model ships.

The average company loses **3–7% of its parcel spend** to overcharges, billing
errors, and missed refunds, and **over $1B in FedEx/UPS credits go unclaimed every
year.** This engine is the part that finds the money.

## Why this is a business, not a feature
- **Risk-free offer.** "Send us 12 months of invoices, we'll show you what's
  recoverable — free. You only pay a % of what we actually get back." Lowest-friction
  B2B sale there is.
- **The money is real and verifiable** — the carrier either refunds it or doesn't.
- **Incumbents are slow human-labor / consulting shops** (or take 50% of savings). An
  automated, AI-native cost structure undercuts them and serves the mid-market they
  ignore.
- **Outside the model.** The moat is the client book, the per-carrier rules, the
  outcome data, and the carrier integrations — none of which a new LLM release touches.

See **[GO_TO_MARKET.md](GO_TO_MARKET.md)** for the 90-day plan to first revenue.

## What it detects
| Category | What it catches | Carrier rule |
|---|---|---|
| **Late delivery** | A guaranteed service that arrived late | Money-back guarantee → full transportation refund (~15-day window) |
| **Lost in transit** | No delivery scan long after ship | Shipping-cost refund |
| **Dimensional-weight overcharge** | Billed weight > max(actual, dim weight) | Dim divisor 139 (domestic) |
| **Invalid residential surcharge** | Residential fee billed to a commercial address | Surcharge reversal |
| **Invalid address-correction fee** | Correction fee billed on a valid address | Fee reversal |
| **Contract rate mismatch** | Billed base above your contracted rate | Rate adjustment |
| **Duplicate billing** | Same tracking number billed twice | Full duplicate reversal |

## Run it
```bash
# Built-in sample (one month of invoices with planted + clean lines)
python -m ventures.parcel_recovery

# Your own data
python -m ventures.parcel_recovery invoices.csv --contingency 0.20
```

CSV columns (header required; blanks allowed):
```
tracking, carrier, service, ship_date, delivery_date, committed_date,
zone, actual_weight, billed_weight, length_in, width_in, height_in,
is_residential, base, fuel, residential_fee, address_correction_fee,
address_was_valid, contracted_base
```
Dates `YYYY-MM-DD`; booleans `true/false`; leave `delivery_date` blank if
undelivered and `committed_date` blank for services with no guarantee.

## Sample output
```
                    PARCEL RECOVERY AUDIT
==============================================================
  92 shipments audited      $2,705.68 billed

  RECOVERABLE:  $262.43   (9.7% of spend, 11 claims)

  By category
    Late delivery (money-back guarantee) $  126.60  ##########.......... x3
    Dimensional-weight overcharge      $   38.23  ###................. x2
    Lost in transit                    $   31.70  ##.................. x1
    Duplicate billing                  $   28.00  ##.................. x1
    Invalid address-correction fee     $   18.00  #................... x1
    Invalid residential surcharge      $   11.90  #................... x2
    Contract rate mismatch             $    8.00  #................... x1

  Economics  (contingency: no recovery, no fee)
    Client keeps     $   196.82   (75%)
    Your fee @ 25%    $    65.61
```
Each claim comes out as a dated, carrier-grouped filing pack (soonest deadline first).

## Tests
```bash
python -m unittest ventures.parcel_recovery.tests.test_audit -v   # 18 tests
```

## Honest scope
This prototype is the **detection + claim-assembly** core — the part that proves
there's money on the table. The real venture adds the unglamorous moat around it:
carrier-API integrations to pull invoices and **file** claims automatically, a
contracted-rate database per client, a dashboard, and the recovered-outcome data
that compounds. Detection is the wedge; filing + integration + the client book is
the business.

## Layout
```
audit.py        Shipment model + the 7 detection rules + summarize()
claims.py       Claim model, filing windows, filing-pack formatter
sample_data.py  deterministic month of invoices (clean + planted)
demo.py         the report you see above
__main__.py     CLI (sample or your CSV)
tests/          18 unittest cases
```
