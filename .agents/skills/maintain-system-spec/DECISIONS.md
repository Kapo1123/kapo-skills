# Decisions

Some entries name `weekly-security-check`, `open-pr`, and `open-pr-workflow`.
Those skills are not in this repository; they live in the team skills repo
this copy came from. The decisions here hold without them.

This copy omits the pull-request workflow skill that asks about each rule
change and writes chart decisions. It is optional. Until one is added,
decisions are settled by hand: the person runs this skill on demand, and
chart entries stay undecided until then. Entries below that name
`open-pr-workflow` describe that skill when it is installed.

## Why system specs exist

Code shows what the system does, not what must stay true. A system spec
records the rules a change must not break. An agent loads one short spec for
the area it touches instead of reading the whole repo. Reviewers,
bug-hunter, the Security Reviewer, and `weekly-security-check` check a
change against named rules instead of guessing intent.

That only works while the spec is right. A stale spec misleads every agent
that trusts it, so keeping specs current is its own skill.

## What the existing specs showed

A survey of the 23 specs in three repos, a mobile app, an API server, and an
AI service, before this skill was written found none complete or reliably
current. Most decisions below answer
one of its findings.

## One format and one name in every repo

The mobile app used `*.system-spec.md`. The two servers used `system_spec.md`,
which allows one spec per folder and so forced specs to follow folders and
layers. One name, `<concern>.system-spec.md`, lets one glob find every spec
in every repo, and lets several concerns share a folder. The format lives in
[format.md](format.md) and nowhere else, so create and maintain cannot
disagree about it.

## Split by concern, with a size cap

The API server's `service/` and `model/` specs each covered about 270 files and
were mostly component lists. A layer has no rules of its own, so a spec for
it fills up with inventory. A concern is a set of rules that break together,
which is what a reviewer needs in one place.

The cap, about 300 lines, 20 rules, and 50 files or 8k lines of code, is what
one sub-agent can check in full without skimming. It matches the area size in
`weekly-security-check` for the same reason.

## Rules only, no signatures or inventories

The AI service's specs ran 750 to 1330 lines, mostly copied function signatures.
Signatures are already in the code, go stale the day it changes, and bury the
few rules that matter. Generic principles such as "Fail Secure" cannot be
checked against code. History, `TEMPORARY` notes, status tables, and plans
describe what is not true yet. [format.md](format.md#what-not-to-record)
lists all of these.

## Each rule has one home

The same rule appeared in up to four specs, and those copies were exactly
where specs contradicted each other: one copy was updated and the others
were not. A cross-cutting rule gets
its own spec and the others link to it by ID. When maintain finds the same
rule in two specs, it keeps one copy, and if the two disagree it holds the
change, because picking one could loosen the other.

## One master index, linked from rule files

Every hand-kept list of specs was incomplete. The mobile app kept four lists, and all
four missed the same 3 of 11 specs. `SYSTEM_SPECS.md` is the only list, and
rule files link to it. Index hygiene runs first every time, so the master
matches the files on disk before anything trusts it. Uncovered folders are
listed so a gap stays visible even when nothing in it changes.

## Stable rule IDs

Specs and comments cited rules by position, such as "invariants 1–2, 7–11".
Adding or removing one rule silently shifted every later citation. An ID
like `SESSION-03` is never renumbered or reused, and a rule keeps its ID when
it moves to another spec. Retired IDs stay on a `Retired:` line so no one
reuses them. Ranges are banned too: a range is a position in disguise.

## A last-verified commit, not a date

One spec was edited months after one of its rules had stopped matching the
code: the edits only appended sections, so the date said "current" while old
content rotted. Another spec showed no commits since its last update while a
file outside its Covers list broke one of its rules.
Hand-kept `Version` and `Last updated` headers drifted from git the same way.

So the master records, per spec, the commit at which the whole scope was last
read and every rule found holding. Due specs come from what changed since
that commit, by `git diff -M`. A date cannot say what was read; a commit can.

The check prompt also asks about changed files outside the spec's scope,
because that is how the second spec's rule was broken.

## Due after 4 weeks or a partial check

Appended edits hide stale content, and a rule can break through code no glob
names. A diff alone would never pick those specs again. So a spec last
verified 4 or more weeks ago is due regardless, and so is one whose last
check was partial. Last verified moves only on a full check, as in
`weekly-security-check`.

## Last verified moves only on the default branch

A branch commit may never reach `main`: squash merges and rebases replace
it. A master pointing at such a commit would give the next run a diff base
that does not exist in other clones. So Last verified moves only when `HEAD`
is `origin/main`. Uncommitted changes to covered code would mean the check
read code that is not in that commit, so they block it too. Comment-only
changes are allowed, because `create-system-spec` updates path references
in code comments in the same change it proves.

## A broken rule keeps the spec due

If Last verified moved while the code broke a rule, the next run would see no
changed files and skip the spec, and the violation would drop out of view. So
a spec with a broken rule, or a held looser change, keeps its old commit and
stays due until that is resolved.

## Every rule cites code

Only 3 of the 23 specs cited a test that enforces a rule. Most rules were
prose with no way to tell if they still held. Every rule now names what
enforces it and the `file:line` that shows it holds. A rule with no citation
is marked `(inferred)`: a claim to check, never a rule, so a guess written
once does not read as fact later.

## Prefer encoding over prose

A rule a test, a type, or a lint rule enforces fails loudly when broken. A
prose rule fails silently. So maintain suggests how to encode each unenforced
rule, and those are where it spends its effort. It does not write the test
itself: that is product code.

## Code that breaks a rule is a bug, not a stale spec

Rewriting the spec to match the code turns a bug into a rule, and the next
agent then protects the bug. So maintain never does it. It reports the break
as a probable bug with `file:line` and leaves the rule. When a sub-agent
cannot tell a bug from an intended change, it reports a break, because a
false bug report costs a person one look, and a false spec edit costs a
silent regression.

## Looser changes wait for the person

A stricter rule or a wording fix is safe to write. A looser one, which allows
more, checks less, widens a contract, or removes a rule, could be a
regression the code just introduced. Writing it would make the regression
the new normal. So it is reported and held until the person confirms it.
This is the same rule `weekly-security-check` uses for trust boundaries.

## The main agent spot-checks what it acts on

Sub-agents make mistakes, and two kinds of verdict lead to action: a stale
spec gets edited, and a broken rule gets reported as a bug. The main agent
opens the code for every one of those. It does not re-prove `holds`, because
that would double the cost for verdicts that change nothing. Coverage claims
are checked against the sub-agent's own file list, because sub-agents
sometimes claim full while listing partial reads.

## Sub-agents read; the main agent writes

Each spec means a lot of code to read, so each gets its own sub-agent, run in
parallel. Only the main agent writes, so two sub-agents cannot make
conflicting edits to the master or to a shared rule.

Sub-agents do not run tests or builds. Several in parallel would fight over
build directories and lock files, and a test run writes. The main agent may
run one enforcing test to confirm a verdict.

Cursor's Task tool has no read-only flag. Its `explore` type is built for
reading code, so the skill uses it, asked to be very thorough so it reads
files in full. Where no read-only type exists, the prompt's read-only line is
the only guard.

When maintain itself runs as a sub-agent, as in `open-pr-workflow`, the tool
may not let it start more sub-agents. It then checks the specs itself, one
at a time, with the same prompt. Slower, but the same result.

## Branch mode is scoped to the branch

`open-pr-workflow` runs maintain on every pull request, so it must be cheap.
Branch mode checks only the specs whose globs a changed file matches, and
reads the changed files plus the files the rules cite, not the whole scope. A
branch can only break a rule through what it changed. For the same reason a
repo-wide rule is searched in the changed files only. On demand, a repo-wide
rule gets a search of the whole repo.

Branch mode includes uncommitted and untracked files, because the person may
not have committed the last change before opening the pull request.

## Exactly one outcome

`clean`, `changed`, or `blocked` tells a caller in one word whether to stop.
`open-pr-workflow` continues on `clean` and stops on the other two. A broken
rule with no spec edits is `blocked`, not `clean`, because the specs cannot be
called current while the code breaks one. Moving Last verified forward is
bookkeeping, so it alone does not make a run `changed`. In branch mode,
`skipped` means there was nothing to check, which is not the same as checking
and finding nothing.

## Never edits product code; never commits

A spec pass that also edits code hides behavior changes inside a docs diff.
The person decides what to fix. Spec edits stay uncommitted so the person
reviews them, the same as `weekly-security-check` records and
`open-pr-workflow` apply edits.

## Splits and new specs wait for approval

A split decides which spec owns each rule, and a new spec takes a prefix that
is permanent. Both are hard to undo once others link to them. So maintain
proposes and waits. Missing rules inside an existing spec are added without
asking, because they make the spec stricter.

## System specs and OpenSpec

A system spec says what the current code must keep. OpenSpec says what a
change proposed and what was archived. OpenSpec requirements record what a
change intended, and nothing checks them against the code afterwards, so
they are not a safe source of current rules. When a change is archived, its
lasting rules move into the system spec that covers that code, checked
against the code like any other rule. Maintain does this when asked and
leaves the OpenSpec files as the record of the change.

## The rule check brief lives here, but this skill does not run it

`bug-hunter` checks each commit against the rules that cover it, and
`open-pr-workflow` checks each branch the same way. One brief serves both,
so they cannot disagree about what a break is or what counts as approval. It
lives in [rule-check.md](rule-check.md), with the slots, the git commands
that pick the specs, and the rule-change chart's format, because it reads
specs in this skill's format and should change when the format does.

It is not part of maintain's own run. Maintain checks whether specs match
code and never decides that a rule may change. The rule check asks a
different question: did this change break a rule, and did a person decide
that before the code existed. Keeping it out of maintain's steps keeps
maintain's outcomes (`clean`, `changed`, `blocked`) meaning what they mean.

Rejected: keeping the brief in `bug-hunter`. `open-pr-workflow` would then
need `bug-hunter` installed only to read a file, and installing it turns on
its hook. Also rejected: a copy in each caller, which drifts.

## A skipped rule change is an open-change line, listed until settled

When the person answers *skip for now* for a rule — in a pull-request
workflow skill's rule step when one is installed, or in a hand run when they
choose to record the skip — the branch merges with code that does not keep
the rule. That is the drift system specs exist to stop, so the skip has to
be followed up after merge. Whoever records the skip commits one
`Open change:` line under the rule, naming the
branch, the date, and the new behavior. The rule text stays as it was: the
line is not a rule edit and not approval, only a record that the code and the
rule disagree and the decision is pending. Every run of this skill lists each
one first and, on demand, asks the person to settle it: update the rule
(which removes the line) or change the code back (after which an on-demand
run with full coverage finds the rule holds and removes the line). An
unanswered one is asked again next run.

It lives in the spec because the spec is the one record that is in git,
reaches `main` with the code, and is read by every later check of that rule.
It names a branch, not a pull request, because Step 2a runs before the pull
request exists. It is the one note about pending work the format allows. The
ban on `TEMPORARY` notes is about text that describes what is not true yet;
this line describes what is true now.

In branch mode it is listed but does not change the outcome. Otherwise the
pull request that skipped the rule, and every later one touching that spec,
would stop at Step 2b for a decision the person already deferred.

Rejected: no follow-up, leaving the pull request description as the only
trace. Nothing reads it after merge, and the spec stays wrong. Also rejected:
blocking the merge on any skip. Then *skip for now* would not exist, and the
person would be forced to settle a rule in a pull request that is not about
it. And rejected: storing the skip only in the rule-change chart or the pull
request description. The chart is a committed log too, and it records the
skip, but it is history kept apart from the rule: a check of the spec would
not see it, and the chart's entry stays after the rule is settled. The
description is not checked by anything. The `Open change:` line sits next to
the rule, where this skill looks, and goes away when the rule is settled.

## Fixes from the first hunt of the rule check

The first `bug-hunter` run over this change found five gaps in the text
above. Each was shown with a scratch repo or a traced caller. They were
fixed before the first commit.

**An `Open change:` line is removed only by a full, on-demand check.**
Branch mode reads the changed files and the files a rule cites, and a
partial check skips some files. Either can say `holds` while an unread file
in scope still breaks the rule. Removing the line on that verdict loses the
only record that the rule is open. So Step 6 removes it only on demand, with
full coverage after the spot-check. Rejected: re-reading the whole scope in
branch mode to decide. That makes every pull request pay for a full check
of each spec it touches. Where this stops: a full check reads the scope, and
a file outside it that still breaks the rule is not seen. That gap is the
same for every rule.

**One `Open change:` line per branch, and a second skip replaces its own.**
The first draft kept one line per rule and added nothing when one was
there. A later skip of a different break was then lost, and *update the
rule* rewrote the rule to the older behavior. Replacing the old line with
the new one was also rejected: the older branch's code may still break the
rule. Lines from other branches stay; the settle question names them all.

**Chart names carry a hash of the branch name.** `/` to `--` alone sends
`dev/a/b` and `dev--a--b` to one file, and merging both conflicts. The
first 8 characters of `git hash-object` of the exact name tell them apart
and keep the readable part. Rejected: percent-encoding, which is exact but
turns `/` into `%2F`, and a Markdown renderer decodes that in a link.

**Commands fail closed or match the field's form.** The spec list runs with
`core.quotepath=off`, because git quotes non-ASCII paths and the `grep`
then misses them. The open-change search matches the field's form, not the
words, so a rule that mentions them is not listed. Commits for a chart entry
come from `git log -L` over the entry's lines, because `git log -S` on the
heading misses a later edit. An empty merge base stops the check with a
line, because every command after it would print nothing and exit 0.

**Branch approval is judged against the lines now there.** The first draft
compared the change doc with the first commit that ever made the break. A
break made, reverted, approved and made again then never counted the
approval. The first fix used the commits `git blame` names for the breaking
lines; the second hunt replaced that (below). Text committed in the
conversation under check still approves nothing.

**Decisions follow reported work.** In a pull-request workflow skill's rule
step, when one is installed, a decision goes into the chart only for a rule the spec-edit or fix sub-agent
reported done. A `could not`, a time-out, or a missing line stays undecided
and goes back to the person. Otherwise the chart said `skipped — open
change` for a rule whose spec never got the line, and nothing would ask
about it again. The same holds when a later break of a decided rule has a
different new behavior: it is a new entry and a new question, not the old
decision.

## Fixes from the second hunt of the rule check

A second `bug-hunter` run, over the text with the first fixes in, found ten
more gaps, three of them in those fixes. All were fixed before the first
commit.

**The break dates from the newest point the rule held.** `git blame` moved
the break's date to any later commit that touched the line, a comment or
trailing spaces included. A doc written after the break then counted as
approval. `git log -1 -S` for a removal picked a later comment that repeated
the removed words. Both are replaced by one method: walk the branch commits
that touched the files, find the newest at which the rule held, and take the
next one. A formatting or comment edit does not make the rule hold, so it
never moves the date. Where this stops: the sub-agent judges "held" at each
commit by reading it, so the answer is only as good as that reading.

**Approving text is dated by its lines.** `git log -S` on a phrase finds the
commit that first wrote the phrase. A rewrite in this conversation that kept
the phrase was then dated to an older commit and approved. The brief now
lists every commit that touched the approving lines with `git log -L`; in
one-change mode, any of them made in this conversation means no approval.

**Branch mode reads commits only.** `git diff <merge base>` compares the
working tree, so an unstaged revert hid a committed break and an unstaged
edit was asked about as if it would ship. The rule check now diffs
`<merge base> HEAD`. Maintain's own branch mode still includes uncommitted
files, because it checks specs against the code in front of the person; the
rule check decides what the pull request carries.

**Smaller command fixes.** `--no-renames` on the changed-file lists, so a
renamed test a rule cites still makes its spec due. The open-change search
takes `.+` for the branch, because git allows a comma there. The chart entry
range ends at the entry's last non-blank line, not two lines above the next
heading. An extension does not repeat a behavior the entry already has.

**Unfinished work is put back.** A spec edit that returned `could not` could
leave half a line in the file, and the commit took it; a retry then kept it
as an edit already made. Step 2a now restores those rules' lines from `HEAD`
before the commit, and the spec-edit brief starts each rule from `HEAD`. A
keep-old fix that did not make a rule hold no longer names that rule to
bug-hunter, so bug-hunter can still pause on it.

**Full coverage needs the file count.** A check that said `Coverage: full`
and gave no count of files read was taken as full, which is what lets an
`Open change:` line be removed. Now it counts as partial.

## Fixes from the third hunt of the rule check

A third `bug-hunter` run found thirteen more gaps, two of them in the
second-hunt walk. All were fixed before the first commit.

**The walk runs oldest first and follows renames.** The second-hunt walk
listed commits newest first, so "the next one" was the older commit, and a
re-break dated from the first break. It also listed only the current path,
so a rename looked like the break. It now follows renames and lists
oldest first; the fourth hunt changed how (below).

**Branch approval reads the doc just before the break.** Taking only the
newest commit that touched the approving lines let a trailing-space edit
hide an approval written in time. Branch mode now asks whether the text is
in the doc at the break commit's parent and still at `HEAD`. One-change
mode keeps the `git log -L` dating, because there the question is whether
this conversation touched the text.

**Skip restores the old rule; update keeps only a matching rewrite.** On
*skip for now*, a rewrite the branch had committed stayed, so a full check
later found the code matched it and removed the `Open change:` line. Skip
now restores the rule from the merge base. *Update the spec* kept any earlier
rewrite, even one for a different behavior; now it keeps one only if it
already says the new behavior.

**A marked line must match the search.** A `marked` result with a hyphen
for the em dash, or a cut-off date, was taken as done, and no later search
found it. Step 2a now counts it done only if the line matches the search.

**One `- new:` line per behavior.** The second-hunt fix joined behaviors
with `; ` and split on it. A sentence can hold `; `, so one behavior read as
two. Each behavior now has its own line, and a break joins an entry only by
matching one whole line.

**Paths are passed as they are.** The spec list uses `git ls-tree -z`,
because `core.quotepath=off` still quotes `"` and `\`. The changed-file list
and the citation search run with `core.quotepath=off`, so a non-ASCII path
matches and the spec path printed can be opened. Paths and globs go in
double-quoted shell variables, and `git show` takes a quoted
`"<rev>:<path>"`, so a space or an apostrophe does not break the command.
The single-quoted glob in `records.md`'s check prompt had the same fault
before this change; it was fixed here too.

**A missing chart heading stops the lookup.** An empty start line made
`git log -L` list the wrong lines and exit 0. The snippet now stops and
names the heading.

## Fixes from the fourth hunt of the rule check

A fourth `bug-hunter` run, over all three skills at once, found 29 gaps.
The user chose ten to fix before the first commit; these three are here.

**No `--reverse` with `--follow`.** On git 2.50 `git log --reverse
--follow` lists only the rename and drops every commit before it, so a
rename still looked like the break. The walk runs `git log --follow` and
reverses the list with `awk`. Checked in a scratch repo: the reversed list
held the break, the rename and a later edit, in that order.

**A skip's restore is not a break.** *Skip for now* puts the rule back to
its merge-base text. bug-hunter's check on that commit read the restore as
a rule edit and added a second, undecided entry. The brief now lists that
restore, when the caller names the rule as a Step 2a skip, as not a break,
and a Step 2a commit adds no new entry for a rule it decides.

**A failed keep-old fix is put back.** The fix brief had a sub-agent that
returned `could not` leave its half-written code, and the fallback commit
used when bug-hunter is missing committed it. It now puts that rule's files
back from `HEAD` before it returns or commits.

**The default branch, not `origin/main`.** The merge base is taken with the
branch `origin/HEAD` points at, as `open-pr` does, so a repo whose default
branch is `master` is checked instead of stopped.

## Known gaps after the fourth hunt

The fourth hunt found these in this skill. None could be shown with a
failing test, and the user left them for a later change. Each line is the
gap and the proposed fix.

- `git log --follow` leaves out a merge whose conflict resolution makes the
  break. List merge commits that touched the file too.
- A change doc moved after the break fails the parent-and-`HEAD` check.
  Follow the doc's renames to its path at the break commit's parent.
- The citation search still quotes `"` and `\` in the spec path it prints.
  Use `git grep -z -l` and `tr '\0' '\n'`.
- The changed-file list still quotes `"`. Use `--name-only -z`.
- `records.md`'s draft prompt has a single-quoted glob that breaks on an
  apostrophe. It was there before this change. Use the double-quoted
  variable form.
- The on-demand scope list leaves out untracked files, so a full `holds`
  can remove an `Open change:` line while an untracked file still breaks
  the rule. Add `git ls-files --others --exclude-standard`.
- The spec-edit brief uses one spec path at `HEAD` and the merge base, so a
  renamed spec fails each time. Pass both paths.
- Every detached `HEAD` shares the chart file `detached-<hash>.md`. Use the
  starting commit's sha, or ask.
- Step 3's open-change search and the check prompt's scope list print
  quoted non-ASCII paths. Run both with `-c core.quotepath=off`.
- On demand, Step 6 removes an `Open change:` line without opening the
  cited code. Confirm the `holds` first for such a rule.
- The open-change search accepts a line with nothing after `— `. End the
  pattern with `— [^[:space:]]`.
