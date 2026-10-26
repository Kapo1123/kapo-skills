---
name: create-system-spec
description: >-
  Set up system specs in a repo for the first time. Surveys the code with
  read-only sub-agents, proposes a split by concern, and after approval
  writes <concern>.system-spec.md files and a root SYSTEM_SPECS.md index,
  restructures old system_spec.md and *.system-spec.md files into the new
  format, and relinks AGENTS.md and other rule files. Runs once per repo,
  then proves the result with maintain-system-spec, which must be installed.
  Use when the user asks to create, set up, bootstrap, or migrate system
  specs, or write system specs for a repo with no SYSTEM_SPECS.md. Does not
  run when SYSTEM_SPECS.md already exists; use maintain-system-spec then.
  Leaves everything uncommitted.
---

# Create system specs

Set up system specs in one repo, once. Survey the code, propose which
concerns get a spec, and stop for approval. Then draft the specs from the
code, write them with the master index, relink every rule file, and prove
the result by running `maintain-system-spec` once. Stop after the report.

Later upkeep, and specs for code that has none yet, belong to
`maintain-system-spec`.

The format is in `maintain-system-spec`:
[format.md](../maintain-system-spec/format.md). Read it before Step 4. This
skill needs `maintain-system-spec` installed. The survey prompt is in
[prompts.md](prompts.md). Why each rule is the way it is:
[DECISIONS.md](DECISIONS.md).

## Hard stops

- Do **not** run when `SYSTEM_SPECS.md` has the line `<!-- system-specs format: 1 -->`. Tell the person to use `maintain-system-spec`, which also adds specs for gaps.
- Do **not** run unless `maintain-system-spec` is installed. Check that [format.md](../maintain-system-spec/format.md) can be read. If not, tell the person to install it, then end the turn.
- Do **not** run unless `HEAD` equals `origin/main` and tracked files have no changes.
- Do **not** draft a spec until the person approves the split. Propose, then end the turn.
- Do **not** let a sub-agent write. Only the main agent writes.
- Do **not** edit product code, except comment lines that name an old spec path or cite a rule by position.
- Do **not** drop a rule from an old spec without listing it in the proposal or the report, with the reason.
- Do **not** commit, push, or open a pull request.
- Do **not** ask the person what the repo can show.

## Checklist

```
Create system specs:
- [ ] Step 1: Name the repo and check the tree
- [ ] Step 2: Inventory existing specs and rule files
- [ ] Step 3: Survey the code in read-only sub-agents
- [ ] Step 4: Propose the split — then stop for approval
- [ ] Step 5: Draft each spec in its own read-only sub-agent
- [ ] Step 6: Write the specs, the master, and the links
- [ ] Step 7: Prove it with maintain-system-spec
- [ ] Step 8: Report, then stop
```

## Step 1 — Name the repo and check the tree

Use the git repository that contains the work in front of you. If several
repos are open, ask which one, then end the turn. Say its `owner/repo`.

Read `SYSTEM_SPECS.md` at the root, if there is one. If it has the format
marker, stop: see Hard stops.

Run `git fetch origin main`. Refuse to run, and say why, unless both hold:

- `HEAD` equals `origin/main`, either on the branch `main` or detached
- `git status --porcelain --untracked-files=no` prints nothing

Tell the person what to run to fix it, then end the turn:

- **No work in progress:** `git switch main && git pull`.
- **Work in progress:** `git worktree add --detach <path> origin/main`, then
  run the skill from `<path>`. Do not create the worktree yourself.

Read only files git tracks: list them with `git ls-files`, not `rg --files`.
Gitignored build output such as `infra/cdk.out/`, `target/`, and `build/`
holds stale copies of source and specs.

## Step 2 — Inventory

List, with paths:

- **Existing specs:** `git ls-files | rg -i 'system[-_]spec'`, and a
  `SYSTEM_SPECS.md` without the marker.
- **Rule files:** `AGENTS.md`, `CLAUDE.md`, `.cursorrules`,
  `.github/copilot-instructions.md`, `.cursor/rules/*.mdc`, and any of these
  in subfolders.
- **Constitution:** `.specify/memory/*.md`.
- **OpenSpec:** `openspec/specs/**`.
- **References to old specs:** `git grep -n -i -e 'system_spec' -e 'system-spec'`.
  These are the lists, links, and comments Step 6 must update. Also note
  references that cite rules by position, such as "invariants 1–2".
- **Source areas:** the tracked source directories, with file and line
  counts (`git ls-files <dir> | xargs wc -l`). Split a directory over about
  50 files or 8k lines one level down. Each area is one survey sub-agent.

## Step 3 — Survey the code

Launch one read-only sub-agent per source area, all at once:

| Tool | Sub-agent |
|------|-----------|
| Cursor | The `explore` type, asked to be "very thorough". Cursor's Task tool has no read-only flag. |
| Claude Code | A read-only agent type, if one is available |
| Anything else | A general sub-agent. The prompt's read-only line is the only guard. |

Give each one the [survey prompt](prompts.md), filled in for its area, with
the existing specs, rule files, and OpenSpec specs that mention it. Wait for
all of them before Step 4.

Read each Files read line. Where a sub-agent read part of its area, note it:
the drafts in Step 5 read those files again.

## Step 4 — Propose the split

Read [format.md](../maintain-system-spec/format.md). Group the rules the
survey found into concerns, using its
[split rules](../maintain-system-spec/format.md#split-rules).

**What comes first.** Propose specs for the 3 to 5 riskiest concerns, plus
every existing spec restructured into the new format. Riskiest means a
broken rule would harm people or money most: authentication and sessions,
payments, personal data, request signing, data other repos rely on. Every other source area goes under `Uncovered`, so later runs of
`maintain-system-spec` can add specs there.

**Existing specs.** Restructure every one into the new format. For each,
say whether it is renamed, merged into another spec, split into several, or
retired because it holds no rules. Name where its rules go. List any real
rule that would have no home, and why.

Show the proposal in this order:

1. **Specs**, one block each: path, concern and one-line purpose, ID prefix,
   Scope globs, source (new, or restructured, merged, or split from which old
   spec), about how many rules, and why it is in the first set.
2. **Old specs:** each old path, and what happens to it.
3. **Rules with no home:** old rules that would be dropped, and why.
4. **Uncovered:** source folders left without a spec.
5. **Links to update:** rule files and the number of code comments and docs
   that point at old spec paths or cite rules by position.
6. **Questions:** only what the code cannot answer, such as whether a
   behavior is intended. Most proposals have none.

Then ask, and end the turn:

**Approve this split, or tell me what to change?**

Change the proposal as asked and show it again until the person approves.

## Step 5 — Draft each spec

Run the Step 1 tree check again first: the person may have changed the
checkout since the proposal.

Launch one read-only sub-agent per approved spec, all at once, with the same
sub-agent type as Step 3. Give each one the
[draft prompt](../maintain-system-spec/records.md#draft-prompt), filled in
from the approved split: its old specs, the rules that move in from other old
specs, and the specs it should link to instead of restating. Sub-agents
return the draft text. They do not write files. Wait for all of them.

**Check each draft:**

- Every rule has an ID with its prefix, an `Enforced by` line, and an
  `Evidence` line that cites `file:line` or says `(inferred)`.
- Nothing the format forbids: signatures, inventories, history, plans,
  `Version` or `Last updated` headers, position references.
- Within the size cap. If a draft overflows, propose a split and wait.
- Every statement in each old spec appears in some draft's Carried list. A
  real rule marked dropped needs a reason the person saw in Step 4, or it goes
  in the report.
- No rule is written in two drafts. Keep it in one and link it from the
  other.

Open the cited code for any rule whose evidence looks doubtful. Step 7 checks
every rule, so you do not need to prove them all here.

## Step 6 — Write

Write in this order. Do not stage or commit anything.

1. **Spec files** at their approved paths.
2. **Old specs:** delete each old spec file once every rule in it is carried,
   merged, or listed as dropped. Use a plain delete or move, not `git mv`,
   which stages the change.
3. **`SYSTEM_SPECS.md`** in the [master format](../maintain-system-spec/format.md#master-index),
   with the format marker. Every row starts at Last verified `never` and
   Last check `—`. List `Uncovered` folders.
4. **Rule files:** in each rule file and constitution, replace any list of
   specs with a link to `SYSTEM_SPECS.md`, as in
   [Links from rule files](../maintain-system-spec/format.md#links-from-rule-files).
   Keep the file's own wording of the obligation.
5. **Other references:** in code comments and docs, replace old spec paths
   with the new spec path, and positions with rule IDs. Change only the
   comment text.

Then run the Step 2 reference search again for every old spec path. Each hit
left is either fixed or listed in the report.

## Step 7 — Prove it

Follow `maintain-system-spec` on demand, naming every new spec. A spec no one
has checked against the code is a draft.

Act on its results as that skill says: it edits stale specs, reports rules
the code breaks as probable bugs, and holds looser changes. It moves Last
verified only for specs it checked in full with no rule broken.

If it is `blocked` because it could not run, fix what blocked it and run it
again once. If it still cannot run, say so in the report.

## Step 8 — Report

In this order, leaving out empty sections:

1. **Specs written:** path, rule count, how many are enforced and how many
   are `unenforced` or `(inferred)`, and Last check.
2. **Code breaks a rule:** from Step 7: rule ID, `file:line`, one sentence.
   These are probable bugs.
3. **Held for confirmation:** from Step 7.
4. **Old specs:** each old path, and where its rules went.
5. **Rules dropped:** old rule and why.
6. **Links updated:** rule files, and how many comments and docs. Any old
   reference left, with its path.
7. **Uncovered:** folders with no spec yet.
8. **Questions:** anything still open.

End with: everything is uncommitted in `<checkout path>`. Create a branch
and commit it through a pull request, for example
`git switch -c docs/system-specs`. From now on, `maintain-system-spec` keeps
the specs current; run it before each pull request.

Then stop.
