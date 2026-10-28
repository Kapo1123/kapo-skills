#!/usr/bin/env python3
"""Print a condensed, noise-stripped transcript of a Cursor chat .jsonl file.

Each line in a transcript file is one JSON object shaped like
{"role": "user"|"assistant", "message": {"content": [...]}} or a control
event like {"type": "turn_ended", ...}. "text" content blocks carry the
actual conversation; "tool_use" blocks only carry a tool name + input.

Raw transcripts are dominated by injected system context (rules, attached
skills, file lists, etc.) wrapped in tags like <system_reminder>...</...>.
That boilerplate repeats on every user turn and is not useful for summarizing
"what did I work on today", so this script strips any XML-ish tag block
whose inner content is longer than --strip-threshold characters, on the
assumption that real conversation text rarely contains long custom tags.

Used by the update-work-notes skill (SKILL.md) as a pre-processing step
before an agent reads and summarizes a day's chats.

Usage:
    python3 dump_chat_text.py /path/to/chat.jsonl
    python3 dump_chat_text.py /path/to/chat.jsonl --max-chars 8000
"""
import argparse
import json
import re
import sys

NOISE_TAG_RE = re.compile(r"<([a-zA-Z][\w-]*)>([\s\S]*?)</\1>")


def strip_noise(text: str, threshold: int) -> str:
    def _replace(m: "re.Match[str]") -> str:
        tag, inner = m.group(1), m.group(2)
        if len(inner) > threshold:
            return f"[stripped injected context: <{tag}>]"
        return m.group(0)

    # Run twice to catch tags nested one level inside a block that itself
    # was just under the threshold (rare, cheap to just repeat).
    text = NOISE_TAG_RE.sub(_replace, text)
    text = NOISE_TAG_RE.sub(_replace, text)
    return text


def render_line(entry: dict, threshold: int) -> str | None:
    role = entry.get("role")
    if role not in ("user", "assistant"):
        return None
    content = entry.get("message", {}).get("content")
    if not isinstance(content, list):
        return None

    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype == "text":
            cleaned = strip_noise(block.get("text", ""), threshold).strip()
            if cleaned:
                parts.append(cleaned)
        elif btype == "tool_use":
            name = block.get("name", "?")
            parts.append(f"[tool: {name}]")

    if not parts:
        return None
    return f"### {role}\n" + "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Path to a transcript .jsonl file")
    parser.add_argument(
        "--strip-threshold",
        type=int,
        default=400,
        help="Strip <tag>...</tag> blocks longer than this many chars (default 400)",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=8000,
        help="Cap output length; keeps head and tail if exceeded (default 8000)",
    )
    args = parser.parse_args()

    rendered = []
    with open(args.path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            piece = render_line(entry, args.strip_threshold)
            if piece:
                rendered.append(piece)

    full_text = "\n\n".join(rendered)
    if len(full_text) > args.max_chars:
        head = full_text[: args.max_chars // 2]
        tail = full_text[-args.max_chars // 2 :]
        full_text = f"{head}\n\n...[truncated middle]...\n\n{tail}"

    print(full_text if full_text else "(no readable text content in this transcript)")


if __name__ == "__main__":
    main()
