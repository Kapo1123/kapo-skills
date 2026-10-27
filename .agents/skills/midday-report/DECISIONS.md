# midday-report — decisions

Read this before changing the window, the destination, the send step, or
which sources get gathered.

Gathering follows the `daily-report` skill: resolve the person from each
tool, search once per source instead of looping over repositories, leave
out activity you cannot tie to them, and link only a URL the tool returned.
Nothing from that skill's company setup is copied here: no workspace, no
channel, no list id, no repository, no handle.

## Its own skill, not a mode of daily-report

**Decision.** `midday-report` is a separate skill. It does not add a flag
or a mode to `daily-report`.

**Why.** The two reports answer different questions. This one is the middle
of the day and asks for review or feedback where the work needs it.
`daily-report` is the end of the day. A mode would hide a different window,
a different destination rule, and a real send behind one command.

**Rejected.** A mode of `daily-report`.

## Show the draft, then wait for an OK

**Decision.** Show the full draft first. Send only after a later message
that approves this exact text. Edits are applied, the full draft is shown
again, and the agent waits again. The opening request does not count as
the OK, even when it says "send".

**Why.** The message goes to other people. The user has to see the words
and the destination before they go out.

**Rejected.** Sending directly. Also rejected: saving a Slack draft for the
user to send themselves. That is how `daily-report` posts. This skill
sends, and only after the OK.

## Ask where to send it, every time

**Decision.** Every run asks which channel or person, unless this request
already named one. That name is repeated beside the draft. It is not
written into the skill, and it is not stored for the next run.

**Why.** The audience changes. A stored channel would send a later update
to the wrong place without a new question.

**Rejected.** A hard-coded channel. A stored channel.

## The window is today so far

**Decision.** The window starts at local midnight and ends now. The user
may name a different window. The agent says which window it used.

**Why.** A mid-day note is about today. Anchoring on the last end-of-day
post would pull in yesterday, or drop this morning when that post went out
late.

**Rejected.** `daily-report`'s window (from the last report, capped at 36
hours). A saved "last run" time. A discarded draft must not move the
window, because this skill does not store one.

## Every source is optional

**Decision.** Gather all of these, and skip any whose tool is missing:
git commits and GitHub pull requests and reviews; today's Cursor and
Claude Code chats; tasks (ClickUp when that is the tool); Slack threads
the user took part in; meeting notes in Google Drive. Say which source
was skipped, in one line, to the user. Do not put that line in Slack.

**Why.** People do not all have the same tools connected. A missing tool
should not block the update, and the channel should not hear about the
agent's setup.

**What was borrowed from `daily-report`.** One `gh search prs` for the
account, plus a second `--reviewed-by` search, instead of a loop over
repos. Flags were checked with `gh search prs --help`: `--involves`,
`--reviewed-by`, `--updated`, `--limit`, `--json`. Requested reviewers
come from `reviewRequests` on `gh pr view`. No owner is hard-coded,
because this skill is not tied to one organization. Slack uses the
tool's timestamp bound when it has one, because a date-only filter
includes the previous day. Meeting notes start from one Drive search
and the snippet. Open a note only when that snippet has neither a
decision nor an action item. Agent chats are summarized from local
transcripts. `daily-report` only sees the session it is running in;
this skill also reads today's transcript files, when those folders
exist, and still does not quote them.

**Rejected.** Requiring every source. Putting "Slack was unavailable"
in the message. Copying a fixed organization into the GitHub search.

## What the message contains

**Decision.** Slack mrkdwn, readable in under a minute. Sections, in
this order, and only when they have something to say: Done so far; Up
next this afternoon; Review wanted; Feedback wanted; Blockers. The same
work from two sources becomes one line. In Review wanted, tag a
reviewer only when the pull request already requests them, or when the
user names that person during this run.

**Why.** The reader is a teammate with a minute. Empty headings and
repeated lines waste it. Tagging someone who was not asked for a review
is a nuisance.

**Rejected.** A fixed template that keeps empty sections. Tagging every
collaborator. Inventing a reviewer.

## What stays out of the draft

**Decision.** Before the draft is shown, remove secrets, tokens,
customer or personal data, and content from a private DM or a private
channel. Borderline items are listed under the draft. They go in only
if the user says so. Slack threads contribute decisions and asks, not
quotes. Meeting notes contribute decisions and the user's action items.
Agent chats contribute a summary of work done, never quoted text.

**Why.** The draft is about to be posted. Quoting a private thread, or
a transcript, publishes something the user did not choose to share.

**Rejected.** Quoting the source "so the user can see it was accurate"
inside the Slack message. Trusting the model to paraphrase a private
channel into the draft without asking.
