"""Tool definitions and executors for the procurement assistant.

Tool inputs are validated against the JSON schemas Anthropic enforces; the
executor is the small Python adapter that turns the parsed input into a
backend call and serializes the result.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from lib.tenant import TenantContext

from .stubs import CartService, CatalogService, SupplierService


SEARCH_CATALOG = {
    "name": "search_catalog",
    "description": (
        "Search the product catalog by free-text query (matches generic name, "
        "brand name, strength, dosage form, SKU, or NDC). Returns up to 10 "
        "matching products. Set `formulary_only` to restrict to the tenant's "
        "approved formulary."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "formulary_only": {"type": "boolean", "default": False},
        },
        "required": ["query"],
    },
}

GET_PRODUCT = {
    "name": "get_product_details",
    "description": "Look up a single product by SKU.",
    "input_schema": {
        "type": "object",
        "properties": {"sku": {"type": "string"}},
        "required": ["sku"],
    },
}

COMPARE_SUPPLIERS = {
    "name": "compare_suppliers",
    "description": (
        "Return supplier offers for a SKU at the given quantity. Filters to "
        "suppliers that can actually fulfill the order (in stock, meets MOQ)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sku": {"type": "string"},
            "qty": {"type": "integer", "minimum": 1},
        },
        "required": ["sku", "qty"],
    },
}

ADD_TO_CART = {
    "name": "add_to_cart",
    "description": (
        "Add a line to the buyer's draft cart. Use this only after confirming "
        "the supplier choice with the user (e.g. they asked for 'lowest "
        "price' or named a specific supplier)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sku": {"type": "string"},
            "qty": {"type": "integer", "minimum": 1},
            "supplier_id": {"type": "string"},
        },
        "required": ["sku", "qty", "supplier_id"],
    },
}

VIEW_CART = {
    "name": "view_cart",
    "description": "Return the current draft cart for this session.",
    "input_schema": {"type": "object", "properties": {}},
}


TOOLS = [SEARCH_CATALOG, GET_PRODUCT, COMPARE_SUPPLIERS, ADD_TO_CART, VIEW_CART]


class ProcurementTools:
    """Glue layer between tool calls and the backend services.

    Tenant context is bound at construction time so we never trust a
    `tenant_id` arriving from the model — it always comes from the platform.
    """

    def __init__(
        self,
        tenant: TenantContext,
        cart_id: str,
        catalog: CatalogService,
        suppliers: SupplierService,
        carts: CartService,
    ) -> None:
        self.tenant = tenant
        self.cart_id = cart_id
        self.catalog = catalog
        self.suppliers = suppliers
        self.carts = carts
        # Make sure the cart exists for this session.
        self.carts.open(tenant.tenant_id, cart_id)

    def dispatch(self, name: str, args: dict[str, Any]) -> str:
        if name == "search_catalog":
            return self._search_catalog(**args)
        if name == "get_product_details":
            return self._get_product(args["sku"])
        if name == "compare_suppliers":
            return self._compare_suppliers(args["sku"], args["qty"])
        if name == "add_to_cart":
            return self._add_to_cart(args["sku"], args["qty"], args["supplier_id"])
        if name == "view_cart":
            return self._view_cart()
        return _err(f"unknown tool {name!r}")

    def _search_catalog(self, query: str, formulary_only: bool = False) -> str:
        hits = self.catalog.search(
            self.tenant.tenant_id,
            query,
            self.tenant.formulary_id,
            formulary_only,
        )
        return _ok({"products": [asdict(p) for p in hits[:10]]})

    def _get_product(self, sku: str) -> str:
        product = self.catalog.get(self.tenant.tenant_id, sku)
        if product is None:
            return _err(f"sku {sku!r} not found")
        return _ok(asdict(product))

    def _compare_suppliers(self, sku: str, qty: int) -> str:
        offers = self.suppliers.offers_for(self.tenant.tenant_id, sku, qty)
        if not offers:
            return _ok({"offers": [], "note": "no supplier can fulfill this qty"})
        offers_sorted = sorted(offers, key=lambda o: o.unit_price)
        return _ok(
            {
                "qty": qty,
                "offers": [
                    {**asdict(o), "extended_price": round(o.unit_price * qty, 2)}
                    for o in offers_sorted
                ],
            }
        )

    def _add_to_cart(self, sku: str, qty: int, supplier_id: str) -> str:
        offers = self.suppliers.offers_for(self.tenant.tenant_id, sku, qty)
        match = next((o for o in offers if o.supplier_id == supplier_id), None)
        if match is None:
            return _err(
                f"supplier {supplier_id!r} cannot fulfill {qty} of {sku!r}"
            )
        cart = self.carts.add_line(
            self.cart_id, sku=sku, qty=qty, supplier_id=supplier_id,
            unit_price=match.unit_price,
        )
        return _ok({"cart": _serialize_cart(cart), "added_line_index": len(cart.lines) - 1})

    def _view_cart(self) -> str:
        cart = self.carts.open(self.tenant.tenant_id, self.cart_id)
        return _ok({"cart": _serialize_cart(cart)})


def _serialize_cart(cart: Any) -> dict:
    return {
        "cart_id": cart.cart_id,
        "tenant_id": cart.tenant_id,
        "lines": [asdict(line) for line in cart.lines],
        "total": cart.total,
    }


def _ok(payload: dict) -> str:
    return json.dumps({"ok": True, **payload}, default=str)


def _err(message: str) -> str:
    return json.dumps({"ok": False, "error": message})
