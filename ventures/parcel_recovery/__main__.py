"""CLI: audit a CSV of parcel invoices, or the built-in sample if no file is given.

    python -m ventures.parcel_recovery                      # sample data
    python -m ventures.parcel_recovery invoices.csv         # your invoices
    python -m ventures.parcel_recovery invoices.csv --contingency 0.20

CSV columns (header row required; blanks allowed where noted):
    tracking, carrier, service, ship_date, delivery_date, committed_date,
    zone, actual_weight, billed_weight, length_in, width_in, height_in,
    is_residential, base, fuel, residential_fee, address_correction_fee,
    address_was_valid, contracted_base
Dates are YYYY-MM-DD. Booleans are true/false. Leave delivery_date blank if
undelivered; committed_date blank if the service has no guarantee.
"""
from __future__ import annotations

import csv as _csv
import sys
from datetime import datetime

from .audit import Shipment
from .demo import render
from .sample_data import sample_shipments


def _date(v):
    v = (v or "").strip()
    return datetime.strptime(v, "%Y-%m-%d").date() if v else None


def _num(v, default=0.0):
    v = (v or "").strip()
    return float(v) if v else default


def _bool(v, default=False):
    v = (v or "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "y", "t")


def load_csv(path):
    shipments = []
    with open(path, newline="", encoding="utf-8") as fh:
        for r in _csv.DictReader(fh):
            charges = {"base": _num(r.get("base")), "fuel": _num(r.get("fuel"))}
            if _num(r.get("residential_fee")):
                charges["residential"] = _num(r.get("residential_fee"))
            if _num(r.get("address_correction_fee")):
                charges["address_correction"] = _num(r.get("address_correction_fee"))
            contracted = (r.get("contracted_base") or "").strip()
            shipments.append(Shipment(
                tracking=r["tracking"].strip(),
                carrier=(r.get("carrier") or "").strip(),
                service=(r.get("service") or "").strip(),
                ship_date=_date(r.get("ship_date")),
                delivery_date=_date(r.get("delivery_date")),
                committed_date=_date(r.get("committed_date")),
                zone=int(_num(r.get("zone"))),
                actual_weight=_num(r.get("actual_weight")),
                billed_weight=_num(r.get("billed_weight")),
                length_in=_num(r.get("length_in")), width_in=_num(r.get("width_in")),
                height_in=_num(r.get("height_in")),
                is_residential=_bool(r.get("is_residential")),
                charges=charges,
                address_was_valid=_bool(r.get("address_was_valid"), default=True),
                contracted_base=float(contracted) if contracted else None))
    return shipments


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    contingency = 0.25
    if "--contingency" in argv:
        i = argv.index("--contingency")
        contingency = float(argv[i + 1])
        del argv[i:i + 2]
    paths = [a for a in argv if not a.startswith("-")]
    shipments = load_csv(paths[0]) if paths else sample_shipments()
    print(render(shipments, contingency))


if __name__ == "__main__":
    main()
