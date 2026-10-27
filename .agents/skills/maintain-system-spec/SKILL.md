---
name: maintain-system-spec
description: >-
  Check a repo's system specs against the code and keep them current. One
  read-only sub-agent per due spec checks every rule; the main agent fixes
  stale specs, reports code that breaks a rule as a probable bug, holds any
  looser rule for the person to confirm, and updates the root SYSTEM_SPECS.md
  index. Use when the user asks to check, verify, update, maintain, or audit
  system specs, add a spec for uncovered code, split a spec, or move rules
  from an archived OpenSpec change into a system spec. A pull-request
  workflow skill, if you have one, can run it in branch mode on the specs a
  branch touches. Never edits product code and never commits.
---

# Maintain system specs

Check each due system spec against the code. Fix the spec where the code
changed on purpose. Report code that breaks a rule. Stop after the report.

This is not `create-system-spec`. That one sets up specs in a repo once.
This skill also adds specs for code that has none. It is not OpenSpec,
which records proposed and archived changes, and it is not a security
scan that looks for attack paths.

Spec and master formats: [format.md](format.md). Sub-agent prompts:
[records.md](records.md). Why each rule is the way it is:
[DECISIONS.md](DECISIONS.md).

[rule-check.md](rule-check.md) holds the system-spec rule check and the
rule-change chart, a committed log under `system-spec-changes/`, that
`bug-hunter` uses, and a pull-request workflow skill too when one is
installed. This skill does not run that check; it keeps the brief because
the brief reads specs in this skill's format.

The workflow skill is optional and not in this repository. Without it, the
person settles rule changes by running this skill themselves, and chart
entries stay undecided until they do.

## Hard stops

- Do **not** run without a `SYSTEM_SPECS.md` that has the format marker. Suggest `create-system-spec`. In branch mode, return `skipped: no system specs` instead.
- Do **not** edit product code. Edit only spec files and `SYSTEM_SPECS.md`.
- Do **not** commit, push, or open a pull request. Edits stay uncommitted for review.
- Do **not** let a sub-agent write. Only the main agent writes.
- Do **not** rewrite a rule to match code that breaks it. Report it as a probable bug.
- Do **not** add an `Open change:` line on your own. A pull-request workflow skill writes one when installed. Without one, add it only in a hand run, when the person answers *skip for now* for that rule and chooses to record the skip. Do **not** settle an open change without the person's answer.
- Do **not** edit files under `system-spec-changes/` on your own. They are a committed log. A workflow skill writes chart decisions when installed; without one, write a decision into an entry only when the person gives it in a hand run and asks you to record it.
- Do **not** write a looser rule until the person confirms it.
- Do **not** split a spec, or draft a new one, until the person approves it.
- Do **not** move a spec's last verified commit unless [Step 7](#step-7--write-edits-and-update-the-master) allows it.

## Checklist

```
Maintain system specs:
- [ ] Step 1: Name the repo and the mode
- [ ] Step 2: Load the master index
- [ ] Step 3: Index hygiene, and list open changes
- [ ] Step 4: Pick the due specs
- [ ] Step 5: Check each due spec in its own read-only sub-agent
- [ ] Step 6: Spot-check and decide each rule
- [ ] Step 7: Write edits and update the master
- [ ] Step 8: Report the outcome, then stop
```

## Step 1 — Name the repo and the mode

Use the git repository that contains the work in front of you. If several
repos are open, ask which one, then end the turn. Say its `owner/repo`.

Pick the mode:

- **Branch mode:** the caller says so, as a pull-request workflow skill
  would (none is included in this repository). Check only
  the specs this branch touches.
- **On demand:** anything else. Check the specs the person names, or every
  due spec when they name none. "Check every spec" names them all.

Run `git fetch origin`. The default branch is the one `origin/HEAD` points
at (`git symbolic-ref --short refs/remotes/origin/HEAD`, such as
`origin/main` or `origin/master`). Read only files git tracks, plus new files on
this branch: list them with `git ls-files` and
`git ls-files --others --exclude-standard`. Gitignored build output such as
`infra/cdk.out/`, `target/`, and `build/` holds stale copies of source and
specs.

## Step 2 — Load the master index

Read `SYSTEM_SPECS.md` at the repo root. If it is missing, or lacks the line
`<!-- system-specs format: 1 -->`:

- On demand: say so, suggest `create-system-spec`, and stop.
- Branch mode: return `skipped: no system specs`.

## Step 3 — Index hygiene

Compare the master with the spec files on disk
(`git ls-files --cached --others --exclude-standard ':(glob)**/*.system-spec.md'`).
Fix these in the master:

- **Missing:** a row whose spec file does not exist. Remove the row, unless
  git shows the file was renamed: then fix the path.
- **Extra:** a spec file with no row. Add a row with last verified `never`.
- **Duplicate:** two rows for one file. Keep one.
- **Dead:** a Covers glob that matches no file. Where git reports a rename,
  update the glob in the spec and the master. Otherwise list it in the report.

Also report, without fixing:

- two specs that use the same ID prefix, or one ID used twice
- old-format specs still in the repo (`system_spec.md`, or a
  `*.system-spec.md` with no Rules section)
- a rule file that keeps its own list of specs instead of linking the master

**Open changes.** List every rule that carries an `Open change:` line, in any
spec, due or not:

```bash
git grep -n -E '^[[:space:]]+- Open change: .+, [0-9]{4}-[0-9]{2}-[0-9]{2} — ' -- ':(glob)**/*.system-spec.md'
```

The pattern is the field's own form ([format.md](format.md#open-changes)),
so a rule, a Reason or a link that only mentions the words is not listed.
The branch part is `.+`, not `[^,]+`: git allows a comma in a branch name.

Each one is a rule the code and the spec disagree on, left open by a
recorded skip ([format.md](format.md#open-changes)). For context, the chart entry
for that rule, if there is one under `system-spec-changes/`, says when it was
skipped and what changed; show it, but nothing here depends on it. Every run reports them first,
until none remain. On demand, its spec is due (Step 4), so a check sub-agent
reads whether the code still breaks it.

## Step 4 — Pick the due specs

**Changed files.**

- On demand: run `git diff -M --name-status <oldest last verified commit>..HEAD`
  once. A spec at `never` counts every scope file as changed.
- Branch mode: take the merge base with the default branch,
  `base=$(git merge-base "$(git symbolic-ref --short refs/remotes/origin/HEAD)" HEAD)`,
  then join `git diff -M --name-status "$base"..HEAD`,
  `git diff -M --name-status HEAD`, and
  `git ls-files --others --exclude-standard`. If `git merge-base` fails or
  prints nothing, stop and return `blocked: no merge base with the default branch`.
  Not `skipped`: with an empty base, `"$base"..HEAD` compares `HEAD` with
  itself, prints nothing, and exits 0.

Where git reports a rename of a file a Scope glob names, update the glob in
the spec and the master.

**Due specs.**

| Mode | A spec is due when |
|------|--------------------|
| On demand | The person named it; or a scope file changed since its last verified commit; or it was last verified 4 or more weeks ago; or its last check was partial; or it is `never`; or a rule in it has an `Open change:` line |
| Branch | A changed file matches its Covers globs; or it has a repo-wide rule and a changed file is code |

In branch mode, a spec due only because of a repo-wide rule checks only its
repo-wide rules. If no spec is due in branch mode, skip Steps 5–7 and go
directly to [Step 8](#step-8--report).

**Uncovered changes.** A changed source file that no spec covers and no
`Uncovered` entry names: add its folder to `Uncovered`. If it looks like it
holds rules, propose a spec for it in the report. Skip docs, tests, and
generated files.

## Step 5 — Check each spec

Launch one read-only sub-agent per due spec, all at once:

| Tool | Sub-agent |
|------|-----------|
| Cursor | The `explore` type, asked to be "very thorough". Cursor's Task tool has no read-only flag. |
| Claude Code | A read-only agent type, if one is available |
| Anything else | A general sub-agent. The prompt's read-only line is the only guard. |

Give each one the [check prompt](records.md#check-prompt), filled in for its
spec. Wait for all of them before Step 6.

If you cannot launch sub-agents, for example because you are already a
sub-agent and your tool does not allow nesting, check the specs one at a
time yourself, with the same prompt and the same read-only limits. Say so in
the report.

## Step 6 — Spot-check and decide

**Check before acting:**

- Read each Coverage line. If a sub-agent claims full but lists a file read
  partly or not at all, or gives no count of files read completely out of
  files to read, count the check as partial. Only a full claim with that
  count, and every file read, is full coverage.
- Open the cited code for every `spec is stale` and every `code breaks it`
  verdict, and confirm it. Do not re-prove `holds`.
- You may run a rule's enforcing test to confirm a verdict, when the repo's
  test command is known and quick. That raises its evidence to `test run`.
- Where a sub-agent's verdict does not survive your check, change it and say
  why in the report.

**Decide each rule:**

| Verdict after your check | What to do |
|--------------------------|------------|
| holds | Nothing. Fix the Evidence line if the cited line moved. If the rule has `Open change:` lines: on demand, with full coverage after your check, the code was changed back, so remove them. In branch mode, or with partial coverage, leave them and list the rule under Open changes as holding where read |
| code breaks it | Report a probable bug with `file:line`. Leave the rule as it is. If the rule has an `Open change:` line, report it under Open changes instead, not as a bug |
| spec is stale, stricter or wording only | Edit the spec |
| spec is stale, looser | Do not edit. Report it as held for the person to confirm |
| can't verify | Report it with the reason |

A looser change allows more, checks less, widens a contract, or removes a
rule. Removing a rule moves its ID to the `Retired:` line, once confirmed.

**Decide the rest:**

- **Inferred rule now shown:** replace `(inferred)` with the cited line.
- **Missing rule:** add it with the next unused ID when the code shows it
  clearly. A missing rule makes the spec stricter.
- **Scope gap:** add a file that keeps or breaks a rule to Scope. Removing a
  glob that still matches files is looser: hold it.
- **Format violation:** fix it. Delete signatures, inventories, history,
  `TEMPORARY` notes, plans, and `Version` or `Last updated` headers. Replace
  position references with IDs.
- **Encodable rule:** propose the test, type, or lint rule in the report. Do
  not write it.
- **Oversized spec:** over the [size cap](format.md#split-rules). Propose a
  split in the report. Do it only after approval.
- **Same rule in two specs:** keep it in one, link it from the other. If the
  two say different things, hold it as looser.

## Step 7 — Write edits and update the master

Write the spec edits. Re-read each changed spec once against
[format.md](format.md).

Update the master row of each checked spec:

- **Last check:** `full` or `partial`.
- **Last verified:** move to the short `HEAD` commit and today's date only
  when all of these hold:
  - coverage was full after your check
  - no rule is broken by the code, and no looser change is held
  - `HEAD` equals `origin/main`, on `main` or detached
  - covered code files have no uncommitted changes other than comments
    (`git diff HEAD -- <scope files>`; spec files do not count)

In branch mode, none of this applies: leave Last check and Last verified as
they are. Branch commits may never reach `main`. Branch mode still writes
spec edits, glob renames, and `Uncovered` entries.

Never edit product code. Never commit.

## Step 8 — Report

Start with the outcome, exactly one of:

- **clean:** no spec edits, no rule broken, nothing held. Moving Last verified
  and Last check forward does not count as an edit.
- **changed:** spec edits made. List them.
- **blocked:** no spec edits, but the specs are not current. Say what blocked
  it: a rule the code breaks, a looser change waiting for confirmation, an
  open change the code still breaks (on demand only), or a check that could
  not run. In branch mode, and for an open change not checked this run, open
  changes are listed and do not change the outcome.

In branch mode, a run with nothing to check returns `skipped: <why>` instead.

Then, before anything else, **Open changes**, whenever Step 3 found any:
rule ID, spec, each `Open change:` line, and whether the code still breaks the
rule (or "not checked this run"). On demand, settle each one after the report
([Settling an open change](#settling-an-open-change)). In branch mode, list
them; the caller asks.

Then, leaving out empty sections:

1. **Code breaks a rule:** rule ID, spec, `file:line`, one sentence. These
   are probable bugs.
2. **Held for confirmation:** rule ID, the looser edit, and the `file:line`
   that shows why.
3. **Spec edits made:** spec, rule IDs, what changed.
4. **Index fixes:** what Step 3 changed, and what it reported.
5. **Proposals:** new specs for uncovered code, splits, rules to encode as a
   test, type, or lint rule.
6. **Can't verify:** rule ID and why.
7. **Coverage:** each spec checked, full or partial, and whether its Last
   verified moved.

End with: the edits are uncommitted. Review and commit them in a pull
request. Then stop.

## Confirming a held change

When the person confirms a held looser change, make that edit and say it is
uncommitted. When they reject it, leave the rule: the code is what needs to
change. Nothing records a rejection, so later checks report it again until
the code is fixed.

## Settling an open change

On demand, after the report, ask about each open change the code still
breaks, one question per rule, with the host's picker when it has one, and
end the turn:

**`<RULE-ID>` has an open change from `<branch>`: <the new behavior>. Settle it?**

A rule with lines from several branches is one question that names each
branch and behavior.

- Update the rule — rewrite it to the new behavior, remove its `Open change:` lines
- Change the code back — the code is yours to change; the rule stays

On *update the rule*, the main agent rewrites the rule in place and keeps
its ID, points `Enforced by` and `Evidence` at what the check sub-agent
cited, and removes the lines. This is a looser edit the person confirmed, so
it is written. On *change the code back*, edit nothing: this skill never
edits product code. The lines stay until an on-demand run with full coverage
finds the rule holds; then Step 6 removes them. A branch-mode run, or one
with partial coverage, reads only part of the code, so its `holds` leaves
them. An open change with no answer stays, and the next run asks again.
Edits are uncommitted, as always.

## Approved proposals

**Split a spec.** After approval, launch one sub-agent per new spec with the
[draft prompt](records.md#draft-prompt), passing the old spec. Rules keep
their IDs when they move. Write the new specs, delete the old one, update the
master and every link to the old path, then check the new specs with Step 5.

**New spec for uncovered code.** After approval, draft it the same way with a
new prefix, add a master row at `never`, remove its folder from `Uncovered`,
then check it with Step 5.

## Moving rules in from an OpenSpec change

When the person asks to move an archived OpenSpec change into the system
specs:

1. Read the change under `openspec/changes/archive/<change>/`, including its
   `specs/` deltas.
2. Pick the lasting rules: requirements the current code must keep. Skip
   tasks, rollout steps, and plans.
3. Find the spec whose scope covers each rule. If none does, propose a new
   spec.
4. Check each rule against the code, citing `file:line`, the same way as
   Step 6. An added rule makes a spec stricter: write it with the next
   unused ID. A modified or removed requirement that loosens an existing rule
   is held.
5. Leave the OpenSpec files as they are. Report the IDs written and held.
