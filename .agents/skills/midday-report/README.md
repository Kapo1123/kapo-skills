# midday-report

Drafts a Slack message for the middle of the day: what you have done since
local midnight, plus a review or feedback ask where that applies. You see
the full draft, you pick the channel or person, and it sends only after you
say so.

This is not the end-of-day report. That one is `daily-report`, which is not
in this repo.

Source gathering follows `daily-report`: who you are comes from each tool,
activity you cannot tie to yourself stays out, and a link is used only when
the tool returned a real URL. The window, the destination, and the send
step are different. See [DECISIONS.md](DECISIONS.md).

> Agent instructions: [SKILL.md](SKILL.md).

## Setup

Ask the agent: **"Install the midday-report skill"**. Try it in this tab.
Open a new tab only if it is not picked up.

If the agent does not know how, set up the skill manager first. See
[Install](../../../README.md#install) in the repo root.

No extra token. It uses tools you already connected. Each source is
optional:

| Source | Tool, if you have it |
| --- | --- |
| Commits and pull requests | `git` and `gh` |
| Agent chats | Local Cursor and Claude Code transcripts |
| Tasks | A task tool such as ClickUp |
| Slack threads | Slack search |
| Meeting notes | Google Drive search |
| Sending | Slack send |

A missing tool is skipped. The agent tells you in one line. That line is
not part of the Slack message.

## Using it

> "Write my mid-day report"
> "Midday update for the team"
> "Progress update, and ask for review"

It asks where to send the message every time. Say a channel or a person
when you want to, or wait and answer when it asks. Then read the draft.
Say "send it" when the text and the destination are both right. Ask for an
edit if they are not. It shows the new draft and waits again.

It does not remember the channel.

## When something looks wrong

**It sent nothing.** Expected until you approve the draft. Name the
destination and say "send it".

**A section is missing.** Empty sections are left out. Say what to add.

**It skipped tasks, Slack, or meetings.** That tool is not connected. The
rest of the draft still stands. Connect the tool and ask again if you want
that source included.

**It left something out.** Secrets, customer or personal data, and private
DMs stay out until you say to include them. The note under the draft lists
what was held back.

**The send failed.** The draft is still in the chat. Nothing was posted to
a different channel.
