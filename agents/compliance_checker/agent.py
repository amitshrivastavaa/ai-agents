"""
compliance-checker: regulatory guardrails on a draft cart.

Runs before checkout. Looks up each line against the drug master, validates
the tenant's licenses (DEA schedules, state board, expiry), checks lot
expiry, and produces a typed `ComplianceReport`. The platform uses
`overall_status` to decide whether checkout proceeds, requires acknowledgment,
or is blocked entirely.

CLI:
    python -m agents.compliance_checker.agent \\
        --tenant t_acme --license lic_dea_acme --license lic_state_acme \\
        --formulary form_acute_care --cart cart.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import anthropic

from lib.config import Config
from lib.llm import cached_system, run_tool_loop
from lib.logging import configure as configure_logging, get_logger
from lib.tenant import TenantContext

from .schema import CartForReview, ComplianceReport
from .stubs import DrugMaster, InventoryService, LicenseRegistry
from .tools import TOOLS, ComplianceTools

LOG = get_logger("agents.compliance_checker")

SYSTEM_PROMPT = """You are a pharma procurement compliance checker. Given a \
draft cart and the buyer's tenant context, evaluate each line against \
regulatory rules and produce a structured `ComplianceReport`.

Rules to apply, in order:

1. Drug record exists. If `lookup_drug` returns no record, emit a BLOCKER \
finding (`rule_id`: `unknown-drug`).
2. Controlled substance license. For any line whose `dea_schedule` is not \
null, call `check_license_coverage` for that schedule. If `covered` is \
false, emit a BLOCKER (`rule_id`: `controlled-substance-license`, citation: \
`21 CFR 1301.74`).
3. Basic license. Once per cart, call `check_license_coverage` with \
`dea_schedule: null` to confirm a state-board or DEA license is on file. If \
not, emit a BLOCKER (`rule_id`: `no-state-license`).
4. Formulary alignment. If the tenant's formulary is set and the line's \
`formularies` does not include it, emit a WARNING (`rule_id`: \
`formulary-not-approved`).
5. Expiry. Call `check_lot_expiry` for each SKU.
   * `< 30 days`: BLOCKER (`rule_id`: `expiry-30-days`).
   * `< 90 days`: WARNING (`rule_id`: `expiry-90-days`).
6. Cold chain. If `requires_cold_chain` is true, emit an INFO (`rule_id`: \
`cold-chain-required`) reminding the buyer to confirm refrigerated shipping.

Determine `overall_status`:
- `block` if any BLOCKER.
- `warn` if WARNINGs but no BLOCKERs.
- `pass` if only INFOs (or no findings).

Be exhaustive and precise. Cite the regulation in `citation` when one is \
named in the rules above. Keep `summary` short — one paragraph the buyer \
can read at checkout."""


def _build_user_message(cart: CartForReview, tenant: TenantContext) -> str:
    return (
        "Review this draft cart for compliance. Apply every rule.\n\n"
        f"<tenant>\n"
        f"tenant_id={tenant.tenant_id}\n"
        f"license_ids={list(tenant.license_ids)}\n"
        f"formulary_id={tenant.formulary_id}\n"
        f"</tenant>\n\n"
        f"<cart>\n{cart.model_dump_json(indent=2)}\n</cart>"
    )


def check(
    client: anthropic.Anthropic,
    *,
    model: str,
    tenant: TenantContext,
    cart: CartForReview,
) -> ComplianceReport:
    """Run the compliance check. Returns a validated `ComplianceReport`."""
    LOG.info(
        "check.start",
        extra={"ctx_tenant_id": tenant.tenant_id, "ctx_cart_id": cart.cart_id},
    )

    agent_tools = ComplianceTools(
        tenant=tenant,
        drugs=DrugMaster(),
        licenses=LicenseRegistry(),
        inventory=InventoryService(),
    )

    response = run_tool_loop(
        client,
        model=model,
        system=cached_system(SYSTEM_PROMPT),
        tools=TOOLS,
        dispatch=agent_tools.dispatch,
        messages=[{"role": "user", "content": _build_user_message(cart, tenant)}],
        thinking={"type": "adaptive"},
        output_config={
            "format": {
                "type": "json_schema",
                "schema": ComplianceReport.model_json_schema(),
            }
        },
        on_tool_use=lambda name, args: LOG.info(
            "check.tool_use",
            extra={
                "ctx_tenant_id": tenant.tenant_id,
                "ctx_cart_id": cart.cart_id,
                "ctx_tool": name,
                "ctx_args": args,
            },
        ),
    )

    text = next(
        (b.text for b in response.content if b.type == "text"),
        None,
    )
    if not text:
        raise RuntimeError(
            f"compliance check produced no text (stop_reason={response.stop_reason!r})"
        )
    report = ComplianceReport.model_validate_json(text)

    LOG.info(
        "check.done",
        extra={
            "ctx_tenant_id": tenant.tenant_id,
            "ctx_cart_id": cart.cart_id,
            "ctx_overall": report.overall_status,
            "ctx_finding_count": len(report.findings),
        },
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Compliance checker agent")
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--user", help="Acting user ID (for audit)")
    parser.add_argument(
        "--license", action="append", default=[],
        help="License ID. Repeatable.",
    )
    parser.add_argument("--formulary", help="Formulary ID for this tenant.")
    parser.add_argument(
        "--cart", type=Path, required=True, help="JSON file with the draft cart.",
    )
    args = parser.parse_args()

    cfg = Config.from_env()
    configure_logging(cfg.log_level)

    tenant = TenantContext(
        tenant_id=args.tenant,
        user_id=args.user,
        license_ids=tuple(args.license),
        formulary_id=args.formulary,
    )
    tenant.require()

    cart_data = json.loads(args.cart.read_text())
    cart = CartForReview.model_validate(cart_data)

    client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
    try:
        report = check(client, model=cfg.default_model, tenant=tenant, cart=cart)
    except Exception as exc:
        LOG.exception("check.failed")
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(report.model_dump(mode="json"), indent=2))
    # Exit code reflects status so CI / pipelines can gate on it.
    return {"pass": 0, "warn": 0, "block": 2}[report.overall_status]


if __name__ == "__main__":
    sys.exit(main())
