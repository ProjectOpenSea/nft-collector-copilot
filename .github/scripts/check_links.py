#!/usr/bin/env python3
"""Check that relative .md links in the template's docs resolve to real files.

Scans README.md, CONTRIBUTING.md, and every .md under workspace/ and .openclaw/.
Skips anchors, external URLs, and any path under skills/opensea/ (mounted at
deploy time, not in this repo).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
ROOTS = ["README.md", "CONTRIBUTING.md", "workspace", ".openclaw"]


def md_files() -> list[Path]:
    files: list[Path] = []
    for root in ROOTS:
        p = REPO / root
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            files.extend(p.rglob("*.md"))
    return files


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#"))


def main() -> int:
    broken: list[str] = []
    for md in md_files():
        text = md.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1).split("#", 1)[0]
            if not target or is_external(target):
                continue
            if target.startswith("skills/opensea/"):
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                rel = md.relative_to(REPO)
                broken.append(f"{rel} → {target}")

    if broken:
        print("Broken in-repo links:")
        for b in broken:
            print(f"  {b}")
        return 1
    print("markdown links OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
