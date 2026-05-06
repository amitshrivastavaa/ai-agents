"""Pydantic schema for an extracted purchase order.

This is the canonical shape the platform expects. The PO extractor uses it as
the structured-output target for `client.messages.parse()` so every result is
validated before it reaches the rest of the system.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """A single line on the PO."""

    sku: str | None = Field(
        default=None,
        description="Internal SKU if present on the document. Null if the PO "
                    "uses an external code or only a free-text description.",
    )
    ndc: str | None = Field(
        default=None,
        description="National Drug Code (e.g. '00093-1048-01') if present.",
    )
    description: str = Field(description="Product description as written on the PO.")
    qty: int = Field(ge=1, description="Quantity ordered.")
    unit_of_measure: str | None = Field(
        default=None,
        description="UOM if specified (each, pack, case, vial, etc.).",
    )
    unit_price: float = Field(ge=0, description="Per-unit price.")
    line_total: float = Field(ge=0, description="qty * unit_price (or as printed).")


class PurchaseOrder(BaseModel):
    """The full extracted PO."""

    po_number: str = Field(description="Purchase order number / ID.")
    issue_date: date = Field(description="Date the PO was issued.")
    delivery_date: date | None = Field(
        default=None, description="Requested delivery date if specified."
    )

    vendor_name: str = Field(description="Selling vendor / supplier name.")
    vendor_address: str | None = Field(
        default=None, description="Vendor address as a single string."
    )
    vendor_dea: str | None = Field(
        default=None,
        description="Vendor DEA registration number if present (controlled subs).",
    )

    buyer_name: str = Field(description="Buyer organization name.")
    buyer_address: str | None = None
    buyer_dea: str | None = None

    line_items: list[LineItem] = Field(min_length=1)
    subtotal: float = Field(ge=0)
    tax: float | None = Field(default=None, ge=0)
    shipping: float | None = Field(default=None, ge=0)
    total: float = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)

    payment_terms: str | None = Field(
        default=None, description="Free-text terms, e.g. 'Net 30'."
    )

    extraction_confidence: Literal["high", "medium", "low"] = Field(
        description=(
            "Self-reported confidence. Use 'low' when fields were inferred or "
            "the document was hard to read so the platform can route low-"
            "confidence extractions to human review."
        )
    )
    notes: str | None = Field(
        default=None,
        description="Anything the human reviewer should know (ambiguities, "
                    "missing fields, inferred values).",
    )
