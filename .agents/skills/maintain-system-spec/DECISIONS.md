# Decisions

Some entries name `weekly-security-check` and `open-pr-workflow`. Those skills
are not in this repository; they live in the team skills repo this copy came
from. The decisions here hold without them.

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
