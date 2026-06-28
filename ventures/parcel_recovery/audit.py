"""Parcel-invoice audit engine: find recoverable money in carrier billing.

Pure, deterministic, stdlib-only. Each rule encodes a real recovery category
used by parcel-audit firms:

  * late_delivery   — a guaranteed service that arrived late is fully refundable
  * lost_in_transit — no delivery scan long after ship → claim the shipping cost
  * dim_weight      — billed weight exceeds max(actual, dimensional) weight
  * invalid_residential        — residential surcharge billed to a commercial address
  * invalid_address_correction — address-correction fee billed on a valid address
  * rate_mismatch   — billed base rate above the contracted rate
  * duplicate_charge — the same tracking number billed more than once
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from typing import Optional

from .claims import Claim, FILING_WINDOWS

# FedEx/UPS domestic dimensional divisor (cubic inches per pound).
DIM_DIVISOR = 139


@dataclass(frozen=True)
class Shipment:
    """One billed parcel line from a carrier invoice."""

    tracking: str
    carrier: str
    service: str
    ship_date: date
    delivery_date: Optional[date]      # None => no delivery scan yet
    committed_date: Optional[date]     # guaranteed delivery date; None => no guarantee
    zone: int
    actual_weight: float               # lb, scale weight
    billed_weight: float               # lb the carrier billed
    length_in: float
    width_in: float
    height_in: float
    is_residential: bool               # true destination type
    charges: dict                      # line item -> $ (base, fuel, residential, address_correction, other)
    address_was_valid: bool = True
    contracted_base: Optional[float] = None

    @property
    def total_billed(self) -> float:
        return round(sum(self.charges.values()), 2)

    @property
    def transportation_charge(self) -> float:
        # Refundable portion under a money-back guarantee: base + fuel.
        return round(self.charges.get("base", 0.0) + self.charges.get("fuel", 0.0), 2)

    @property
    def dim_weight(self) -> float:
        return (self.length_in * self.width_in * self.height_in) / DIM_DIVISOR


def _claim(s: Shipment, category: str, amount: float, reason: str,
           confidence: float) -> Optional[Claim]:
    if amount <= 0.005:
        return None
    return Claim(s.tracking, s.carrier, category, round(amount, 2),
                 reason, confidence, FILING_WINDOWS[category])


def check_late_delivery(s: Shipment) -> Optional[Claim]:
    if s.committed_date and s.delivery_date and s.delivery_date > s.committed_date:
        days = (s.delivery_date - s.committed_date).days
        return _claim(
            s, "late_delivery", s.transportation_charge,
            f"Delivered {days} day(s) late vs the {s.service} guarantee "
            f"({s.committed_date} -> {s.delivery_date}); full transportation refund.",
            0.97)
    return None


def check_lost(s: Shipment, as_of: date) -> Optional[Claim]:
    if s.delivery_date is None:
        ref = s.committed_date or s.ship_date
        if (as_of - ref).days >= 7:
            return _claim(
                s, "lost_in_transit", s.transportation_charge,
                f"No delivery scan {(as_of - s.ship_date).days} days after ship; "
                f"likely lost - file shipping refund.", 0.6)
    return None


def check_dim_weight(s: Shipment) -> Optional[Claim]:
    expected = max(s.actual_weight, math.ceil(s.dim_weight))
    if s.billed_weight > expected + 1e-9:
        base = s.charges.get("base", 0.0)
        over = base * (s.billed_weight - expected) / s.billed_weight
        return _claim(
            s, "dim_weight", over,
            f"Billed {s.billed_weight:.0f} lb vs expected {expected:.0f} lb "
            f"(actual {s.actual_weight:.0f}, dim {s.dim_weight:.1f}); "
            f"overcharge on {s.billed_weight - expected:.0f} lb.", 0.85)
    return None


def check_residential(s: Shipment) -> Optional[Claim]:
    amt = s.charges.get("residential", 0.0)
    if amt > 0 and not s.is_residential:
        return _claim(s, "invalid_residential", amt,
                      "Residential surcharge billed to a commercial address.", 0.9)
    return None


def check_address_correction(s: Shipment) -> Optional[Claim]:
    amt = s.charges.get("address_correction", 0.0)
    if amt > 0 and s.address_was_valid:
        return _claim(s, "invalid_address_correction", amt,
                      "Address-correction fee billed though the address was valid.", 0.8)
    return None


def check_rate_mismatch(s: Shipment) -> Optional[Claim]:
    if s.contracted_base is not None:
        base = s.charges.get("base", 0.0)
        if base > s.contracted_base + 1e-9:
            return _claim(
                s, "rate_mismatch", base - s.contracted_base,
                f"Billed base ${base:.2f} exceeds contracted ${s.contracted_base:.2f} "
                f"for {s.service} zone {s.zone}.", 0.92)
    return None


PER_SHIPMENT_RULES = (check_late_delivery, check_dim_weight, check_residential,
                      check_address_correction, check_rate_mismatch)


def _max_date(shipments) -> date:
    dates = []
    for s in shipments:
        dates.append(s.ship_date)
        if s.delivery_date:
            dates.append(s.delivery_date)
        if s.committed_date:
            dates.append(s.committed_date)
    return max(dates) if dates else date(2026, 1, 1)


def audit(shipments, as_of: Optional[date] = None):
    """Return every recoverable Claim found across a set of shipments."""
    shipments = list(shipments)
    as_of = as_of or _max_date(shipments)
    claims = []

    # Cross-shipment: duplicate billing (same tracking billed more than once).
    seen = set()
    is_duplicate = [False] * len(shipments)
    for i, s in enumerate(shipments):
        if s.tracking in seen:
            is_duplicate[i] = True
            c = _claim(s, "duplicate_charge", s.total_billed,
                       f"Tracking {s.tracking} billed more than once; "
                       f"full duplicate charge recoverable.", 0.95)
            if c:
                claims.append(c)
        else:
            seen.add(s.tracking)

    # Per-shipment rules (skip duplicate lines — the whole line already comes back).
    for i, s in enumerate(shipments):
        if is_duplicate[i]:
            continue
        for rule in PER_SHIPMENT_RULES:
            c = rule(s)
            if c:
                claims.append(c)
        c = check_lost(s, as_of)
        if c:
            claims.append(c)
    return claims


def summarize(shipments, claims, contingency: float = 0.25) -> dict:
    """Roll claims up into headline numbers + contingency economics."""
    shipments = list(shipments)
    total_billed = round(sum(s.total_billed for s in shipments), 2)
    total_recoverable = round(sum(c.amount for c in claims), 2)

    by_category: dict = {}
    for c in claims:
        d = by_category.setdefault(c.category, {"count": 0, "amount": 0.0})
        d["count"] += 1
        d["amount"] = round(d["amount"] + c.amount, 2)

    fee = round(total_recoverable * contingency, 2)
    return {
        "shipments": len(shipments),
        "total_billed": total_billed,
        "total_recoverable": total_recoverable,
        "recovery_rate": round(total_recoverable / total_billed, 4) if total_billed else 0.0,
        "claim_count": len(claims),
        "by_category": by_category,
        "contingency": contingency,
        "your_fee": fee,
        "client_net": round(total_recoverable - fee, 2),
    }
