"""Parcel-invoice recovery audit — find money carriers owe back.

A deterministic, stdlib-only engine that scans parcel/freight invoices for
recoverable money (late-delivery refunds, dimensional-weight errors, invalid
surcharges, duplicate billing, contract-rate mismatches) and produces a
ready-to-file claim pack. The business sells this on contingency: no recovery,
no fee.
"""
from .audit import Shipment, audit, summarize
from .claims import Claim, filing_pack

__all__ = ["Shipment", "audit", "summarize", "Claim", "filing_pack"]
