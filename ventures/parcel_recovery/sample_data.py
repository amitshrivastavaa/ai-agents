"""A realistic, deterministic month of parcel invoices.

~80 clean shipments plus planted line items across every recovery category, so
the demo finds real (and reproducible) money on every run. No RNG — purely a
function of the index, so results never drift.
"""
from __future__ import annotations

import math
from datetime import date, timedelta

from .audit import Shipment, DIM_DIVISOR


def _ship(tracking, carrier, service, ship, delivered, committed, zone, actual,
          dims, residential, base, fuel, *, dim_overbill=0.0, residential_fee=0.0,
          addr_fee=0.0, addr_valid=True, contracted=None):
    """Build a Shipment; bills the correct weight unless dim_overbill is set."""
    length, width, height = dims
    dim_w = (length * width * height) / DIM_DIVISOR
    expected = max(actual, math.ceil(dim_w))
    billed = expected + dim_overbill

    charges = {"base": base, "fuel": fuel}
    if residential_fee:
        charges["residential"] = residential_fee
    if addr_fee:
        charges["address_correction"] = addr_fee

    return Shipment(
        tracking=tracking, carrier=carrier, service=service, ship_date=ship,
        delivery_date=delivered, committed_date=committed, zone=zone,
        actual_weight=float(actual), billed_weight=float(billed),
        length_in=float(length), width_in=float(width), height_in=float(height),
        is_residential=residential, charges=charges, address_was_valid=addr_valid,
        contracted_base=contracted)


def _clean_filler(n=80):
    """Correctly-billed, on-time shipments — the bulk of any real invoice file."""
    out = []
    for i in range(n):
        zone = 2 + (i % 7)
        wt = 3 + (i % 18)
        base = round(7.5 + zone * 1.4 + wt * 0.9, 2)
        fuel = round(base * 0.16, 2)
        ship = date(2026, 3, 1) + timedelta(days=i % 20)
        deliv = ship + timedelta(days=2 + (i % 4))
        carrier = "UPS" if i % 2 else "FedEx"
        out.append(_ship(f"CLEAN{i:08d}", carrier, "Ground", ship, deliv, None,
                         zone, wt, (10, 8, 5), bool(i % 3), base, fuel))
    return out


def _planted():
    d = date
    return [
        # late delivery (guaranteed service arrived late) -> full transport refund
        _ship("794600000010", "FedEx", "Overnight", d(2026, 3, 5), d(2026, 3, 9),
              d(2026, 3, 6), 6, 3, (10, 8, 6), True, 58.40, 9.40),
        _ship("1Z100AAA0000000011", "UPS", "2Day", d(2026, 3, 6), d(2026, 3, 10),
              d(2026, 3, 9), 4, 7, (13, 10, 7), False, 26.75, 4.30),
        _ship("794600000012", "FedEx", "2Day", d(2026, 3, 9), d(2026, 3, 12),
              d(2026, 3, 11), 5, 5, (12, 9, 7), True, 23.90, 3.85),
        # dimensional-weight overcharge (billed weight inflated)
        _ship("1Z100AAA0000000020", "UPS", "Ground", d(2026, 3, 10), d(2026, 3, 13),
              None, 5, 8, (16, 12, 8), False, 39.60, 6.40, dim_overbill=10),
        _ship("794600000021", "FedEx", "Ground", d(2026, 3, 11), d(2026, 3, 16),
              None, 6, 6, (14, 10, 6), True, 33.10, 5.30, dim_overbill=11),
        # invalid residential surcharge (billed to commercial address)
        _ship("1Z100AAA0000000030", "UPS", "Ground", d(2026, 3, 12), d(2026, 3, 16),
              None, 4, 10, (15, 11, 9), False, 21.40, 3.45, residential_fee=5.85),
        _ship("794600000031", "FedEx", "Ground", d(2026, 3, 12), d(2026, 3, 17),
              None, 5, 14, (18, 13, 10), False, 28.90, 4.65, residential_fee=6.05),
        # invalid address-correction fee (address was valid)
        _ship("794600000040", "FedEx", "Ground", d(2026, 3, 13), d(2026, 3, 17),
              None, 3, 5, (11, 9, 6), True, 14.20, 2.30, addr_fee=18.00, addr_valid=True),
        # contract rate mismatch (billed base above contracted)
        _ship("1Z100AAA0000000050", "UPS", "2Day", d(2026, 3, 16), d(2026, 3, 18),
              d(2026, 3, 18), 6, 11, (16, 12, 9), False, 41.00, 6.60, contracted=33.00),
        # lost in transit (no delivery scan, shipped long ago)
        _ship("794600000060", "FedEx", "Ground", d(2026, 3, 2), None, None, 7, 9,
              (15, 12, 9), True, 27.30, 4.40),
        # duplicate billing — a clean line, then the same tracking billed again
        _ship("1Z100AAA0000000002", "UPS", "2Day", d(2026, 3, 2), d(2026, 3, 4),
              d(2026, 3, 4), 5, 9, (14, 12, 8), False, 24.10, 3.90),
        _ship("1Z100AAA0000000002", "UPS", "2Day", d(2026, 3, 2), d(2026, 3, 4),
              d(2026, 3, 4), 5, 9, (14, 12, 8), False, 24.10, 3.90),
    ]


def sample_shipments():
    return _clean_filler() + _planted()
