"""Recovery-claim model, carrier filing windows, and a submission-ready pack."""
from __future__ import annotations

from dataclasses import dataclass

# How long you have to file each claim type (days from ship/invoice date).
# Money-back-guarantee windows are tight (~15 days); billing disputes are longer.
FILING_WINDOWS = {
    "late_delivery": 15,
    "lost_in_transit": 60,
    "duplicate_charge": 180,
    "dim_weight": 180,
    "invalid_residential": 180,
    "invalid_address_correction": 180,
    "rate_mismatch": 180,
}

CATEGORY_LABELS = {
    "late_delivery": "Late delivery (money-back guarantee)",
    "lost_in_transit": "Lost in transit",
    "duplicate_charge": "Duplicate billing",
    "dim_weight": "Dimensional-weight overcharge",
    "invalid_residential": "Invalid residential surcharge",
    "invalid_address_correction": "Invalid address-correction fee",
    "rate_mismatch": "Contract rate mismatch",
}


@dataclass(frozen=True)
class Claim:
    """One recoverable line item, ready to file with the carrier."""

    tracking: str
    carrier: str
    category: str
    amount: float
    reason: str
    confidence: float      # 0..1 — odds the carrier grants it
    file_within_days: int

    @property
    def label(self) -> str:
        return CATEGORY_LABELS.get(self.category, self.category)


def filing_pack(claims) -> str:
    """Group claims by carrier into a submission-ready text block, soonest-due first."""
    by_carrier: dict = {}
    for c in claims:
        by_carrier.setdefault(c.carrier, []).append(c)

    lines = []
    for carrier in sorted(by_carrier):
        cs = by_carrier[carrier]
        total = round(sum(c.amount for c in cs), 2)
        lines.append(f"=== {carrier} — {len(cs)} claim(s), ${total:,.2f} ===")
        for c in sorted(cs, key=lambda x: (x.file_within_days, -x.amount)):
            lines.append(
                f"  [{c.file_within_days:>3}d] {c.tracking:<18} ${c.amount:>8,.2f}  {c.label}"
            )
            lines.append(f"        {c.reason}")
        lines.append("")
    return "\n".join(lines).rstrip()
