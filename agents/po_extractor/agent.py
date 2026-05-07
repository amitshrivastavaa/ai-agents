"""
po-extractor: extracts a structured PurchaseOrder from a PDF or image.

Buyers and vendors send purchase orders in every format imaginable — clean
PDFs from an ERP, scanned faxes, photos taken on a phone. This agent
normalizes them into a typed `PurchaseOrder` (see `schema.py`) so downstream
services (catalog matching, compliance, AP) can work against a single shape.

CLI:
    python -m agents.po_extractor.agent --tenant t_acme --pdf invoice.pdf
    python -m agents.po_extractor.agent --tenant t_acme --image scan.png
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
from pathlib import Path

import anthropic

from lib.config import Config
from lib.llm import cached_system
from lib.logging import configure as configure_logging, get_logger
from lib.tenant import TenantContext

from .schema import PurchaseOrder

LOG = get_logger("agents.po_extractor")

SYSTEM_PROMPT = """You extract structured purchase orders from documents in \
the pharma supply chain (PDFs, scans, photos). Produce a `PurchaseOrder` \
object that exactly matches the provided schema.

Rules:
- Copy values verbatim where the document is clear. Do not normalize formatting.
- Compute `line_total = qty * unit_price` and double-check `subtotal` and \
`total` against the document; if numbers disagree, prefer the printed total \
and flag the discrepancy in `notes`.
- For NDCs, accept any standard format (10- or 11-digit, hyphenated or not). \
Set `ndc` to null if no code is present.
- Set `extraction_confidence`:
  * `high`: clean document, every required field unambiguous.
  * `medium`: minor ambiguities (a date format, a missing UOM).
  * `low`: scan quality is poor, fields are missing, or you had to infer key \
values. Always include a `notes` field at low confidence.
- Never hallucinate vendor or DEA numbers. If a field isn't present, leave it \
null.

You will receive the document followed by no further questions. Return only \
the structured object."""

PROMPT_INSTRUCTION = (
    "Extract this purchase order. Validate totals and report any discrepancies "
    "in `notes`."
)


def _load_document_block(path: Path) -> dict:
    mime, _ = mimetypes.guess_type(str(path))
    data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    if mime == "application/pdf" or path.suffix.lower() == ".pdf":
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": data,
            },
        }
    if mime in {"image/png", "image/jpeg", "image/gif", "image/webp"}:
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": mime, "data": data},
        }
    raise ValueError(
        f"unsupported file type for {path.name!r} (mime={mime!r}); "
        "use a PDF or PNG/JPEG/GIF/WebP image"
    )


def extract(
    client: anthropic.Anthropic,
    *,
    model: str,
    tenant: TenantContext,
    document_path: Path,
) -> PurchaseOrder:
    """Run the extraction. Returns a validated `PurchaseOrder`."""
    LOG.info(
        "extract.start",
        extra={
            "ctx_tenant_id": tenant.tenant_id,
            "ctx_path": str(document_path),
        },
    )

    response = client.messages.parse(
        model=model,
        max_tokens=8000,
        system=cached_system(SYSTEM_PROMPT),
        messages=[
            {
                "role": "user",
                "content": [
                    _load_document_block(document_path),
                    {"type": "text", "text": PROMPT_INSTRUCTION},
                ],
            }
        ],
        output_format=PurchaseOrder,
    )

    if response.parsed_output is None:
        raise RuntimeError(
            f"extraction failed (stop_reason={response.stop_reason!r})"
        )

    LOG.info(
        "extract.done",
        extra={
            "ctx_tenant_id": tenant.tenant_id,
            "ctx_po_number": response.parsed_output.po_number,
            "ctx_confidence": response.parsed_output.extraction_confidence,
            "ctx_input_tokens": response.usage.input_tokens,
            "ctx_output_tokens": response.usage.output_tokens,
        },
    )
    return response.parsed_output


def main() -> int:
    parser = argparse.ArgumentParser(description="PO extractor agent")
    parser.add_argument("--tenant", required=True, help="Tenant ID")
    parser.add_argument("--user", help="Acting user ID (for audit)")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pdf", type=Path, help="Path to a PDF PO.")
    source.add_argument("--image", type=Path, help="Path to an image PO.")
    args = parser.parse_args()

    cfg = Config.from_env()
    configure_logging(cfg.log_level)
    tenant = TenantContext(tenant_id=args.tenant, user_id=args.user)
    tenant.require()

    document_path = args.pdf or args.image
    if not document_path.is_file():
        print(f"Error: {document_path} is not a file.", file=sys.stderr)
        return 1

    client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
    try:
        po = extract(
            client, model=cfg.default_model, tenant=tenant,
            document_path=document_path,
        )
    except Exception as exc:
        LOG.exception("extract.failed")
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(po.model_dump(mode="json"), indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
