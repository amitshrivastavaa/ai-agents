"""Stub regulatory data backends for the compliance checker.

Replace each class with the real registry / drug-master client. The data here
is illustrative only.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DrugRecord:
    sku: str
    ndc: str
    generic_name: str
    dea_schedule: str | None  # None for non-controlled, else 'I'-'V'
    requires_cold_chain: bool
    formularies: tuple[str, ...]  # formularies that include this drug


@dataclass(frozen=True)
class LicenseRecord:
    license_id: str
    type: str  # 'state-board', 'dea', 'wholesaler'
    state: str | None
    dea_schedules_covered: tuple[str, ...]  # e.g. ('II','III','IV','V')
    expires_on: str  # ISO date


_DRUGS: dict[str, DrugRecord] = {
    "SKU-METF-500-100": DrugRecord(
        sku="SKU-METF-500-100", ndc="00093-1048-01",
        generic_name="Metformin HCl",
        dea_schedule=None, requires_cold_chain=False,
        formularies=("form_default", "form_acute_care"),
    ),
    "SKU-LISI-10-90": DrugRecord(
        sku="SKU-LISI-10-90", ndc="68180-0513-09",
        generic_name="Lisinopril",
        dea_schedule=None, requires_cold_chain=False,
        formularies=("form_default", "form_acute_care"),
    ),
    "SKU-AMOX-500-30": DrugRecord(
        sku="SKU-AMOX-500-30", ndc="65862-0017-30",
        generic_name="Amoxicillin",
        dea_schedule=None, requires_cold_chain=False,
        formularies=("form_default", "form_acute_care"),
    ),
    "SKU-OXYC-5-100": DrugRecord(
        sku="SKU-OXYC-5-100", ndc="00406-0552-01",
        generic_name="Oxycodone HCl",
        dea_schedule="II", requires_cold_chain=False,
        formularies=("form_acute_care",),
    ),
    "SKU-INS-LANT-10": DrugRecord(
        sku="SKU-INS-LANT-10", ndc="00088-2220-33",
        generic_name="Insulin glargine",
        dea_schedule=None, requires_cold_chain=True,
        formularies=("form_default", "form_acute_care"),
    ),
}


_LICENSES: dict[str, LicenseRecord] = {
    "lic_dea_acme": LicenseRecord(
        license_id="lic_dea_acme", type="dea", state="CA",
        dea_schedules_covered=("II", "III", "IV", "V"),
        expires_on="2027-04-30",
    ),
    "lic_dea_basic": LicenseRecord(
        license_id="lic_dea_basic", type="dea", state="CA",
        dea_schedules_covered=("III", "IV", "V"),  # NO Schedule II
        expires_on="2026-09-15",
    ),
    "lic_state_acme": LicenseRecord(
        license_id="lic_state_acme", type="state-board", state="CA",
        dea_schedules_covered=(),
        expires_on="2026-12-31",
    ),
}


# Per-SKU lot expiry stub. Real implementation queries inventory by lot.
_LOT_DAYS_TO_EXPIRY: dict[str, int] = {
    "SKU-METF-500-100": 540,
    "SKU-LISI-10-90": 380,
    "SKU-AMOX-500-30": 25,    # close to expiry — should fire a WARNING
    "SKU-OXYC-5-100": 800,
    "SKU-INS-LANT-10": 95,
}


class DrugMaster:
    def lookup(self, sku_or_ndc: str) -> DrugRecord | None:
        if sku_or_ndc in _DRUGS:
            return _DRUGS[sku_or_ndc]
        for d in _DRUGS.values():
            if d.ndc == sku_or_ndc:
                return d
        return None


class LicenseRegistry:
    def get_many(self, license_ids: tuple[str, ...]) -> list[LicenseRecord]:
        return [_LICENSES[lid] for lid in license_ids if lid in _LICENSES]


class InventoryService:
    def days_to_expiry(self, sku: str, lot_id: str | None = None) -> int | None:
        return _LOT_DAYS_TO_EXPIRY.get(sku)
