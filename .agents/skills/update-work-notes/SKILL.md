---
name: update-work-notes
description: Gather a day's meetings (from Google Drive meeting notes) and a summary of Cursor chat activity across all projects, then draft and write an entry into the Obsidian vault's Work Notes/<Month Year>.md daily log. Use when the user asks to update work notes, log today's work, fill in a daily/work report, or write a work journal entry.
disable-model-invocation: false
---

# Update Work Notes

Compiles a Work Notes entry from two sources — meeting notes in Google Drive
and Cursor chat transcripts — then writes it into the vault following the
format rules in the vault's `README.md` (if it has one).

## Setup (once per person)

- **Vault path**: read it from the `WORK_NOTES_VAULT` environment variable.
  If it is not set, ask the user for the path to their Obsidian vault and
  suggest they set the variable. Entries go under `<vault>/Work Notes/`.
- **Google account**: use whichever Google Drive tool is connected, signed in
  with the user's work account. Do not guess or switch accounts; if no Drive
  tool is connected, skip Step 1 and say so in the draft.
- **Skipped meetings** (optional): the user may list recurring meetings they
  never want logged (for example a daily standup). Respect that list.

## Step 0: Determine the target date

Default to today. If the user says "yesterday" or names a date/day, use that
instead. You need:
- `date_iso` (e.g. `2026-08-10`) — for querying sources
- `day_heading` (e.g. `August 10`) — for the `##` section
- `month_file` (e.g. `August 2026.md`) — the file under `Work Notes/`

## Step 1: Gather meetings (Google Drive)

Meeting notes usually live as Google Docs (for example Gemini
"Notes by Gemini" exports such as
`Weekly sync - 2026/09/30 10:29 MDT - Notes by Gemini`).

1. Search Drive for Google Docs modified on `date_iso`:
   - mime type `application/vnd.google-apps.document`
   - modified between `<date_iso>T00:00:00` and `<date_iso>T23:59:59` in the
     user's local UTC offset
   - about 30 results, newest first
2. For each result, use judgement on the title to decide if it looks like a
   meeting note (attendee names, "1:1", "sync", meeting-tool naming patterns
   like Gemini/Granola/Otter exports, etc.) — skip obvious non-meeting docs
   (specs, PRDs the user is just editing, unrelated files).
3. Skip any meetings on the user's skip list (see Setup).
4. For remaining plausible candidates, read the file and confirm it's
   actually meeting notes. Gemini docs put "Quick notes", "Next steps",
   "Decisions" and "Details" at the top and a long image/transcript tail at
   the bottom, so reading the first ~30,000 characters is usually enough. If
   the harness writes a large result to a file, read the `content` field
   from that file instead of re-fetching. A tiny (~3–4 KB) doc whose summary
   says "A summary wasn't produced" is an empty session — skip it.
5. Extract one short bullet per meeting: meeting name + one-line gist (topic
   or key outcome, not a full recap).

If the Drive search fails or comes back empty, skip this step and note in the
draft that meetings weren't checked.

## Step 2: Gather Cursor chat activity (all projects)

Cursor chats are not scoped to the current repo — scan every project the
user has opened, since Work Notes covers all work, not just this codebase.
Scripts live in this skill's `scripts/` folder.

1. Run:

```bash
python3 <skill-dir>/scripts/find_chats_by_date.py <date_iso>
```

   This lists every transcript `.jsonl` file (across all `~/.cursor/projects/*`)
   touched on that date, with project name, size, and path.

2. Skip trivial ones (a few KB, likely a one-off or aborted chat) unless the
   list is short. For the rest, condense each with:

```bash
python3 <skill-dir>/scripts/dump_chat_text.py <path> --max-chars 6000
```

   This strips injected system context (rules, attached files, skills, etc.)
   and returns just the user/assistant text plus tool names used, so you can
   read it directly instead of the raw JSONL.

3. For each chat, write one short bullet: what was worked on (feature, bug,
   investigation, PR), naming the project when it's not obvious from context.
   Merge multiple chats about the same task into a single bullet.

To backfill a whole month, `scripts/extract_queries.py <YYYY-MM>` prints one
line per chat (date, project, opening request).

## Step 3: Draft and confirm

Compile Steps 1 and 2 into Work Notes format and show it to the user before
writing anything:

```
## <day_heading>
- <meeting bullet(s)>
- <work bullet(s)>
```

Follow the vault's content rules: one line per item, short and concrete, no
secrets/credentials, no long recaps — this is a scan-later log, not a report.
Let the user edit, add blockers/ideas they know about that you can't see
(e.g. Slack-only conversations), or drop bullets before writing.

## Step 4: Write

Once confirmed, edit `Work Notes/<month_file>` in the vault:
- If the file doesn't exist, create it with the H1 title (`# <Month Year> Work Notes`) and a blank line first.
- If a `##` section for `day_heading` already exists, append new bullets under it (don't duplicate/rewrite existing ones).
- Otherwise, add a new `##` section at the end, separated from the previous day by a blank line.
- Never touch other days' sections.
