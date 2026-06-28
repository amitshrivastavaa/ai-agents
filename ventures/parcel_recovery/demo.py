"""Run the recovery audit on the built-in sample invoices and print a report."""
from __future__ import annotations

from .audit import audit, summarize
from .claims import CATEGORY_LABELS, filing_pack
from .sample_data import sample_shipments


def _bar(frac, width=20):
    n = int(round(frac * width))
    return "#" * n + "." * (width - n)


def render(shipments, contingency=0.25) -> str:
    claims = audit(shipments)
    s = summarize(shipments, claims, contingency)

    out = []
    out.append("PARCEL RECOVERY AUDIT".center(62))
    out.append("=" * 62)
    out.append(f"  {s['shipments']} shipments audited      ${s['total_billed']:,.2f} billed")
    out.append("")
    out.append(f"  RECOVERABLE:  ${s['total_recoverable']:,.2f}"
               f"   ({s['recovery_rate'] * 100:.1f}% of spend, {s['claim_count']} claims)")
    out.append("")
    out.append("  By category")
    for cat, d in sorted(s["by_category"].items(), key=lambda kv: -kv[1]["amount"]):
        frac = d["amount"] / s["total_recoverable"] if s["total_recoverable"] else 0
        out.append(f"    {CATEGORY_LABELS.get(cat, cat):<34} ${d['amount']:>8,.2f}  "
                   f"{_bar(frac)} x{d['count']}")
    out.append("")
    out.append("  Economics  (contingency: no recovery, no fee)")
    out.append(f"    Client keeps     ${s['client_net']:>9,.2f}   ({(1 - contingency) * 100:.0f}%)")
    out.append(f"    Your fee @ {contingency * 100:.0f}%    ${s['your_fee']:>9,.2f}")
    out.append("")
    out.append("-" * 62)
    out.append("FILING PACK  (submit before each deadline)")
    out.append("-" * 62)
    out.append(filing_pack(claims))
    return "\n".join(out)


def main():
    print(render(sample_shipments()))


if __name__ == "__main__":
    main()
