"""
procurement-assistant: a conversational catalog & cart-building agent.

A buyer (pharmacist, hospital procurement officer, etc.) describes what they
need in natural language; the agent searches the catalog, compares supplier
offers, and builds a draft cart. The platform's session layer hydrates the
tenant context — every tool call is scoped by `tenant_id`.

CLI:
    python -m agents.procurement_assistant.agent \\
        --tenant t_acme --formulary form_default \\
        "I need 500 units of metformin 500mg, lowest price"

    python -m agents.procurement_assistant.agent \\
        --tenant t_acme --interactive
"""
from __future__ import annotations

import argparse
import sys
import uuid

import anthropic

from lib.config import Config
from lib.llm import cached_system, run_tool_loop
from lib.logging import configure as configure_logging, get_logger
from lib.tenant import TenantContext

from .stubs import CartService, CatalogService, SupplierService
from .tools import TOOLS, ProcurementTools

LOG = get_logger("agents.procurement_assistant")

SYSTEM_PROMPT = """You are a procurement assistant for a pharmacy / hospital \
buyer using a multi-tenant pharma e-commerce platform. Your job is to help \
the buyer find products, compare supplier offers, and build a draft cart.

Behavior:
- Always search the catalog first; do not invent SKUs or NDCs.
- When the buyer specifies a strength or dosage form, prefer exact matches.
- Before adding a line to the cart, present the top 1-3 supplier offers and \
their extended price, and confirm the choice unless the buyer has already \
named a selection criterion (e.g. "lowest price", a specific supplier).
- Controlled substances (DEA schedule II-V) require extra care: surface the \
schedule prominently and remind the buyer that the compliance check will \
verify license coverage at checkout.
- Keep responses tight. After a successful add-to-cart, summarize what was \
added and the running cart total.

You only have access to the tenant scope provided. Do not ask for or accept \
tenant or license IDs from the user — those are bound by the platform."""


def build_agent_tools(tenant: TenantContext, cart_id: str) -> ProcurementTools:
    """Wire up backend services. Production: inject real clients here."""
    return ProcurementTools(
        tenant=tenant,
        cart_id=cart_id,
        catalog=CatalogService(),
        suppliers=SupplierService(),
        carts=CartService(),
    )


def run_once(
    client: anthropic.Anthropic,
    *,
    model: str,
    tenant: TenantContext,
    user_message: str,
    cart_id: str,
    messages: list[dict] | None = None,
    agent_tools: ProcurementTools | None = None,
) -> tuple[list[dict], ProcurementTools]:
    """Run a single user turn. Returns the updated message history and tools."""
    if agent_tools is None:
        agent_tools = build_agent_tools(tenant, cart_id)
    if messages is None:
        messages = []
    messages.append({"role": "user", "content": user_message})

    LOG.info(
        "agent.turn.start",
        extra={"ctx_tenant_id": tenant.tenant_id, "ctx_cart_id": cart_id},
    )

    run_tool_loop(
        client,
        model=model,
        system=cached_system(SYSTEM_PROMPT),
        tools=TOOLS,
        dispatch=agent_tools.dispatch,
        messages=messages,
        thinking={"type": "adaptive"},
        on_text=lambda text: print(text),
        on_tool_use=lambda name, args: LOG.info(
            "agent.tool_use",
            extra={
                "ctx_tenant_id": tenant.tenant_id,
                "ctx_cart_id": cart_id,
                "ctx_tool": name,
                "ctx_args": args,
            },
        ),
    )
    return messages, agent_tools


def main() -> int:
    parser = argparse.ArgumentParser(description="Procurement assistant agent")
    parser.add_argument("--tenant", required=True, help="Tenant ID")
    parser.add_argument("--user", help="Acting user ID (for audit)")
    parser.add_argument("--formulary", default="form_default", help="Formulary ID")
    parser.add_argument(
        "--interactive", action="store_true", help="Multi-turn REPL"
    )
    parser.add_argument(
        "message",
        nargs="?",
        help="Single-turn message (omit with --interactive).",
    )
    args = parser.parse_args()

    cfg = Config.from_env()
    configure_logging(cfg.log_level)
    tenant = TenantContext(
        tenant_id=args.tenant,
        user_id=args.user,
        formulary_id=args.formulary,
    )
    tenant.require()

    cart_id = f"cart_{uuid.uuid4().hex[:12]}"
    client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)

    if args.interactive:
        messages: list[dict] = []
        agent_tools: ProcurementTools | None = None
        print("Procurement assistant. Ctrl-D or empty line to exit.")
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                print()
                return 0
            if not line:
                return 0
            messages, agent_tools = run_once(
                client, model=cfg.default_model, tenant=tenant,
                user_message=line, cart_id=cart_id,
                messages=messages, agent_tools=agent_tools,
            )

    if not args.message:
        parser.error("provide a message or use --interactive")
    run_once(
        client, model=cfg.default_model, tenant=tenant,
        user_message=args.message, cart_id=cart_id,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
