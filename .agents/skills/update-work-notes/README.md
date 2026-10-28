# update-work-notes

Writes a daily entry into an Obsidian vault's `Work Notes/<Month Year>.md`
log. It pulls the day's meetings from Google Drive meeting notes and a
summary of your Cursor chats across every project, shows you the draft, and
writes only after you confirm.

> Agent instructions: [SKILL.md](SKILL.md).

## Setup

Ask the agent: **"Install the update-work-notes skill"**. Try it in this
tab. Open a new tab only if it is not picked up.

If the agent does not know how, set up the skill manager first. See
[Install](../../../README.md#install) in the repo root.

Then:

- Set your vault path: `export WORK_NOTES_VAULT="/path/to/your/vault"` in
  your shell profile. If it is not set, the agent asks for it.
- Connect a Google Drive tool signed in with your work account. Without it,
  meetings are skipped and the draft says so.
- Optional: tell the agent which recurring meetings never to log.

Scripts need Python 3.10 or later, as `python3`.

## Using it

> "Update my work notes"
> "Log yesterday's work"

## When something looks wrong

**No meetings in the draft.** The Drive tool is not connected, or no meeting
docs were changed that day. The draft notes when meetings were not checked.

**A chat is missing.** Chats are matched by file modified date. A chat
resumed on a later day shows up on that later day.
