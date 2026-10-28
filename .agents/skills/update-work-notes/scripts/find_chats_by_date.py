#!/usr/bin/env python3
"""List Cursor agent-transcript files touched on a given local date.

Scans ~/.cursor/projects/*/agent-transcripts/*/*.jsonl (every project/repo the
user has opened in Cursor, not just the current one) and reports files whose
mtime falls on the requested date. Used by the update-work-notes skill
(SKILL.md) to find candidate chats to summarize for a Work Notes entry.

Usage:
    python3 find_chats_by_date.py 2026-08-10
    python3 find_chats_by_date.py 2026-08-10 --projects-root ~/.cursor/projects
"""
import argparse
import datetime as dt
import glob
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", help="Target date, YYYY-MM-DD, local time")
    parser.add_argument(
        "--projects-root",
        default=os.path.expanduser("~/.cursor/projects"),
        help="Root folder containing per-project transcript dirs",
    )
    args = parser.parse_args()

    try:
        target = dt.date.fromisoformat(args.date)
    except ValueError:
        print(f"error: '{args.date}' is not a valid YYYY-MM-DD date", file=sys.stderr)
        sys.exit(1)

    pattern = os.path.join(args.projects_root, "*", "agent-transcripts", "*", "*.jsonl")
    matches = []
    for path in glob.glob(pattern):
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        file_date = dt.datetime.fromtimestamp(mtime).date()
        if file_date == target:
            project = path.split(os.sep)[-4]  # .../<project>/agent-transcripts/<uuid>/<uuid>.jsonl
            matches.append((mtime, project, path))

    matches.sort()
    if not matches:
        print(f"No transcripts found for {target.isoformat()}")
        return

    for mtime, project, path in matches:
        ts = dt.datetime.fromtimestamp(mtime).strftime("%H:%M")
        size_kb = os.path.getsize(path) / 1024
        print(f"{ts}  {project:<45}  {size_kb:6.1f} KB  {path}")


if __name__ == "__main__":
    main()
