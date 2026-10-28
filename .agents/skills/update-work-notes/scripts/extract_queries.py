#!/usr/bin/env python3
"""
extract_queries.py

Pulls a one-line summary out of every Cursor transcript so a whole month of
work can be reconstructed without reading each chat in full.

For each transcript it emits: ISO date, project name, and the first
<user_query> (the opening request, which is the best short label for what the
chat was about).

The date comes from the <timestamp> tag inside the first user message, not the
file mtime -- mtime shifts when a chat is resumed later.

Referenced by: update-work-notes/SKILL.md (Step 2, backfill).
Used to backfill <vault>/Work Notes/.

Usage:
  python3 extract_queries.py 2026-02 2026-03 ...
  python3 extract_queries.py --all
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECTS = Path.home() / ".cursor" / "projects"
# Cursor names project dirs after the opened folder path with "/" -> "-",
# e.g. "Users-alice-code-myrepo". Anything under the home dir starts with this.
HOME_SLUG = str(Path.home()).strip("/").replace("/", "-") + "-"

TIMESTAMP_RE = re.compile(r"<timestamp>(.*?)</timestamp>", re.S)
QUERY_RE = re.compile(r"<user_query>(.*?)</user_query>", re.S)

# Cursor writes timestamps like "Monday, Jun 29, 2026, 5:50 PM (UTC-6)".
TS_FORMAT = "%A, %b %d, %Y, %I:%M %p"


def parse_timestamp(raw: str):
    cleaned = re.sub(r"\s*\(UTC[^)]*\)", "", raw).strip()
    try:
        return datetime.strptime(cleaned, TS_FORMAT).date().isoformat()
    except ValueError:
        return None


def project_name(path: Path) -> str:
    """Project dir is either a readable path slug or an opaque numeric id."""
    for part in path.parts:
        if part.startswith(HOME_SLUG):
            return part.rsplit("-", 1)[-1]
    if "empty-window" in path.parts:
        return "adhoc"
    return "other"


# Older transcripts (pre-~Apr 2026) inline context -- git diffs, attached files,
# rules -- into the same user message as the real request, and have no
# <timestamp> tag. Strip these wrappers so the leftover text is the human ask.
CONTEXT_TAGS = (
    "git_diff_from_branch_to_main",
    "attached_files",
    "system_reminder",
    "additional_data",
    "current_file",
    "linter_errors",
    "rules",
)


def strip_context(text: str) -> str:
    for tag in CONTEXT_TAGS:
        text = re.sub(rf"<{tag}>.*?</{tag}>", " ", text, flags=re.S)
        # Unclosed wrappers are common in truncated transcripts.
        text = re.sub(rf"<{tag}>.*", " ", text, flags=re.S)
    return " ".join(text.split())


def first_query(jsonl: Path):
    """Scan user messages for the human request. Falls back to mtime for date."""
    date = None
    fallback = None
    with jsonl.open(errors="ignore") as handle:
        for line in handle:
            if '"role":"user"' not in line and '"role": "user"' not in line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = entry.get("message", {}).get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") != "text":
                    continue
                text = block.get("text", "")
                if date is None:
                    match = TIMESTAMP_RE.search(text)
                    if match:
                        date = parse_timestamp(match.group(1))
                match = QUERY_RE.search(text)
                if match:
                    return date, " ".join(match.group(1).split())
                if fallback is None:
                    stripped = strip_context(text)
                    # Very short leftovers are usually tag debris, not a request.
                    if len(stripped) > 15:
                        fallback = stripped
    return date, fallback


def main() -> None:
    args = sys.argv[1:]
    wanted = None if args == ["--all"] else set(args)

    rows = []
    for jsonl in PROJECTS.glob("*/agent-transcripts/*/*.jsonl"):
        date, query = first_query(jsonl)
        if not query:
            continue
        if not date:
            date = datetime.fromtimestamp(jsonl.stat().st_mtime).date().isoformat()
        if wanted is not None and date[:7] not in wanted:
            continue
        rows.append((date, project_name(jsonl), query[:220]))

    for date, project, query in sorted(rows):
        print(f"{date}\t{project}\t{query}")


if __name__ == "__main__":
    main()
