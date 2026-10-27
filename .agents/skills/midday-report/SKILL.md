---
name: midday-report
description: >-
  Draft a mid-day Slack update of what the user has done so far today, and
  ask for review or feedback where that applies. Show the full draft first.
  Send it only after an explicit OK, to a channel or person you ask for each
  time. Use when they ask for a mid-day report, a midday update, a progress
  update to the team, or to ask for review or feedback in Slack, including
  "what should I tell the team so far" and "draft my midday update". Not the
  end-of-day daily report. Never run it on a schedule or without being asked.
---

# Mid-day report

One Slack message: work done so far today, plus a review or feedback ask
where the sources support one. Show the full draft. Send it only after the
user says to send that exact text.

This is its own skill. An end-of-day report belongs to `daily-report`.

- **Why these rules** — [DECISIONS.md](DECISIONS.md). Read it before changing
  the window, the destination, the send step, or which sources are gathered.
- **For the person using it** — [README.md](README.md).

## Contract

1. Run only when asked. Never on a timer. Never for someone else's day.
2. The window is local midnight today through now, unless they name another
   window. Tell them which window you used.
3. The opening request is not approval to send. Show the full draft, then
   wait. Send only after a later, explicit OK for this exact text and this
   destination. After any edit, show the full draft again and wait again.
4. Ask which channel or person each time. Do not hard-code one. Do not save
   one for the next run.
5. Five sources, each optional. If a tool is missing, skip that source and
   say so in one line to the user. Do not put that line in Slack.
6. Before you show the draft, leave out secrets, tokens, customer or personal
   data, and private DM or private-channel content. Flag anything borderline
   next to the draft, not inside it.
7. The message is Slack mrkdwn, readable in under a minute. Omit empty
   sections.

## Checklist

```
- [ ] Window: local midnight to now, or the window they named
- [ ] Gather available sources (parallel subagents when you can)
- [ ] One line to the user for each missing source
- [ ] Merge items that are the same work
- [ ] Draft, then strip secrets and private content
- [ ] Show the full draft and ask where it goes
- [ ] Wait for an explicit OK
- [ ] Send, then return the message link
```

## 1. Window

Start is today at 00:00:00 in the user's local timezone. End is now. If they
name a window ("since 11", "yesterday afternoon"), use that and repeat it
back.

```python
from datetime import datetime, time
now = datetime.now().astimezone()
start = datetime.combine(now.date(), time()).astimezone()
```

Do not use `now.replace(hour=0, ...)`. It keeps the current UTC offset, so
on a daylight-saving change day the window starts an hour off.
`scripts/test_window.py` checks this.

Pass `start.isoformat()` to a tool that takes a timestamp. Pass
`int(start.timestamp())` to a tool that takes epoch seconds.

## 2. Gather

Where you can run subagents, use one per source below, at the same time.
Each returns a short list with links. None of them writes the Slack message.
You merge. If you cannot run subagents, gather the sources yourself, in
parallel when the tools allow it.

Resolve who the user is on each source, from that tool, every run. Do not
type a name, login, or id from memory. If it is unclear whether an item is
theirs, leave it out.

A missing tool skips that source. Say which one, in one line, to the user.

### Git commits and GitHub pull requests

Needs `git`, and `gh` authenticated. Login: `gh api user --jq .login`.

Repos to look at, and no others: open workspace roots; a project path encoded
in today's transcript folder name, when that directory exists; a repo named
by the search below, when you already have a checkout. Do not scan the home
directory.

In each repo, commits in the window. Keep a commit when its author email
matches `git config user.email`, or the email or name contains the GitHub
login. If you cannot tell, leave the commit out. If `user.email` is unset
and `gh` has no login, skip local commits and say so.

```bash
git -C "$REPO" log --since="$START" --until="$NOW" --pretty=format:'%H%x09%an%x09%ae%x09%s'
```

Build a commit link only from a remote URL you read (`git remote get-url
origin`). Do not invent a host or an owner.

Pull requests: one search for the whole account, not a loop over repos.
These flags come from `gh search prs --help`. If a flag errors, read that
help again instead of guessing.

```bash
gh search prs --involves "$LOGIN" --updated ">=$START" --limit 100 \
  --json repository,number,title,url,updatedAt,state,author
gh search prs --reviewed-by "$LOGIN" --updated ">=$START" --limit 100 \
  --json repository,number,title,url,updatedAt,state
```

`$START` is the ISO timestamp with the local offset, quoted. `--limit`
defaults to 30, so pass 100. If the count comes back equal to the limit,
raise it and search again. Do not pass a fixed `--owner`.

`--involves` matches author, assignee, commenter, and mentions. Treat the
rows as candidates. Keep a pull request when they authored it, pushed it,
reviewed it, or were asked to review it. The second command is there because
a review with no comment is not a commenter.

For an open pull request they authored, requested reviewers are
`reviewRequests` on `gh pr view` (see `gh pr view --help`):

```bash
gh pr view <number> --repo <owner/repo> --json reviewRequests,url,title,state
```

Tag someone in *Review wanted* only when that list already includes them,
and only when a user search matches them to a Slack user. Do not invent a
reviewer or a Slack id. If the user names a person to ask during this run,
you may tag that person. They just asked.

### Agent chats

Check the usual folders. Use one only if it exists.

- Cursor: `~/.cursor/projects/*/agent-transcripts/*.jsonl`
- Claude Code: `~/.claude/projects/**/*.jsonl`

Keep files modified inside the window, plus this session if it is not on
disk yet. Skip directories named `memory` or `tool-results`. Summarize work
done: what was built, fixed, or decided. Never quote prompts, replies, or
tool output. Never put a machine path in the Slack message. If neither
folder exists, skip past chats and say so. This session still counts.

### Tasks

A task tool, for example ClickUp. If none is connected, skip. Resolve the
current user with that tool's own current-user call. Take tasks they
updated, commented on, or finished in the window. Before an ask, read the
thread. If someone already answered, report the answer instead of asking
again. Link the URL the tool returned. Do not guess an id.

### Slack threads

A Slack search. Resolve the logged-in user id from the tool, not from
memory. Search messages they sent in the window. If the tool takes epoch
seconds, pass the window start there. A date-only `after:` includes the
previous day, so drop anything before the start. If a shortcut such as
`@me` returns nothing, retry once with the literal id.

Read a thread they posted in during the window far enough to see the
decision and whether an ask is still open. Report decisions and open asks.
Do not quote messages. A thread they did not post in does not count.

Use a public search when the tool offers one. Leave out direct messages and
private channels. Count them and list the count next to the draft. Add one
only if the user says to.

### Meeting notes

A Google Drive search. One search for documents modified after the window
start whose titles look like meeting notes. Skip a status ritual (standup,
stand-up, daily sync, scrum, daily huddle) unless its notes contain a
decision or an action item for the user. A meeting counts when the notes
mention the user.

Report decisions and their action items. Do not quote the notes. Use the
search snippet when it already has those. Open a document only when the
snippet has neither, and only for a note that mentions them. Do not open
every note. If the Drive tool is missing, skip. Do not start a sign-in
mid-report.

## 3. Merge

The same work is one line. A pull request, its commits, and a chat about
that pull request are one line. A meeting action item that is already a task
is one line. Keep the latest state. Link the specific thing once, with a URL
you actually have. A made-up link is worse than plain text.

## 4. Draft

Slack mrkdwn. A person should read it in under a minute. One sentence per
line. Omit a section that has nothing in it. No greeting, no sign-off, and
no note about which tools worked. That note stays in the chat with the user.

```
*Mid-day update* — Tue Oct 27

*Done so far*
- Shipped <https://github.com/example/repo/pull/1|the widget export>: the shop can download last month as a file.

*Up next this afternoon*
- Finish the export tests.

*Review wanted*
- <https://github.com/example/repo/pull/2|Add export filters> is open. <@USERID|Ada> is already requested.

*Feedback wanted*
- Is a weekly file enough, or do you want a daily one too?

*Blockers*
- Waiting on a sample file before the parser can be checked.
```

- **Done so far.** Outcomes from the window. Lead with the effect.
- **Up next this afternoon.** Only what the sources support: an open task, a
  meeting action item, or something they said they would do. If you do not
  know, omit the section and say so next to the draft.
- **Review wanted.** Open pull requests. Tag a reviewer only when
  `reviewRequests` already lists them, or when the user named that person
  in this request. If the ask was already answered, do not ask again.
- **Feedback wanted.** An open question they raised, or work that is not a
  formal review. Do not invent a question.
- **Blockers.** Something actually stuck. Do not invent one.

Links are `<url|text>`. Mentions are `<@USERID|Name>`. Section titles are
`*like this*`.

Before you show the draft, read the send tool's description. If that tool
posts standard markdown and would show mrkdwn as raw characters, convert
syntax only and show the version it will post. Wait for OK on that version.

## 5. Show, then wait

Read the draft for secrets, tokens, customer data, health data, personal
phone numbers, personal email, and quotes or details from a private DM or
private channel. Take them out. If an item is borderline, leave it out and
put one line under the draft: "Left out: … Say if it should go in."

Show the full draft. If this request already named a channel or person,
repeat it beside the draft. If it did not, ask where to send it. A
destination is not an OK. An OK with no destination is not enough: ask
where.

OK means a clear yes to send this exact text to that place ("send it",
"yes, post it"). "Looks good" counts only when both the draft and the
destination are already on screen. "Change the second line" does not. Apply
the edit, show the full draft again, and wait.

## 6. Send

Resolve the channel or the person with a search at send time. Send with the
Slack action that posts a message, not the one that saves a draft. The
review happened in this chat.

Return the link the tool gives you. Do not build a permalink by hand.

If sending fails, say why in plain language, show the draft again, and
stop. Do not post it somewhere else. Do not retry until they ask.
