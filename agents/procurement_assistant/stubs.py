"""Stub backends for the procurement assistant.

These are in-memory placeholders that match the shape of the real services
on the platform. Replace each class with the production client (catalog
service, supplier marketplace, cart service) without touching the agent.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Product:
    sku: str
    ndc: str
    generic_name: str
    brand_name: str | None
    strength: str
    dosage_form: str  # tablet, capsule, vial, etc.
    pack_size: int
    dea_schedule: str | None  # None for non-controlled
    requires_cold_chain: bool = False


@dataclass(frozen=True)
class SupplierOffer:
    supplier_id: str
    supplier_name: str
    sku: str
    unit_price: float
    min_order_qty: int
    in_stock_qty: int
    lead_time_days: int


_CATALOG: dict[str, Product] = {
    "SKU-METF-500-100": Product(
        sku="SKU-METF-500-100",
        ndc="00093-1048-01",
        generic_name="Metformin HCl",
        brand_name=None,
        strength="500 mg",
        dosage_form="tablet",
        pack_size=100,
        dea_schedule=None,
    ),
    "SKU-LISI-10-90": Product(
        sku="SKU-LISI-10-90",
        ndc="68180-0513-09",
        generic_name="Lisinopril",
        brand_name="Prinivil",
        strength="10 mg",
        dosage_form="tablet",
        pack_size=90,
        dea_schedule=None,
    ),
    "SKU-AMOX-500-30": Product(
        sku="SKU-AMOX-500-30",
        ndc="65862-0017-30",
        generic_name="Amoxicillin",
        brand_name="Amoxil",
        strength="500 mg",
        dosage_form="capsule",
        pack_size=30,
        dea_schedule=None,
    ),
    "SKU-OXYC-5-100": Product(
        sku="SKU-OXYC-5-100",
        ndc="00406-0552-01",
        generic_name="Oxycodone HCl",
        brand_name=None,
        strength="5 mg",
        dosage_form="tablet",
        pack_size=100,
        dea_schedule="II",
    ),
    "SKU-INS-LANT-10": Product(
        sku="SKU-INS-LANT-10",
        ndc="00088-2220-33",
        generic_name="Insulin glargine",
        brand_name="Lantus",
        strength="100 U/mL",
        dosage_form="vial 10 mL",
        pack_size=1,
        dea_schedule=None,
        requires_cold_chain=True,
    ),
}

_OFFERS: dict[str, list[SupplierOffer]] = {
    "SKU-METF-500-100": [
        SupplierOffer("sup_amerisource", "AmerisourceBergen", "SKU-METF-500-100",
                      unit_price=4.85, min_order_qty=10, in_stock_qty=2400, lead_time_days=2),
        SupplierOffer("sup_cardinal", "Cardinal Health", "SKU-METF-500-100",
                      unit_price=4.62, min_order_qty=24, in_stock_qty=900, lead_time_days=3),
        SupplierOffer("sup_mckesson", "McKesson", "SKU-METF-500-100",
                      unit_price=4.78, min_order_qty=12, in_stock_qty=1500, lead_time_days=2),
    ],
    "SKU-LISI-10-90": [
        SupplierOffer("sup_amerisource", "AmerisourceBergen", "SKU-LISI-10-90",
                      unit_price=3.10, min_order_qty=10, in_stock_qty=1800, lead_time_days=2),
        SupplierOffer("sup_cardinal", "Cardinal Health", "SKU-LISI-10-90",
                      unit_price=3.25, min_order_qty=20, in_stock_qty=600, lead_time_days=3),
    ],
    "SKU-AMOX-500-30": [
        SupplierOffer("sup_mckesson", "McKesson", "SKU-AMOX-500-30",
                      unit_price=8.40, min_order_qty=6, in_stock_qty=320, lead_time_days=2),
    ],
    "SKU-OXYC-5-100": [
        SupplierOffer("sup_amerisource", "AmerisourceBergen", "SKU-OXYC-5-100",
                      unit_price=22.10, min_order_qty=1, in_stock_qty=80, lead_time_days=5),
    ],
    "SKU-INS-LANT-10": [
        SupplierOffer("sup_cardinal", "Cardinal Health", "SKU-INS-LANT-10",
                      unit_price=98.50, min_order_qty=1, in_stock_qty=120, lead_time_days=4),
        SupplierOffer("sup_mckesson", "McKesson", "SKU-INS-LANT-10",
                      unit_price=101.20, min_order_qty=1, in_stock_qty=60, lead_time_days=3),
    ],
}

# Per-tenant formularies: which SKUs the tenant is approved to purchase.
_FORMULARIES: dict[str, set[str]] = {
    "form_default": {
        "SKU-METF-500-100",
        "SKU-LISI-10-90",
        "SKU-AMOX-500-30",
        "SKU-INS-LANT-10",
    },
    "form_acute_care": set(_CATALOG.keys()),  # everything, including controls
}


class CatalogService:
    """Read-only product catalog. Replace with the real catalog client."""

    def search(
        self,
        tenant_id: str,
        query: str,
        formulary_id: str | None,
        formulary_only: bool,
    ) -> list[Product]:
        q = query.lower()
        approved: set[str] | None = None
        if formulary_only and formulary_id:
            approved = _FORMULARIES.get(formulary_id, set())

        hits: list[Product] = []
        for product in _CATALOG.values():
            if approved is not None and product.sku not in approved:
                continue
            haystack = " ".join(
                filter(None, [
                    product.generic_name,
                    product.brand_name,
                    product.strength,
                    product.dosage_form,
                    product.sku,
                    product.ndc,
                ])
            ).lower()
            if q in haystack:
                hits.append(product)
        return hits

    def get(self, tenant_id: str, sku: str) -> Product | None:
        return _CATALOG.get(sku)


class SupplierService:
    """Aggregates supplier offers across the marketplace."""

    def offers_for(
        self,
        tenant_id: str,
        sku: str,
        qty: int,
    ) -> list[SupplierOffer]:
        offers = _OFFERS.get(sku, [])
        # Only return offers that can fulfill the requested qty.
        return [o for o in offers if o.in_stock_qty >= qty and qty >= o.min_order_qty]


@dataclass
class CartLine:
    sku: str
    qty: int
    supplier_id: str
    unit_price: float


@dataclass
class Cart:
    cart_id: str
    tenant_id: str
    lines: list[CartLine] = field(default_factory=list)

    @property
    def total(self) -> float:
        return round(sum(line.qty * line.unit_price for line in self.lines), 2)


class CartService:
    """Per-session cart store. Production swap: a row in `carts` table."""

    def __init__(self) -> None:
        self._carts: dict[str, Cart] = {}

    def open(self, tenant_id: str, cart_id: str) -> Cart:
        cart = self._carts.get(cart_id)
        if cart is None:
            cart = Cart(cart_id=cart_id, tenant_id=tenant_id)
            self._carts[cart_id] = cart
        return cart

    def add_line(
        self,
        cart_id: str,
        sku: str,
        qty: int,
        supplier_id: str,
        unit_price: float,
    ) -> Cart:
        cart = self._carts[cart_id]
        cart.lines.append(
            CartLine(sku=sku, qty=qty, supplier_id=supplier_id, unit_price=unit_price)
        )
        return cart
