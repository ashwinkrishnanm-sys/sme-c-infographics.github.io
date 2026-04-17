#!/usr/bin/env python3
"""
Ensures the Umami analytics tracking snippet is present in every HTML
page in the repository. Idempotent: if the snippet (identified by its
data-website-id) is already present, the file is left unchanged.

Redirect stubs (pages using <meta http-equiv="refresh">) are skipped
since the tracking script would not have time to load.

Inserts the snippet on its own line immediately before </head>,
matching the indentation of the </head> line.
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WEBSITE_ID = "9478c1a0-93c6-4c21-855a-69e50e15cbc4"
SNIPPET = (
    f'<script defer src="https://a.ndme.sh/script.js" '
    f'data-website-id="{WEBSITE_ID}"></script>'
)

HEAD_CLOSE_RE = re.compile(r"^(?P<indent>[ \t]*)</head>", re.MULTILINE)
META_REFRESH_RE = re.compile(
    r'<meta\s+http-equiv=["\']refresh["\']', re.IGNORECASE
)
# Skip workflow/build output directories.
SKIP_DIRS = {".git", "node_modules", ".github"}


def iter_html_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if fname.lower().endswith(".html"):
                yield os.path.join(dirpath, fname)


def ensure_snippet(filepath: str) -> str:
    """Return 'added', 'present', 'skipped', or 'nohead'."""
    with open(filepath, encoding="utf-8") as fh:
        content = fh.read()

    if META_REFRESH_RE.search(content):
        return "skipped"

    if WEBSITE_ID in content:
        return "present"

    match = HEAD_CLOSE_RE.search(content)
    if not match:
        return "nohead"

    indent = match.group("indent")
    insertion = f"{indent}{SNIPPET}\n"
    new_content = content[: match.start()] + insertion + content[match.start() :]

    with open(filepath, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_content)
    return "added"


def main() -> int:
    totals = {"added": [], "present": [], "skipped": [], "nohead": []}
    for filepath in sorted(iter_html_files(REPO_ROOT)):
        rel = os.path.relpath(filepath, REPO_ROOT).replace(os.sep, "/")
        status = ensure_snippet(filepath)
        totals[status].append(rel)

    for status, label in (
        ("added", "Added snippet"),
        ("present", "Already present"),
        ("skipped", "Skipped (redirect)"),
        ("nohead", "No </head> found"),
    ):
        files = totals[status]
        print(f"{label}: {len(files)}")
        for f in files:
            print(f"  - {f}")

    if totals["nohead"]:
        print("ERROR: one or more HTML files have no </head> tag.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
