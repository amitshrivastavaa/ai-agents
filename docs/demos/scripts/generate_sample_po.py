"""Generate a synthetic purchase-order PDF for the po_extractor demo.

Run once before recording the demo:

    pip install reportlab
    python docs/demos/scripts/generate_sample_po.py

Output: docs/demos/fixtures/sample_po.pdf

The PDF is gitignored (real vendor POs contain PII and shouldn't be
committed). This script is the canonical way to (re)generate the sample.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib import colors
except ImportError:
    print(
        "Error: reportlab is required. Install with: pip install reportlab",
        file=sys.stderr,
    )
    sys.exit(1)


OUTPUT = Path(__file__).resolve().parents[1] / "fixtures" / "sample_po.pdf"


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=LETTER,
        title="Sample Purchase Order",
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )
    styles = getSampleStyleSheet()
    body = []

    body.append(Paragraph("<b>PURCHASE ORDER</b>", styles["Title"]))
    body.append(Spacer(1, 0.15 * inch))

    header_data = [
        ["PO Number:", "PO-2026-0142", "Issue Date:", "2026-01-15"],
        ["Vendor:", "AmerisourceBergen", "Buyer:", "Acme Pharmacy LLC"],
        ["Vendor DEA:", "RA0123456", "Buyer DEA:", "BA9876543"],
        ["Terms:", "Net 30", "Delivery By:", "2026-01-29"],
    ]
    header_table = Table(header_data, colWidths=[1.1 * inch, 2.4 * inch, 1.0 * inch, 2.4 * inch])
    header_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    body.append(header_table)
    body.append(Spacer(1, 0.25 * inch))

    line_data = [
        ["Line", "NDC", "Description", "Qty", "UOM", "Unit Price", "Line Total"],
        ["1", "00093-1048-01", "Metformin HCl 500 mg tablet (100ct)",
         "10", "pack", "$4.85", "$48.50"],
        ["2", "68180-0513-09", "Lisinopril 10 mg tablet (90ct)",
         "6", "pack", "$3.10", "$18.60"],
        ["3", "65862-0017-30", "Amoxicillin 500 mg capsule (30ct)",
         "8", "pack", "$8.40", "$67.20"],
        ["4", "00088-2220-33", "Insulin glargine 100 U/mL vial 10 mL (Lantus)",
         "2", "vial", "$98.50", "$197.00"],
    ]
    line_table = Table(
        line_data,
        colWidths=[0.4 * inch, 1.2 * inch, 3.2 * inch, 0.5 * inch, 0.55 * inch, 0.85 * inch, 0.95 * inch],
    )
    line_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    body.append(line_table)
    body.append(Spacer(1, 0.2 * inch))

    totals_data = [
        ["", "Subtotal:", "$331.30"],
        ["", "Tax (0%):", "$0.00"],
        ["", "Shipping:", "$12.00"],
        ["", "Total (USD):", "$343.30"],
    ]
    totals = Table(totals_data, colWidths=[5.0 * inch, 1.2 * inch, 1.0 * inch])
    totals.setStyle(
        TableStyle(
            [
                ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("LINEABOVE", (1, -1), (-1, -1), 0.7, colors.black),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    body.append(totals)
    body.append(Spacer(1, 0.3 * inch))
    body.append(
        Paragraph(
            "<i>Synthetic sample document for demo purposes only. "
            "All vendor and DEA numbers are fictitious.</i>",
            styles["Italic"],
        )
    )

    doc.build(body)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build()
