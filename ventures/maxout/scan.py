"""CLI: scan a repo for real backlog work (and optionally run the autopilot).

    python -m ventures.maxout.scan                 # scan the current dir
    python -m ventures.maxout.scan labs            # scan a subtree
    python -m ventures.maxout.scan . --execute     # actually run claude per item
                                                   #   (needs your authenticated Max)
"""
from __future__ import annotations

import sys
from collections import Counter

from .model import CREDIT_USD
from .scanner import scan_repo


def report(items) -> str:
    by_kind = Counter(i.kind for i in items)
    credits = sum(i.est_credits for i in items)
    out = ["MAXOUT BACKLOG SCAN".center(60), "=" * 60]
    out.append(f"  {len(items)} items found · ~{credits} credits "
               f"(~${credits * CREDIT_USD:.0f} of capacity) to clear")
    out.append("")
    for kind, n in by_kind.most_common():
        c = sum(i.est_credits for i in items if i.kind == kind)
        out.append(f"    {kind:<10} {n:>4} items · ~{c} cr")
    out.append("")
    out.append("  Sample items")
    for i in items[:12]:
        out.append(f"    [{i.kind:<8}] {i.path}:{i.line}  {i.summary}")
    if len(items) > 12:
        out.append(f"    … and {len(items) - 12} more")
    return "\n".join(out)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root = next((a for a in argv if not a.startswith("-")), ".")
    items = scan_repo(root)
    print(report(items))
    if "--execute" in argv:
        from .runner import ClaudeCodeRunner
        runner = ClaudeCodeRunner(root, week="scan")
        tasks = runner.run_backlog(items, dry_run=False, budget_credits=1000)
        print(f"\n[--execute] ran {len(tasks)} item(s) via claude; review the maxout/* "
              f"branches and open PRs. (Needs your authenticated Claude Code Max.)")


if __name__ == "__main__":
    main()
