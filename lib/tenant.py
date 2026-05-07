"""Multi-tenant context plumbed through every agent call.

The platform's auth/session layer hydrates a `TenantContext` per request and
hands it to the agent. Every tool that touches data must scope by
`tenant_id` — this object is the canonical place that scoping comes from.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TenantContext:
    """Identifies the tenant invoking an agent.

    Fields:
        tenant_id: Required. Pharmacy / hospital group / distributor ID.
        user_id: Optional. The acting user (for audit logs).
        license_ids: License numbers held by this tenant (DEA, state board,
            wholesaler licenses, etc.). Compliance checks use these.
        formulary_id: Optional. Approved-product list this tenant buys from.
    """

    tenant_id: str
    user_id: str | None = None
    license_ids: tuple[str, ...] = field(default_factory=tuple)
    formulary_id: str | None = None

    def require(self) -> None:
        if not self.tenant_id:
            raise ValueError("tenant_id is required")

    def to_log_fields(self) -> dict[str, str | None]:
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "formulary_id": self.formulary_id,
        }
