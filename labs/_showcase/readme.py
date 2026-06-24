"""Parse the labs/README.md MVP table into per-lab metadata.

Table rows look like:

    | [`agent_swarm`](agent_swarm/) | A panel of agents ... | the viral *Trading* ... |

We pull the lab name (the link target), the "What it is" column (tagline), and
the "Inspired by" column. Header, separator, and prose lines are ignored.
"""
from __future__ import annotations

import re

# | [`name`](name/) | tagline | inspired_by |
_ROW = re.compile(r"^\|\s*\[`?([a-z0-9_]+)`?\]\([a-z0-9_]+/\)\s*\|(.*)\|(.*)\|\s*$")


def parse_readme(text: str) -> dict[str, dict[str, str]]:
    """Map lab name -> {'tagline', 'inspired_by'} from the README MVP table."""
    out: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        m = _ROW.match(line.strip())
        if not m:
            continue
        name, tagline, inspired = m.group(1), m.group(2), m.group(3)
        out[name] = {
            "tagline": tagline.strip(),
            "inspired_by": inspired.strip(),
        }
    return out
