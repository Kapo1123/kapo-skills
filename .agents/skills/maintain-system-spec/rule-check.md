# System-spec rule check

A read-only check of one change against the system specs that cover it. It
reports each rule the change breaks, and whether a change doc approved it.
`bug-hunter` runs it at commit time, over one change. A pull-request workflow
skill, when one is installed, runs it at pull-request time, over a whole
branch. That skill is optional and not in this repository; without it, the
person settles rule changes by running `maintain-system-spec` themselves,
and chart entries stay undecided until then. This skill does not run the
check. It lives here because the specs and their [format](format.md) do.
This file also defines the rule-change chart, the committed log those
callers write.

Each caller says when the check runs and what its answer does. This file
holds who does each step, the slots, which specs to check, the briefs, and
the chart.

## Who does what

A step that must ask the person and wait stays with the main agent: a
sub-agent cannot stop and ask. Reading specs against a diff, editing to an
outcome already decided, writing a fix, and committing go to sub-agents.
Independent work runs in parallel. Work that shares one context stays in one
agent.

| Step | Who | Why |
|------|-----|-----|
| **bug-hunter**: does the repo have specs; is this file readable | Main agent | Two reads that decide whether anything launches |
| bug-hunter: pick the specs | Main agent | `git` only; no spec due means no sub-agent |
| bug-hunter: the rule check | One sub-agent, `rule_check` role, [brief](#brief), launched in the same message as the finders | Reads specs and the diff in full; independent of the hunt, so it runs beside it |
| bug-hunter: apply an earlier acknowledgement | Main agent | Only it sees the conversation |
| bug-hunter: pause, continue or stop and fix | Main agent | Asks and waits |
| bug-hunter: the stop-and-fix code change | The rule-check sub-agent, resumed with the [fix brief](#fix-brief) | It already read the rule, the diff and the break. A fresh one, `rule_check` role, only if it cannot be resumed |
| bug-hunter: chart entries, then the commit | Main agent | Entries are written and staged before the mint, so the binding covers them; the commit script mints in the main agent |
| **PR workflow skill, rule step ("2a")**, only when one is installed: preconditions, this branch's chart file | Main agent | A few reads |
| 2a: branch re-check, merged with the chart | One sub-agent, `rule_check` role, [brief](#brief) | One branch diff is shared context; one agent per spec would re-read it each time |
| 2a: ask about each rule | Main agent | Asks and waits, one rule at a time |
| 2a: spec edits and open-change lines | One sub-agent per spec file, `mechanical` role, [spec-edit brief](#spec-edit-brief), all in one message | Different files, no shared state |
| 2a: commit the spec edits | One sub-agent, `mechanical` role, following `bug-hunter` | Every commit goes through bug-hunter; a spec-only commit is a triage skip plus the rule check |
| 2a: keep-old-behavior code change, and its commit | One sub-agent, `rule_check` role, [fix brief](#fix-brief): it returns before committing, then is resumed to follow `bug-hunter` | The decision is written only after it reports the rule holds; the fix and its hunt share context |
| 2a: write each decision into the chart | Main agent, only for work a sub-agent reported done, before the commit that carries the decision | A small edit; it must be staged with the spec edit or fix it records |
| **maintain-system-spec**: list open changes | Main agent | One `git grep` |
| maintain: check the rules that carry one | The per-spec check sub-agents it already runs | Already read-only and parallel |
| maintain: settle each open change | Main agent on demand; the caller in branch mode | Asks and waits |
| maintain: rewrite the rule, remove the line | Main agent | In this skill only the main agent writes, so no two agents edit the same spec or the master |

**Model.** The role named in each row is one of `bug-hunter`'s model roles.
Run its `scripts/models.py` and pass the first entry of that role's list the
host offers, as `bug-hunter`'s SKILL.md, *Models by role*, says, with
`subagent_type: generalPurpose`. The rule check, its re-check, and a fresh
fix agent use `rule_check`, which is Grok-first by default: the check runs on
every reviewed commit, so the cost and speed that keep the finders on Grok
apply to it too. The spec-edit and commit sub-agents use `mechanical`: they
edit to an outcome already decided, or commit. A resumed agent keeps its
model.

## Slots

| Slot | One change (`bug-hunter`) | Branch (a PR workflow skill) |
|------|---------------------------|-----------------------------|
| `<rev>`: rules and change docs as of | `HEAD` | the merge base with the remote's default branch, `git merge-base "$(git symbolic-ref --short refs/remotes/origin/HEAD)" HEAD` |
| `<diff>`: the change | `git diff --cached` | `git diff <rev> HEAD` |
| `<changed>`: its file list | `git -c core.quotepath=off diff --cached --no-renames --name-only` | `git -c core.quotepath=off diff --no-renames --name-only <rev> HEAD` |
| Commits that cannot approve | the short sha of every commit this conversation made, or `none` | `none`; the order rule in the brief applies instead |

Branch mode reads commits only. The pull request carries what is
committed, so an unstaged edit or an untracked file is not part of the
change: it can neither hide a committed break nor report one that will not
ship. `--no-renames` lists a renamed file under its old path too, so a rule
that cites the old path still makes its spec due.

For a commit that already landed, use one-change mode with `<rev>` =
`<sha>^` and `<diff>` = `git diff <sha>^ <sha>`.

The default branch is the one `origin/HEAD` points at (`origin/main`,
`origin/master`, …). If `origin/HEAD` is not set,
`git remote set-head origin --auto` sets it.

**No merge base, no check.** In branch mode, if the default branch cannot be
found, or `git merge-base` fails or prints nothing, stop before picking
specs. Say `rule check stopped — no merge base with the default branch`,
and do not report "no rule changes". An empty `<rev>` makes the commands
below check nothing and still exit 0.

## Which specs to check

The caller does this before launching, from git alone. Put `<rev>` in
`REV`, and each path and glob in a shell variable, double-quoted as below:
a value with an apostrophe or a space breaks inside single quotes.

1. **Spec files at `<rev>`:**
   `git ls-tree -r -z --name-only "$REV" | tr '\0' '\n' | grep -E '\.system-spec\.md$'`.
   `git ls-tree` does not take `:(glob)` pathspecs, hence the `grep`.
   With `-z`, git prints each path as it is. Without it, git quotes a path
   with non-ASCII bytes, a `"` or a `\`, the line no longer ends in
   `.system-spec.md`, and that spec is missed. `core.quotepath=off` alone
   still quotes `"` and `\`.
2. **Scope globs:** the Covers column of `git show "$REV:SYSTEM_SPECS.md"`.
   For a spec with no row there, the Scope section of `git show "$REV:$SPEC"`.
   A spec with neither covers its own folder.
3. **A spec is due** when any of these hold:
   - a glob matches a changed file:
     `<changed> -- ":(glob)$GLOB" ':(exclude)system-spec-changes/**'` prints
     something;
   - a rule cites a changed file, such as a test named in `Enforced by`:
     `git -c core.quotepath=off grep -l -F "$PATH_CHANGED" "$REV" -- ':(glob)**/*.system-spec.md'`.
     It prints `<rev>:<spec path>`; the spec path is the part after the
     first `:`;
   - the change edits or deletes the spec file itself;
   - the spec has a `Scope: repo-wide` rule and a changed file is code. Pass
     "only the repo-wide rules" for that spec.

A spec that does not exist at `<rev>` is new with this change. It has no
committed rule to break, so it is not due.

## Brief

Use this template verbatim. Slots are in angle brackets. The caller adds its
own constraints after it, never inside it.

```text
You are a system-spec rule check. You cannot see the parent conversation.
Do not edit files. Do not commit. Do not run the project's test suite or a build.

Repo: <absolute path>
Mode: <"one change" or "branch">
Rules as of: <rev>
Change: <diff command>
Specs to check: <each spec path, with the changed files that made it due, and "all rules" or "only the repo-wide rules">
Change docs: <"openspec/changes/" and its archive, "specs/<feature>/" for spec-kit, other paths the repo uses for them, or "none">
Commits that cannot approve: <short shas, or "none">

A system spec is a <concern>.system-spec.md file. Each rule has an ID such as REFUND-02, a rule sentence, and Enforced by and Evidence lines.
Read each spec as it was at <Rules as of>: git show "<Rules as of>:<path>", quoted, since a path can hold a space. The working copy is in flight and is not the rule.
Read the change for each spec's files, and each file a rule cites, in full.

A break is any of these:
- code breaks it: the change makes code do what a rule forbids, or stop doing what a rule requires
- evidence removed: the change deletes or weakens a test or other evidence a rule cites
- rule edited: the change edits a rule in a spec file: the rule sentence now means something else, the rule is removed or retired, the spec file is deleted, or a Scope glob that still matches files is dropped
Not a break: behavior no rule covers yet; a new rule; an Evidence or Enforced by line moved because the cited code moved; a wording fix with the same meaning; an Open change line added or removed under a rule; a rule put back to its text at the merge base, when the caller's constraints name that rule as answered skip for now; any change under system-spec-changes/, which is a log, not a spec. A rule marked Evidence: (inferred) is a claim, not a rule: list what breaks it as a note, not a break.
A rule with an Open change line is still the rule. Report a break of it as usual, and quote that line in the block.

For each break, decide whether a change doc approved it:
1. Look in the change docs for text that records a decision to make this rule change. It names the rule ID, or describes this same change to this same behavior. Text about a nearby decision is context, not approval.
2. Check when that text was committed.
   Mode "one change": date the approving lines, not a phrase in them. Find their range <a>,<b> in git show "<Rules as of>:<doc>", then list every commit that wrote or changed them: git log --format=%h -s -L "<a>,<b>:<doc>" <Rules as of>. It counts only if no sha in that list is in "Commits that cannot approve". A rewrite made in this conversation approves nothing, even when it kept the old words.
   Mode "branch": it counts only if the approving text is in git show "<break commit>^:<doc>", the doc just before the break, and is still in git show "HEAD:<doc>". A later edit that keeps the text, such as a trailing space, does not undo it. To find the break commit, list the branch commits that touched each file in "where", following renames, then put them oldest first: git log --follow --format=%h <Rules as of>..HEAD -- "<file>" | awk '{ l[NR] = $0 } END { for (i = NR; i > 0; i--) print l[i] }'. Do not use git log --reverse with --follow: git then lists only the rename and drops the commits before it. Read the file at each one (git show "<sha>:<path at that commit>") and find the newest at which the rule held. The break commit is the first commit after it in that list, or the first in the list if the rule held at none. A commit that only renames the file, edits comments or formatting, or repeats a removed phrase in a comment, does not make the rule hold, so it never moves the break commit. A break that was made, reverted, then made again dates from the commit that made it again.
   Text only in the working tree, or staged with this change, approves nothing.
3. When unsure, it is not approved.

Return one block per break, or the single line "none":
- rule — spec path and rule ID (a spec with no IDs: its heading)
- old — the rule, quoted as it was at <Rules as of>
- kind — code breaks it | evidence removed | rule edited
- new — the new behavior, in one sentence
- where — file:line ranges
- commit — mode "branch" only: the short sha of the break commit
- approved — "no", or the change doc path, the commit that wrote the text, and the quoted text
- open change — the rule's Open change lines at <Rules as of>, or "none"
Then the notes on (inferred) rules, one line each, or "notes: none".
```

The text above the slots stays byte-stable across runs, so repeated launches
hit the prompt cache.

**Committed versus in flight.** A sub-agent cannot date a document, so it
would read a design written minutes ago as deliberated intent. An agent can
write both the code and the doc that justifies it. So only text a commit put
there before the change counts. In one-change mode `git log -L` dates the
approving lines themselves: `git log -S` on a phrase finds the commit that
first wrote the phrase, which can be older than the rewrite that turned it
into approval. In branch mode the doc is read as it was just before the
break commit, so a later touch of the text cannot hide or create approval.

## Spec-edit brief

A pull-request workflow skill's rule step, when one is installed, one
sub-agent per spec file, after the person has answered every rule. Template
verbatim, slots in angle brackets:

```text
You are a system-spec editor. You cannot see the parent conversation.
Edit only the one spec file named below. Do not edit code, tests, SYSTEM_SPECS.md, or any other file. Do not commit.

Repo: <absolute path>
Spec: <repo-relative path>
Format: <absolute path to maintain-system-spec/format.md>
Branch: <branch name>
Merge base: <sha>
Date: <YYYY-MM-DD>
Rules: one line each: <rule ID> — <"update the spec" or "skip for now"> — new behavior: <one sentence> — where: <file:line ranges> — open change already: <the rule's Open change lines, or "none">

Read the format file, then the spec, then the code and tests at "where".
Start each rule from its text in git show "HEAD:<Spec>". An uncommitted edit to that rule in the working tree is not kept: it may be a half-finished earlier attempt.
For "update the spec": rewrite the rule sentence in place to the new behavior and keep its ID. If the new behavior removes the rule, delete it and put its ID on the section's Retired: line. Point Enforced by and Evidence at the code and tests that show the new rule, by file:line; write unenforced or (inferred) when nothing does. Remove the rule's Open change line for <Branch>, if any. Leave lines from other branches; maintain-system-spec checks them against the new rule. If a commit on this branch already rewrote this rule and that rewrite already states the new behavior, keep it and fix only its format. Otherwise write the new behavior.
For "skip for now": restore the rule sentence, Enforced by and Evidence to their text in git show "<Merge base>:<Spec>", undoing any rewrite this branch committed; the rule stays as it was before the branch. If the rule has an Open change line for <Branch>, replace it with "  - Open change: <Branch>, <Date> — <new behavior>". Otherwise add that line under the rule, after its other fields and any Open change lines. Leave lines from other branches.
If you cannot finish a rule, put its lines back exactly as they are in git show "HEAD:<Spec>" before you return.

Return one line for every rule in Rules, none left out: <rule ID> updated | marked | replaced, with the spec lines changed, or <rule ID> could not: <why>. A rule you did not finish is could not.
```

## Fix brief

The code change that makes a broken rule hold again: `bug-hunter`'s
*stop and fix*, sent to the resumed rule-check sub-agent, and a pull-request
workflow skill's *keep the old behavior*, when one is installed, in one fresh
sub-agent for all such rules. Template verbatim, slots in angle brackets:

```text
You are a system-spec fix. You cannot see the parent conversation.
Edit code and tests only, plus the spec lines named below. Do not edit any other spec text.

Repo: <absolute path>
Change under review: <"the staged change" or "this branch, against <merge base>">
Rules to keep: one line each: <spec path> <rule ID> — rule as committed: "<quoted rule>" — what breaks it: <one sentence> — where: <file:line ranges>
Also commit: <the chart file the parent updated, or "none">
Then: <"return; do not commit" or "follow the bug-hunter skill to commit these changes and the Also commit file, with this in its brief: the person answered keep the old behavior for <only the rule IDs you reported holding>">

Change the code so each rule holds again. Change back only what breaks the rule; keep the rest of the change. If the change deleted or weakened a test the rule cites, restore it. If it edited the rule's text in its spec, restore the text as committed. Leave any Open change line: it may stand for code outside this change, and maintain-system-spec removes it once an on-demand check with full coverage finds the whole rule holds.
If you cannot make a rule hold, put every file you changed for it back to git show "HEAD:<path>", and delete any file you added for it, before you return or commit. A half-written fix never reaches a commit.
If bug-hunter is not installed and "Then" says to commit, commit those paths with --trailer "Bug-hunter: skipped — bug-hunter not installed", only after that put-back.

Return: files changed, one line each; for each rule, either the file:line that shows it holds now, or <rule ID> could not: <why>, with the files you put back; then bug-hunter's summary, if it ran.
A rule you did not make hold is not named in the bug-hunter brief. It stays open, so bug-hunter's rule check can still pause on it.
```

## The rule-change chart

A permanent, committed log of every rule change: what a commit let through,
and what was later decided for it. It lives beside the spec index, one file
per branch ([format.md](format.md#the-rule-change-chart)):

```bash
BRANCH="$(git branch --show-current)"
NAME="${BRANCH:-detached}"
SAFE="$(printf '%s' "$NAME" | sed -e 's#/#--#g' -e 's#[^A-Za-z0-9._-]#-#g')"
HASH="$(printf '%s' "$NAME" | git hash-object --stdin | cut -c1-8)"
CHART="system-spec-changes/$SAFE-$HASH.md"
```

`dev/someone/store-credit` becomes
`system-spec-changes/dev--someone--store-credit-929d780b.md`. The readable
part alone folds some names together: `dev/someone/store-credit` and
`dev--someone--store-credit` both read `dev--someone--store-credit`. The
hash is of the exact branch name, so those two get different files. One file
per branch, so two branches never append to the same file and never
conflict. The files land on `main` with each pull request and stay there.

**This branch's entries** are the blocks the file did not have at the merge
base: the whole file if `git show "<merge base>:<chart>"` fails, otherwise the
blocks added since. A reused branch name therefore starts clean, and older
blocks in the same file stay as history.

**Format.** A header, then one block per rule change. Field names are fixed:

```markdown
# Rule changes on dev/someone/store-credit

<!-- rule-change chart format: 1 -->

## REFUND-05 · billing/refunds.system-spec.md
- branch: dev/someone/store-credit
- status: recorded — openspec/changes/store-credit/design.md, added in 1c0d2e4
- old: "A refund goes back in the currency of the charge."
- new: a refund can go to store credit in the account currency
- where: billing/credit.py:20-41
- decision: spec updated
- decided: 2026-10-27, by the user, at the pull request

## REFUND-02 · billing/refunds.system-spec.md
- branch: dev/someone/store-credit
- status: acknowledged — by the user at commit time
- old: "A refund never exceeds the captured amount."
- new: refunds up to the authorized amount when capture is partial
- where: billing/reducer.py:88-104
- decision: skipped — open change
- decided: 2026-10-27, by the user, at the pull request
```

- **An entry is one rule change on one branch**, named by its heading
  `<rule ID> · <spec path>`. A second entry for the same rule in the same
  file adds ` · 2` to the heading, then ` · 3`, so every heading in a file
  is unique. No commit field: the commits that carried the change are the
  ones that touched the entry's lines, the first and every later edit:

  ```bash
  H='## <heading>'
  N=$(git show HEAD:"$CHART" | grep -n -F -x "$H" | cut -d: -f1)
  [ -n "$N" ] || { echo "chart heading not found: $H"; exit 1; }
  E=$(git show HEAD:"$CHART" | awk -v n="$N" 'NR > n && /^## / { exit } NR >= n && NF { e = NR } END { print e }')
  git log --format=%h -s -L "${N},${E}:${CHART}"
  ```

  A heading that is not found, for example one with a trailing space, stops
  the lookup with that line; with an empty start, `git log -L` would list
  the wrong lines and still exit 0. The range ends at the entry's last non-blank line before the next
  heading, however many blank lines sit between entries, so an edit to the
  last field is listed. `git log -S` on the heading is not enough: it lists
  only the commit that added the heading, not one that later extended the
  entry.
- **status** is one of:
  - `recorded — <change doc path>, added in <sha>`: a change doc approved it
    under the brief's rule;
  - `acknowledged — by the user at commit time`: the user confirmed the break
    was intentional;
  - `not seen at commit time`: written only by a pull-request workflow
    skill, when one is installed, for a change its branch re-check found
    with no entry.
  A later commit that breaks the same rule while its newest entry is
  undecided extends that entry: its `where` and a different status go on
  the same lines, after the first, joined by `; `. Its behavior goes on a
  new `- new:` line below the last one, unless one already says it, in
  meaning. Behaviors are never joined on one line: a sentence can itself
  hold a `; `. Once that entry is decided, a later break is a new entry.
- **decision** and **decided** are absent until the rule is settled: at the
  pull request by a workflow skill when one is installed, otherwise when the
  person settles it in a hand run. `decision` is one of `spec updated`,
  `kept old behavior`, `skipped — open change`, or `no longer on the branch`.
  `decided` is the date and who decided: `by the user, at the pull request`,
  `by the user, in a hand run`, or `by the branch re-check` for
  `no longer on the branch`.
- `old` quotes the rule as committed before the change. `new` and `where`
  come from the brief's answer. An entry has one `- new:` line per
  behavior.

**Lifecycle.** Entries are written, then decided, never removed or rewritten.

1. **Written at commit time, in the same commit.** `bug-hunter` writes one
   entry per rule change it let through and stages the file before the
   commit is minted, so the entry and the code land together and the binding
   covers both. Under "caller commits" the entry is staged before the result
   block is minted, and the caller commits it with the rest. A run that does
   not commit writes nothing.
2. **Decided later, with the decision's effect.** Without a workflow skill,
   entries stay undecided until the person settles them in a hand run of
   `maintain-system-spec` and records each decision, committed with the spec
   edit or fix it records. When a pull-request workflow skill is installed,
   it reads this branch's entries, merges them with its
   branch re-check, and writes `decision` and `decided` into each one it
   settles. A break joins an entry when the rule matches and its new
   behavior matches one whole `- new:` line of the entry, by meaning, not
   exact words. An undecided entry is `no longer on the branch` only when
   no break on the branch matches any of its `- new:` lines. A rule with no
   matching entry gets
   one, status `not seen at commit time`, and is asked about, even when an
   earlier entry for the same rule is decided. A decision is written only
   for work a sub-agent reported done; a `could not`, a time-out, or a
   missing report leaves the entry undecided. Each chart edit is committed
   with the spec edit or fix it records. That commit adds no new entry for a
   rule it decides, whichever answer it carries: a skip's restored rule text
   is the skip, not a new break.
3. **Kept.** A decided entry is closed. A later break of the same rule on
   the same branch adds a new entry below it, with the next heading number,
   undecided, so it is asked about when the rule is next settled.

**The chart is a record, not evidence.** Nothing reads it as approval. An
`acknowledged` status here is not the user's reply in a later conversation,
and a workflow skill re-checks the branch from git and asks the person
about every rule, whatever the chart says. `maintain-system-spec` may read
it to show when and why a rule changed. It edits an entry only to write a
decision the person gave in a hand run and asked it to record.

**It is not a spec.** Files under `system-spec-changes/` are never due, never
a break, and never a spec edit. A commit that touches only them is a docs
change, so triage skips it.
