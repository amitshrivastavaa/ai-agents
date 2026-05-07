"""Schemas for the compliance check input and report."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CartLine(BaseModel):
    """A line on the draft cart submitted for compliance review."""

    sku: str
    qty: int = Field(ge=1)
    supplier_id: str
    unit_price: float = Field(ge=0)


class CartForReview(BaseModel):
    """Minimal cart shape the checker accepts."""

    cart_id: str
    tenant_id: str
    lines: list[CartLine] = Field(min_length=1)


class Finding(BaseModel):
    """A single rule outcome."""

    severity: Literal["BLOCKER", "WARNING", "INFO"]
    line_index: int | None = Field(
        default=None,
        description="0-indexed cart line. Null for cart-wide findings.",
    )
    rule_id: str = Field(
        description=(
            "Stable rule slug, e.g. 'controlled-substance-license', "
            "'expiry-30-days', 'formulary-not-approved'."
        )
    )
    message: str
    citation: str | None = Field(
        default=None,
        description="Regulation citation if applicable, e.g. '21 CFR 1301.74'.",
    )


class ComplianceReport(BaseModel):
    overall_status: Literal["pass", "warn", "block"] = Field(
        description=(
            "block: at least one BLOCKER. warn: WARNINGs but no BLOCKERs. "
            "pass: only INFO findings (or none)."
        )
    )
    findings: list[Finding]
    summary: str = Field(description="One-paragraph summary for the buyer.")
