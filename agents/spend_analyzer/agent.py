"""
spend-analyzer: code-execution-driven analysis of a tenant's purchase history.

Takes a CSV of historical purchases (typical columns: po_date, sku,
generic_name, qty, unit_price, supplier_id, dea_schedule), uploads it to the
Anthropic code-execution sandbox, and asks Claude to:

* surface top spend categories and supplier concentration
* flag anomalies (unit-price spikes, supplier price drift, single-sourced SKUs)
* recommend savings (generic substitution, supplier consolidation, MOQ tuning)
* generate one or two charts as PNG attachments

Generated artifacts (charts, summary CSVs) are downloaded into
``--output-dir`` (defaults to ``./reports/<tenant_id>/``).

CLI:
    python -m agents.spend_analyzer.agent --tenant t_acme --csv history.csv
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import anthropic

from lib.config import Config
from lib.logging import configure as configure_logging, get_logger
from lib.tenant import TenantContext

LOG = get_logger("agents.spend_analyzer")

SYSTEM_PROMPT = """You are a procurement analytics agent for a multi-tenant \
pharma e-commerce platform. The user gives you a CSV of one tenant's purchase \
history. You have a Python sandbox via the `code_execution` tool.

Workflow:

1. Load the CSV with pandas. Print the column list and row count so the user \
can sanity-check the file.
2. Compute total spend, top 10 SKUs by spend, and supplier concentration \
(share of spend per supplier).
3. Identify anomalies:
   * Same SKU+supplier where unit price increased >15% in the trailing window.
   * SKUs with 100% spend on a single supplier (single-source risk).
   * Outlier unit prices vs. tenant median for that SKU.
4. Recommend savings. Be concrete: name the SKU, name the action (e.g. \
"consolidate to McKesson at $4.62 unit, save ~$580 annual"), and show the \
math.
5. Produce one or two charts (matplotlib): a top-spend bar chart and a \
supplier-share donut or bar. Save as PNG.
6. End with a short markdown summary the buyer can paste into a board memo.

Be precise with numbers (use round() to 2 decimals). Don't fabricate data — \
if a column is missing, say so and skip the dependent analysis. Keep code \
blocks compact; explain results in prose between them."""


def analyze(
    client: anthropic.Anthropic,
    *,
    model: str,
    tenant: TenantContext,
    csv_path: Path,
    output_dir: Path,
) -> None:
    """Run the analysis and stream output to stdout. Save artifacts to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)

    LOG.info(
        "analyze.start",
        extra={
            "ctx_tenant_id": tenant.tenant_id,
            "ctx_csv": str(csv_path),
            "ctx_output_dir": str(output_dir),
        },
    )

    uploaded = client.beta.files.upload(
        file=(csv_path.name, csv_path.read_bytes(), "text/csv"),
    )
    LOG.info(
        "analyze.upload",
        extra={"ctx_tenant_id": tenant.tenant_id, "ctx_file_id": uploaded.id},
    )

    user_text = (
        f"Analyze this tenant's purchase history. Tenant: {tenant.tenant_id}.\n\n"
        "Follow the workflow in your instructions. Save chart PNGs to the "
        "current directory so they can be downloaded."
    )

    response = client.messages.create(
        model=model,
        max_tokens=16000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "container_upload", "file_id": uploaded.id},
                ],
            }
        ],
        tools=[{"type": "code_execution_20260120", "name": "code_execution"}],
        extra_headers={"anthropic-beta": "files-api-2025-04-14"},
    )

    artifact_ids: list[str] = []
    for block in response.content:
        btype = block.type
        if btype == "text":
            print(block.text)
        elif btype == "server_tool_use":
            LOG.info(
                "analyze.code_run",
                extra={
                    "ctx_tenant_id": tenant.tenant_id,
                    "ctx_tool": block.name,
                },
            )
        elif btype == "bash_code_execution_tool_result":
            result = block.content
            if getattr(result, "type", None) == "bash_code_execution_result":
                if result.return_code != 0 and result.stderr:
                    print(f"[stderr]\n{result.stderr}", file=sys.stderr)
                # Collect any file outputs the sandbox produced.
                for entry in (result.content or []):
                    if getattr(entry, "type", None) == "bash_code_execution_output":
                        artifact_ids.append(entry.file_id)
        elif btype == "text_editor_code_execution_tool_result":
            # File operations from the text_editor sub-tool also surface
            # generated files via file_id; capture them too.
            inner = getattr(block, "content", None)
            for entry in getattr(inner, "content", []) or []:
                fid = getattr(entry, "file_id", None)
                if fid:
                    artifact_ids.append(fid)

    saved = _download_artifacts(client, artifact_ids, output_dir)
    if saved:
        print("\nSaved artifacts:")
        for path in saved:
            print(f"  {path}")

    LOG.info(
        "analyze.done",
        extra={
            "ctx_tenant_id": tenant.tenant_id,
            "ctx_artifacts": len(saved),
            "ctx_input_tokens": response.usage.input_tokens,
            "ctx_output_tokens": response.usage.output_tokens,
        },
    )


def _download_artifacts(
    client: anthropic.Anthropic,
    file_ids: list[str],
    output_dir: Path,
) -> list[Path]:
    saved: list[Path] = []
    for file_id in dict.fromkeys(file_ids):  # de-dupe, preserve order
        try:
            metadata = client.beta.files.retrieve_metadata(file_id)
            content = client.beta.files.download(file_id)
        except anthropic.APIError as exc:
            LOG.warning(
                "analyze.artifact_download_failed",
                extra={"ctx_file_id": file_id, "ctx_error": str(exc)},
            )
            continue
        # Sanitize filename to prevent path traversal.
        safe_name = os.path.basename(metadata.filename or file_id)
        if not safe_name or safe_name in {".", ".."}:
            LOG.warning(
                "analyze.artifact_skipped",
                extra={"ctx_file_id": file_id, "ctx_filename": metadata.filename},
            )
            continue
        target = output_dir / safe_name
        content.write_to_file(str(target))
        saved.append(target)
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Spend analyzer agent")
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--user", help="Acting user ID (for audit)")
    parser.add_argument(
        "--csv", type=Path, required=True,
        help="CSV of purchase history (one row per line item).",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        help="Where to save generated charts. Default: ./reports/<tenant_id>/",
    )
    args = parser.parse_args()

    cfg = Config.from_env()
    configure_logging(cfg.log_level)

    tenant = TenantContext(tenant_id=args.tenant, user_id=args.user)
    tenant.require()

    if not args.csv.is_file():
        print(f"Error: {args.csv} is not a file.", file=sys.stderr)
        return 1

    output_dir = args.output_dir or (Path("reports") / tenant.tenant_id)
    client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)

    try:
        analyze(
            client, model=cfg.default_model, tenant=tenant,
            csv_path=args.csv, output_dir=output_dir,
        )
    except Exception as exc:
        LOG.exception("analyze.failed")
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
