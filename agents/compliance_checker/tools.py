"""Tool definitions for the compliance checker."""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from lib.tenant import TenantContext

from .stubs import DrugMaster, InventoryService, LicenseRegistry


LOOKUP_DRUG = {
    "name": "lookup_drug",
    "description": (
        "Look up a drug by SKU or NDC. Returns the DEA schedule (null if "
        "not controlled), cold-chain flag, and the formularies that include "
        "it."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sku_or_ndc": {"type": "string"},
        },
        "required": ["sku_or_ndc"],
    },
}

CHECK_LICENSE_COVERAGE = {
    "name": "check_license_coverage",
    "description": (
        "Check whether the tenant's licenses cover the given DEA schedule. "
        "Returns the covering license IDs and any expiring/expired licenses. "
        "Pass `dea_schedule` as null to verify the tenant has a basic state-"
        "board license on file."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "dea_schedule": {
                "type": ["string", "null"],
                "enum": ["I", "II", "III", "IV", "V", None],
            },
        },
        "required": ["dea_schedule"],
    },
}

CHECK_LOT_EXPIRY = {
    "name": "check_lot_expiry",
    "description": (
        "Return days-to-expiry for the cheapest available lot of the SKU. "
        "Use this to flag short-dated inventory."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sku": {"type": "string"},
            "lot_id": {"type": "string"},
        },
        "required": ["sku"],
    },
}


TOOLS = [LOOKUP_DRUG, CHECK_LICENSE_COVERAGE, CHECK_LOT_EXPIRY]


class ComplianceTools:
    """Adapters from tool calls to backend services."""

    def __init__(
        self,
        tenant: TenantContext,
        drugs: DrugMaster,
        licenses: LicenseRegistry,
        inventory: InventoryService,
    ) -> None:
        self.tenant = tenant
        self.drugs = drugs
        self.licenses = licenses
        self.inventory = inventory

    def dispatch(self, name: str, args: dict[str, Any]) -> str:
        if name == "lookup_drug":
            return self._lookup_drug(args["sku_or_ndc"])
        if name == "check_license_coverage":
            return self._check_license(args.get("dea_schedule"))
        if name == "check_lot_expiry":
            return self._check_expiry(args["sku"], args.get("lot_id"))
        return _err(f"unknown tool {name!r}")

    def _lookup_drug(self, sku_or_ndc: str) -> str:
        drug = self.drugs.lookup(sku_or_ndc)
        if drug is None:
            return _err(f"no drug record for {sku_or_ndc!r}")
        return _ok(asdict(drug))

    def _check_license(self, dea_schedule: str | None) -> str:
        records = self.licenses.get_many(self.tenant.license_ids)
        if not records:
            return _ok(
                {
                    "covered": False,
                    "reason": "tenant has no licenses on file",
                    "covering_licenses": [],
                }
            )

        covering = []
        if dea_schedule is None:
            covering = [
                r.license_id for r in records if r.type in ("state-board", "dea")
            ]
            covered = bool(covering)
            reason = (
                "state-board or DEA license present"
                if covered
                else "no state-board or DEA license"
            )
        else:
            covering = [
                r.license_id
                for r in records
                if dea_schedule in r.dea_schedules_covered
            ]
            covered = bool(covering)
            reason = (
                f"schedule {dea_schedule} covered"
                if covered
                else f"no license covers schedule {dea_schedule}"
            )

        return _ok(
            {
                "covered": covered,
                "reason": reason,
                "covering_licenses": covering,
                "all_licenses": [
                    {"license_id": r.license_id, "expires_on": r.expires_on}
                    for r in records
                ],
            }
        )

    def _check_expiry(self, sku: str, lot_id: str | None) -> str:
        days = self.inventory.days_to_expiry(sku, lot_id)
        if days is None:
            return _err(f"no expiry data for {sku!r}")
        return _ok({"sku": sku, "lot_id": lot_id, "days_to_expiry": days})


def _ok(payload: dict) -> str:
    return json.dumps({"ok": True, **payload}, default=str)


def _err(message: str) -> str:
    return json.dumps({"ok": False, "error": message})
