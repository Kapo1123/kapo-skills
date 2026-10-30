---
name: bug-hunter
description: >-
  Catch bugs in code the user has asked you to commit. Start only when they
  tell you to commit now — "commit this", "commit my changes", "let's
  commit", "wrap this up and commit" — or when they ask for this skill by
  name: "bug check this", "run bug-hunter", "prevent bugs", "find bugs
  before I commit". A summary, an explanation, or a request for the commit
  message is not a commit. The user is still reading and may still change
  the code, so do not start. Do not start because you expect a commit
  later. If another skill makes the commits and runs this one before each
  of them, let it.
  Finds candidate bugs in the staged change, proves each one with a
  regression test that actually fails, refutes the weak ones, fixes what
  survives, and re-verifies. Light by default; a heavy hunt, with four
  finders on every pass, only when the user asks for one. In a repo with system specs, a separate
  system-spec rule check records each rule change in a committed log,
  and pauses the commit for the user on any break no change doc approved.
  Docs, specs, tests and work-in-progress commits
  skip the hunt, not this skill — they still commit through its script,
  carrying a `Bug-hunter: skipped` trailer. When a caller's brief says
  "caller commits", run in full but do not commit: leave the change staged and
  return the trailer lines and any open decisions for the caller to use. Do
  not use for reviewing someone else's PR or reviewer comments — use a code
  review for that.
---

# Bug Hunter

**A claim with no failing test is a guess.** Everything this skill reports is
proven by a test observed red before the fix and green after; everything it
cannot prove is dropped. That is the whole idea, and the reason its output is
worth reading.

It edits the working tree, adds test files, and by default commits.

- **How to do each step** — [reference.md](reference.md). Read it before Steps
  4–7, before writing a report, and before committing.
- **Why any of this is the way it is** — [DECISIONS.md](DECISIONS.md). Read it
  before changing this file or `scripts/`. It is about this skill; the record
  Step 6 reads before a fix is the codebase's own.

## The contract

1. Every fixed bug has a regression test that was **observed red** on the
   unfixed code and green after the fix.
2. Every candidate that cannot be driven red, or that a second opinion
   refutes, is **dropped** — and its test is deleted, never left failing.
3. Anything real but out of scope or untestable is **reported, not fixed**.
4. The full test suite ends no worse than it started.
5. No commit lands over a system-spec rule break that neither a committed
   change doc nor the user approved.

## Workflow checklist

```
- [ ] Step 0: Scope the change — staged diff only
- [ ] Step 1: Triage — is this commit worth reviewing at all?
- [ ] Step 2: Baseline — run the suite before touching anything
- [ ] Step 3: Find candidates — light by default, heavy only when asked; 1, 2 or 4 finders by changed lines (heavy: 4), then merge without re-reading
- [ ] Rule check: the system-spec rule check in its own subagent, launched with the finders — or one line saying the repo has no system specs
- [ ] Step 4: Prove — write the test, run it, demand a matching red
- [ ] Step 5: Refute — a second opinion tries to kill each proven bug
- [ ] Step 6: Fix (resume this iteration's finder, prevention question, scope-confined)
- [ ] Step 7: Verify — new tests green; the full suite once, before Step 9; stage this iteration's fixes and tests
- [ ] Step 8: Iterate — back to back, up to 3, without asking; never a 4th; light runs read the fixes' delta, settled candidates are not re-hunted
- [ ] Step 9: Report once at the end; ask the user each open decision (picker — written is not asked); then commit (with prose's trailer when prose is installed) or leave it for review — or, under "caller commits", end with `scripts/caller-result.sh`'s block
- [ ] Before any commit, mint or result block: the rule check has returned (or the user decided what to do about a failed one), and every paused system-spec rule break has the user's answer (continue / stop and fix)
```

Never run this from inside a git `pre-commit` hook. It writes files, adds
tests, and commits — all of which fight git's index lock. It runs **before**
the commit is created, and the commit happens at Step 9.

A companion hook watches for commits that never came through here: after each
command it asks git whether HEAD moved and whether the new commit carries a
`Bug-hunter:` trailer. So **the trailer is the only marker that matters** — no
environment variable, nothing to remember, and the record lives in the commit
itself where `git log` can audit it.

The hook also asks a second question of any trailer that is not itself a skip
note — `0 bugs found` and `aborted ...` included, not only ones reporting a
fix: does a `Bug-hunter-Tree` trailer match the tree that actually landed? That
binding is what [`scripts/mint-trailer.sh`](scripts/mint-trailer.sh) produces
when run against the real staged tree, right before the commit — see [Step
9](#step-9--report-and-commit) for how, and
[the shared library's DECISIONS.md](../../lib/commit-trailer/DECISIONS.md#the-trailer-is-minted-from-the-tree-not-recalled-by-the-agent)
for why. A `Bug-hunter:` trailer can be a real git trailer with exactly the
right wording and still be a sentence recalled from having read this file,
rather than one produced by running any part of it — that is the one shape
the string-presence check cannot catch, and the one this binding is for.

A commit that lands without a `Bug-hunter:` trailer at all gets named
in a report, with the repository it is in, and nothing else: the hook cannot see
where you are standing, and the commit it names is often not your HEAD.

---

## If you are an agent about to commit

If another skill makes your commits and runs this skill before each of them,
let that skill start from "commit this"; still run for "bug check this". If
this turn already stated a commit subject, use that subject unchanged. Only add
trailers.

**Run this skill only after the user asks you to commit this code now, or asks
for this skill by name.** "Commit this", "commit my changes", "let's commit",
and "wrap this up and commit" mean: stage the change, run this skill, then
commit. "Run bug-hunter", "bug check this", "prevent bugs", and "find bugs
before I commit" mean the same hunt.

A summary, an explanation of the changes, or "write the commit message" does
not start this skill. The user is still reading and may still change the code.
Give them that and stop. Do not stage the change for a hunt, and do not start
the finders.

Your own guess that a commit is coming does not start it. Wait until they say
to commit.

Triage (Step 1) still decides whether a commit they asked for is worth
reviewing. A docs-only commit is cheap to skip. Run that skip only after
they ask to commit.

### Do not evade this skill

One heading, not five rules, because an agent looking for a way out of a check
reliably finds the seam between separately-stated rules. Every line here was
added after it was walked through — the record is in
[DECISIONS.md](DECISIONS.md#every-anti-evasion-rule-was-added-after-it-was-walked-through).

**1. When a run is owed, say which one you are doing, out loud.** One line in
the reply the user can see: **"running bug-hunter on N files"**, or **"skipping
bug-hunter — <reason>"**. Not in your reasoning — in the reply. Skipping while
saying nothing looks exactly like running it and finding nothing. A stated skip
can be overruled in four words; an unstated one is a decision you made for them.
If you skip, the commit carries the trailer too — `commit-with-trailer.sh
<subject> <body> "skipped — <reason>"`, as in [Step
9](#step-9--report-and-commit). Both, not either. Under *caller commits*, the
skip goes to the result script instead ([When the caller
commits](#when-the-caller-commits)). When no run is owed, do not announce a
skip. There is nothing to skip.

**2. After they ask to commit, or ask for this skill, do not ask permission to
run it.** Inside that run, a pass is owed when code has been written since the
last pass that came back clean: between iterations, after a fix they asked for
during the run, after a refactor of the change being committed. A list of
moments inside the run invites hunting for the moment that is not on it.

Outside that run, new code does not start the hunt. A question, a summary,
or a commit message leaves the hunt stopped.

**3. When a run is already owed, announcing only counts if you have already
started.** *"That's running next unless you want to stop here"* · *"I'll kick
that off if you're happy with it"* · *"the fixes need their own pass — want me
to run it?"* Each ends the turn with the check not running, which hands back
the decision as plainly as asking would. **If a run is owed and you are
describing it in the future tense, you have not started it, and that is the
bug.** When they have not asked to commit and have not asked for this skill,
answer the question. Do not start a run.

**4. Iterations run back to back, and the report is owed.** Up to three, no
check-in between them, and no interim report — a report between iterations
invites stopping early and makes an unfinished run look finished. See Steps 8
and 9.

**Three is the budget, not an opening offer. There is no fourth iteration.**
*"want me to run one more pass?"* · *"iteration 3's own fixes never got
reviewed — shall I do a 4th?"* Both hand back a decision the budget already
made, at the moment the user is most likely to say no. A run that caps out ends
in the root-causes report (Step 9) and one choice per cause, where the first
choice is a **new run at iteration 1** scoped to that cause. That is not rule 2
suspended: a pass over iteration 3's fixes really is owed, and it is still owed
— what ran out is the budget for taking it *inside this run*, which is why it
becomes a new run and why which cause gets it is the user's call. Nor is it rule
3 reversed: inside the budget a pass is owed and you start it without asking;
at the cap the run is over, and what is left is a decision, offered as options
rather than as an open question.

**5. These are not reasons.** Every one has been used, by a capable model, to
skip this skill on a commit that then shipped a bug:

- *the change is small* — one-line changes are wrong all the time
- *I am confident in this code* — so was every author of every bug this has found
- *the user is waiting / we are moving fast* — that is the moment quality gets
  traded away, which is the moment this exists for
- *the session is long and this is expensive* — a run that finds nothing is
  cheap, triage stops most commits before the expensive part, and a large find
  is a few parallel slices rather than one agent walking the whole diff (Step 3)
- *heavy costs more than this needs* — heavy is the user's call, made when
  they asked for it; a heavy run is never dropped to light
- *I already ran it on related code earlier* — you did not run it on this
- *this is the skill's own machinery, not real code* — it is real code, and the
  worst bugs in this skill's own history have been in exactly that machinery
- *the user is clearly watching and would object if they minded* — they are
  watching the output, not the absence of it

Creating bugs and moving on because checking was inconvenient is the specific
behaviour this skill exists to stop. Doing it *to* this skill is not irony, it is
just the bug.

**Whose call the cost is.** A full run is minutes; a bad one is half an hour.
Whoever installed this already weighed a slower commit against a bug reaching
main. An agent that quietly decides the check is too slow today has not made an
engineering judgement — it has overridden that decision on behalf of someone not
in the room, in the direction that happens to be less work. If the cost genuinely
matters right now, say so in one sentence and let them choose.

### Whose decision it is

Two short lists, because both failures live at the boundary between them:
asking about the first trains the user to skim, and deciding the second for
them is choice 3 taken silently.

**Yours, never asked.** Whether to run and when; whether a candidate is proven,
refuted or dropped; how to fix a proven bug inside the change; whether to
iterate, up to the cap; running the suite; whether the repo has system specs
and which ones cover the change; committing a run that ended clean with
nothing open — except under *caller commits*, where the commit is the
caller's; whether a rule break continues, when a committed change doc or the
user's earlier reply already approved it.

**The user's, always asked.** What to act on: each root cause and each
recommendation (fix now / write it down / skip), each unresolved entry of an
abort, each paused system-spec rule break (continue / stop and fix), whether
a commit goes ahead when
something reported-not-fixed changes what it means (report-only mode), and the
Step 0 stop — which of a file's diverging staged and unstaged edits to keep.

**When you do ask, use the host's interactive picker**: any question with
discrete options goes through it, one question per decision, in severity order,
never buried in prose at the end of a long report. Plain text is the fallback
for hosts without a picker, not the default. The picker is also the one thing
here that is structural rather than advisory — a turn with a picker open cannot
end until the user answers — which is why the next rule matters.

**Asked means the user saw it.** A question is asked when it is in a reply the
user reads or a picker they answer — not when an agent wrote it down. If this
skill runs in an agent that reports to another agent, its Step 9 report and its
questions reach *that agent*, and nothing has been asked yet: the hop moves the
picker, it does not discharge the question. So:

- **If you spawned an agent to run this**, its report is your Step 9 input, not
  your Step 9 output. Every entry on the user's list goes in front of the
  user in your **next reply, before anything else** — through your picker, one
  question per decision, or the report's numbered block verbatim where there is
  none. *"The run aborted"* or *"it found three root causes"* with no options
  under it is relaying *about* the report instead of delivering it; if you are
  writing that sentence, that is the bug. Holding the decision across a turn
  while other work finishes is choice 3, made for them — the other work waits,
  or the reply carries both.
- **If you are the agent running this for another agent**, you have no picker
  that reaches the user. Print the whole report in its format — not a summary
  of it — with the hand-off footer
  ([reference.md](reference.md#the-hand-off-footer)) that tells whoever holds
  it what is still theirs to ask. Say plainly which decisions are open and
  that you could not ask them. Under *caller commits*, the result block's
  decisions list replaces the footer ([When the caller commits](#when-the-caller-commits)).

**A run has not ended until its questions are in front of the user**, whichever
agent gets them there.

## Step 0 — Scope

The change under review is the **staged** diff:

```bash
git diff --cached --stat
git diff --cached
```

Group the reviewable files from `--stat` and the paths. Do not read every
changed file in full here — that read is the finder's, on its slice (Step 3).
A bug is usually in the interaction between new code and the code around it,
which is why the finder reads the whole file, not only the hunks. The parent
that re-reads those files is doing the find twice.

**If any file appears in both the staged and the unstaged diff, stop.** You
would be reasoning about the index while testing the working tree, and they
disagree. Tell the user which files diverge and ask them to stage or revert
those edits. **Never `git stash`** to work around this — the user has
uncommitted work and this skill is about to write files on top of it.

Unstaged changes in *other* files are fine. Note them in the report.

Do not hunt for bugs in specs, documentation, or existing tests. Changes to
those files are still context worth reading.

## Step 1 — Triage

**Triage decides from the diff, not from the commit message.** Delegate a
single fast pass to the `triage` role's model ([Models by
role](#models-by-role)). Give it the file list, the diff,
and whether the user asked for a checkpoint (below). Ask for one of `REVIEW` or
`SKIP` plus a one-line reason. Do not ask for a commit message first, and do
not read a subject prefix as a signal ([reference.md](reference.md#what-triage-skips)).

**Commit subjects follow the repo.** If the repo has a doc that states its
naming convention, follow that. If it does not, and `git log` shows one clear
repeated pattern, follow that. Otherwise use `TYPE(Scope): subject`, and add
`(agentic)` when an agent wrote the commit. Never override a convention the
repo already has.

`SKIP` when the diff shows:

- Nothing outside docs, specs, tests, lockfiles, generated or vendored files
  changed. The rule-change chart under `system-spec-changes/` counts as docs.
- The change is purely formatting, renames, moves, or comments — no behavior
  is different.
- It is git's own revert or merge.

**Work in progress is the one skip a diff can't show.** `SKIP` it only when
the user asked, in this conversation, for a checkpoint or a work-in-progress
save — or said the same thing in other words (`tmp`, `save point`, `squash
me`). A checkpoint defers the check, never exempts the code: its behavior
changes are reviewed when they land in a commit that is not a checkpoint.

`REVIEW` for everything else. **When unsure, review.** A small diff is not a
reason to skip; plenty of one-line changes are wrong. "Looks simple" is never
a valid skip reason.

If the user explicitly asked for this skill, run it regardless of triage.

On `SKIP`, print the report (Step 9) with the skip reason and stop hunting.
If the skip is a checkpoint, or the diff edits or deletes a
`*.system-spec.md` file, run the [system-spec rule
check](#alongside-step-3--the-system-spec-rule-check) before the commit
anyway: a skip skips the hunt, not that check.
**`SKIP` is a value for the trailer, not an exemption from it** — the commit
still goes through `commit-with-trailer.sh` with
`skipped at triage (<reason>)` as its third argument ([Step
9](#step-9--report-and-commit)). Skipping the hunt is the cheap half; skipping
the commit script is what puts an unchecked commit in front of the hook.
Under *caller commits*, the same value goes to the result script instead
([When the caller commits](#when-the-caller-commits)).

### A hook report is an input to triage, not an instruction to run

The companion hook reports commits that landed without a trailer. Look at what
actually landed — this is what keeps a false alarm cheap, and
[DECISIONS.md](DECISIONS.md#triage-applies-to-the-hooks-own-reports) is why:

| what the reported commit is | response |
|---|---|
| docs, formatting, a rename, a revert — any skip category | `git commit --amend --no-edit --trailer "Bug-hunter: skipped at triage (<reason>)"` — but if it edits or deletes a `*.system-spec.md` file, run the system-spec rule check over that commit first ([rule-check.md](../maintain-system-spec/rule-check.md#slots)), and amend only after the user has answered every paused break |
| not new work at all — the hook misfired on a branch switch, a replay, a commit that predates the hook | the same amend, with `Bug-hunter: not new work (<what it actually was>)`, and say the hook misfired |
| real code | get the change back in front of you and run the full loop, then record the trailer |

The report gives you the sha and the repository and stops, deliberately, because
it cannot see where you are standing. **Check where that sha sits relative to
your HEAD before acting on it.** The amends above assume it *is* your HEAD, which
is often false: `git commit` then `git checkout main` is the case this hook
exists for, and there they land on the wrong commit.

## Step 2 — Baseline

Run the project's test suite, typecheck, or build — whatever it already has —
and record the result. Start that command and go straight to Step 3 in the
same turn; the finders launch while it runs. Record the result when it
prints. If something is already failing, note it as the baseline. You are not
responsible for pre-existing failures, but you must not add to them, and you
must not mistake one for a bug you found. This is running a command and
writing down what it printed — if you delegate it, the `mechanical` role's
model is sufficient. The finders must not run this same full suite.

## Step 3 — Find candidates

The parent stays thin. It has already scoped the diff (Step 0) and triaged it
(Step 1). Here it slices the reviewable change, launches the finders together,
and merges what they return. It does not hunt.

A reviewable file is a staged file that is not docs, specs, tests, a lockfile,
or generated or vendored. One area means those files share a directory, or
one file plus the code in this diff that it directly calls. Two directories
are two areas unless one exists only to serve the other in this diff.

**Count the changed lines with git, not by eye:**

```bash
git diff --cached -M --numstat -- ':(top)' ':(top,exclude)system-spec-changes/**'
```

The `:(top)` pathspecs count the whole repository from whatever folder you
are in; a plain `.` would count only the current folder. Sum the added and deleted columns over the reviewable rows only. A binary
file (`-`) counts 0, and so does a pure rename. The report's `scope` line
gives the count and names every staged file left out of it, so the count can
be checked.

### Light or heavy

**Light is the default.** A run is **heavy** only when the user asked for
it in this conversation — "heavy hunt", "run bug-hunter heavy", or the same
in other words — or when a caller's brief says `mode: heavy`. Do not choose
heavy yourself and do not offer it. Never drop a heavy run to light because
it is slow; that is the user's call, made already. A run that follows from
another run — a root cause's option 1, the new run after *stop and fix* —
keeps that run's mode. A new commit request starts light.

**How many finders:**

| Changed lines | Light | Heavy |
|---|---|---|
| 1–50 | 1 | 4 |
| 51–300 | 2 | 4 |
| over 300 | 4 | 4 |

No reviewable lines at all is a triage skip (Step 1), not a find. Four is
the cap in both modes. A heavy run spawns four finders on every iteration,
and every iteration re-reads the whole change: no delta. Split by area,
each finder reads its own area of the whole change; split by class, each
reads all of it.

**One finder does the full hunt, all four classes.** Small is not a skip
(Step 1), and it is not a reason to spawn a fleet.

**Two or four finders split one way, never both.** Area slices, or
bug-class slices. Splitting by area and then by class in the same pass is how
a short diff becomes a dozen agents.

- **By area, when the change has at least as many areas as finders.** One
  slice per area. More areas than finders: merge the most related until the
  count is right. Do not give a finder one file when that file's caller in
  this diff sits in another slice; keep that pair together.
- **Otherwise by bug class.** Two finders take classes 1 and 2, and 3 and 4.
  Four finders take one class each. Each finder still reads every
  reviewable file in full — the interaction is why. In a light run, a pair
  or class that cannot fire in this diff is not spawned, and the count drops
  with it. When it drops to one finder, that finder hunts all four classes,
  as any single finder does. In a heavy run all four are spawned: a finder with nothing to find
  returns `none` quickly, and the user asked for the redundancy.

The classes are the hunt this skill already does, named so two finders do not
walk the same questions in series:

1. **Wrong result** — a real input produces the wrong value or side effect.
2. **Failed in the middle** — an error, timeout, or partial result leaves
   state half-applied, swallowed, or reported as success.
3. **The next call** — ordering, retry, duplicate, or stale state. What the
   second call sees.
4. **Trusted boundary** — a caller, schema, stored record, or config the new
   code trusts and does not check.

Each finder runs on the finder role's model: `finder_light`, or
`finder_heavy` in a heavy run ([Models by role](#models-by-role)).

### Models by role

Every subagent this skill launches runs on its role's model. The roles and
their ordered lists come from one script:

```bash
BM=~/.agents/skills/bug-hunter/scripts/models.py
[ -f "$BM" ] || BM=~/.claude/skills/bug-hunter/scripts/models.py
python3 "$BM"
```

It prints one `role` line per role, then any `warning` lines. The defaults
live in the script. A person overrides a role in the kapo-skills config
file, `~/.config/kapo-skills/config.json` (or `SHARED_SKILLS_CONFIG`),
under `"bug-hunter": {"models": {<role>: [<entry>, ...]}}`. Run it once per
run, before Step 1, and use its output for every launch in the run.

| Role | Used for |
|---|---|
| `triage` | Step 1 |
| `finder_light` | Step 3 finders, and a fresh Step 6 fixer, in a light run |
| `finder_heavy` | the same, in a heavy run |
| `refuter` | Step 5 refuters, and the fix-conflict question |
| `rule_check` | the system-spec rule check, and a fresh stop-and-fix agent |
| `mechanical` | Step 2 when delegated, and subagents that only edit to a decided outcome or commit |

**Pass the first entry the host offers.** Go down the role's list:

- **An exact slug**, such as `grok-4.7-high-fast`: pass it if the host
  lists it.
- **A family word**, such as `grok`, `sonnet`, `opus` or `haiku`: pass the
  highest-version slug the host lists whose name contains that word. When
  several share that version, pass the one whose name includes `high`, then
  `thinking`.
- **`inherit`**: omit `model`, so the subagent runs on your model. Every list
  ends with it.

Say which slug you passed for each role. Do not pass a heavier model than the
entry you reached, and do not skip an entry to finish sooner.

**A launch that fails on its model moves down the list.** When the host
refuses the slug, or the subagent fails on quota or availability before it
starts, launch it once more on the next entry that resolves to a
different slug, and say which slug failed. An entry that resolves to a slug
already tried in this run is skipped: after `grok-4.7-high-fast` fails, the
family word `grok` would pick it again. When the list runs out, do that
step in-process and say so. Never skip the
step, and never drop a refuter.

**A `warning` line goes in the report.** It means part of the config could
not be used. A warning about one role means that role fell back to its
default; the other roles keep their overrides. A warning about the whole
file means every role is on its default. Either way the `role` lines are
what the run uses, and it goes on.

**Finders and refuters never all run on your model.** If this run's finder
role and the `refuter` role both resolve to the model you run on — the slug
the host runs you on, not a `Co-Authored-By` name, and `inherit` counts as
that slug — pass the refuters the next entry in the `refuter` list that
resolves to a different model. If none is, say so in the report. An in-process
run, on a host with no subagents, cannot meet this; say that too. Why:
[DECISIONS.md](DECISIONS.md#finders-and-refuters-never-all-run-on-the-main-agents-model).

### How to launch

Launch every finder for this iteration in **one message**. The next finder
does not wait for the previous one to return, and it is not launched from a
later message. Wall-clock is the slowest slice, not the sum. When the
[system-spec rule check](#alongside-step-3--the-system-spec-rule-check) is
owed, launch it in that same message.

| Host | Launch |
|---|---|
| Cursor | N `Task` calls in that one message. `subagent_type: generalPurpose`. `model:` the slug [Models by role](#models-by-role) picked for the finder role. `run_in_background: true` — you are the coordinator, and a foreground task blocks you inside one finder. |
| Claude Code | The same N prompts, all in one turn, as background agents. The same model rule, when the host can name a model. |
| No subagent tool, or you are already a subagent and the host refuses another | You are the one finder. Say **find pass in-process — subagents unavailable**, and name the model you are — you cannot switch it. Same prompt, same bar. Do not claim you split. |

A Cursor subagent does not see this conversation. Each prompt is the template
below with the slots filled. Do not write "as discussed", do not point at a
diff you read earlier, and do not invent a different hunt.

The Step 2 suite should already be running. If it is not, start it in this
same message. Do not start a second suite. Finders must not run the full
suite — two suite runs race. A finder may run one function, script, or
request. Record the suite when it prints. Do not hold the finders until it
finishes, and do not hold the suite until they do.

**Use this template verbatim.** Slots are in angle brackets.

```text
You are a bug-hunter find slice. You cannot see the parent conversation.
Do not edit files. Do not commit. Do not run the project's full test suite.

Repo: <absolute path>
Iteration: <1, 2, or 3>
Slice: <area name and file paths, or one or two bug class names>
Other slices, do not hunt these: <paths, or "none">
Bug classes, if this slice is split by class: <one or two names, or "all four">

Review only this diff for your files:
  <the diff command: git diff --cached -- PATHS, or on a light delta pass git diff -M PREV_TREE CUR_TREE -- PATHS>
Read each of those files in full, not only the hunks.

Hunt this slice for plausible scenarios the code does not handle.
If your slice names bug classes, those classes are your whole hunt. The
other classes are other finders.

Every candidate needs all of these:
- scenario — what situation the code does not handle
- reachability — a real caller, entry point, input, or state, traced.
  No named trigger, no candidate.
- concrete input — the specific value, sequence, or condition
- wrong outcome — what actually happens, and what should have
- where — file:line
- observed — the command you ran and what came back. Run the thing
  (call the function, run the script, curl the endpoint) with the
  concrete input. If you cannot observe it without writing a test, say
  "not observed" and why.

Not a candidate, and not in your reply: style, naming, formatting,
preferences, "consider extracting this", missing comments, defensive
checks for conditions that cannot occur, hypotheticals with no caller.

Return only the candidate list, or the single line "none".
One block per candidate, with the fields above. Do not fix anything.
```

The instructions above the slice slots stay byte-stable across slices and
across iterations. Put per-iteration notes — what the last pass changed,
[the settled list](#the-settled-list), and on a delta pass the context
lines from [The delta pass](#the-delta-pass) — after the template, not
inside it.

### What every candidate still is

The bar did not move. A finder that only reasons reports false bugs, and a
split that adds those is a slower skill with more noise.

- **Reachability.** A candidate whose trigger cannot be named is not a
  candidate.
- **Observed.** The command and the result sit next to the candidate. Reading
  finds it; running it is how you know. If it genuinely cannot be observed
  without a test, the finder says so and Step 4 decides.
- **Not candidates.** Style, naming, formatting, preferences, "consider
  extracting this", missing comments, defensive checks for conditions that
  cannot occur, or hypotheticals with no caller. None of these are reported.

### Merge, do not re-hunt

Wait until every slice has reported. One slice returning is not Step 4. If a
slice fails, launch that slice once more with the same prompt. If it fails
again, those files are **unread**, named in the Step 9 report — an unread
slice is not a clean one, and it is not zero bugs.

Then merge, and stop reading:

- Union the lists.
- Same file and the same wrong outcome are one candidate. Keep the block that
  recorded a command and a result. Two different inputs are two candidates.
- No named caller: drop it.
- A candidate only one slice reported is kept. Another slice staying quiet is
  not a refutation. Refuting is Step 5.
- Do not open the source to re-trace, re-run, or hunt again. Do not rewrite a
  candidate into something the finder did not claim. The merged list is what
  Step 4 proves.

### While the finders run

The find and the refute only read, so other work can happen. Waiting at an
idle prompt is where most of the "this is too expensive" feeling comes from.

Safe meanwhile: unrelated files, documentation, answering the user, planning.
Not safe:

- **Do not touch the files under review.** Findings against a version that no
  longer exists are worthless. If the other work needs an edit there, the run
  is invalid — wait, or restart it against the new state.
- **Do not commit.** The commit waits for the whole run, always.
- **Do not guess at the result.** You know nothing until the slices report.
  Never write up findings you have not received, and if the user asks in the
  meantime, say it is still running.
- **Do not poll.** On Cursor the background finders notify you when they
  finish. Do not re-read their files while you wait.

Steps 4, 6 and 7 write files, so they run in the foreground. The reading
passes are the ones that run together.

**When every slice is back, the run is the next thing.** That return is Step 4
starting — or, after the last iteration, Step 9 — not a notification to file
while other work finishes. Finish the edit you are in the middle of, then
pick the run back up. If what came back ends the run, the report and every
question in it go out in that same turn's reply
([Whose decision it is](#whose-decision-it-is)). A result that arrives during
other work and sits in your context is how a run quietly never ends.

Each iteration spawns fresh finders. Do not resume the previous iteration's
finders to hunt the code they just changed. Step 6 resumes a finder only to
fix, and only inside this iteration. In a light run, iterations 2 and 3 read
only what the last fixes changed ([The delta pass](#the-delta-pass)); in a
heavy run every iteration reads the whole change.

## Alongside Step 3 — the system-spec rule check

**A system spec lists rules a change must not break.** It is a
`<concern>.system-spec.md` file with rule IDs such as `REFUND-02`, indexed by
a root `SYSTEM_SPECS.md`. This check reads the rules that cover the change
and reports each one the change breaks. It is not the refuter's spec check in
Step 5. There, "spec" means feature spec, design and task text, read as
evidence of intent. Both follow the same rule: text written with the change
is not a decision.

**First, does the repo have system specs?**

```bash
git ls-files -- ':(top)SYSTEM_SPECS.md' ':(top,glob)**/*.system-spec.md'
git ls-tree -r --full-tree --name-only "$REV" | grep -E '^SYSTEM_SPECS\.md$|\.system-spec\.md$'
```

`$REV` is `HEAD`, or the commit's parent (`<sha>^`) when the change under
check already landed, as on the hook's amend path. `:(top)` and
`--full-tree` read from the repo root, whatever folder you are in;
`git ls-tree` does not take `:(glob)`, hence the `grep`. The second command sees specs the
change itself deletes: staging the removal of every spec empties the index,
not the commit the rules come from. If both print nothing, skip the check.
Do not hold the commit for it. The report carries one line, once per run:
`system specs  none in this repo — run create-system-spec to set them up`.

**Then, can you read the brief?** It lives in `maintain-system-spec`:
[rule-check.md](../maintain-system-spec/rule-check.md). If that file cannot
be read, skip the check with one line,
`system specs  rule check skipped — install maintain-system-spec`, and do
not hold the commit.

**When it runs.** With iteration 1's finders, in the same message, whenever
triage said `REVIEW`. On a triage `SKIP`, when the skip is a checkpoint, or
when the diff edits or deletes a `*.system-spec.md` file. A checkpoint
defers the hunt, not this check: a rule broken in a checkpoint is already in
`HEAD` when the next commit is checked, so no later commit-time check would
see it. A skip-category commit that edits only a spec is how a rule gets
loosened ahead of the code that breaks it. In a later iteration, run it
again with that iteration's finders only when its fixes touched a file a
checked spec covers. Stage those fixes first: the check reads
`git diff --cached`, and a fix left in the working tree would be committed
without ever being checked.

**Which specs.** Read each spec as committed at `HEAD`, never the working
copy, which may carry edits made with this change. A spec is due when a
Scope glob matches a staged file, when one of its rules cites a staged file,
when the diff edits or deletes it, or when it has a `Scope: repo-wide` rule
and a staged file is code (then check only those rules). The commands are in
[rule-check.md](../maintain-system-spec/rule-check.md#which-specs-to-check),
in one-change mode. No spec due: one report line,
`system specs  no spec covers this change`, and no subagent.

**Its own subagent.** One, beside the finders. Do not fold it into a
finder's brief, and do not launch one per finder. It does not count against
the cap of 4. Launch it like a finder: on Cursor, `Task`, `subagent_type:
generalPurpose`, the `rule_check` role's slug ([Models by
role](#models-by-role)), `run_in_background: true`. That list is Grok-first
like the finders', because the check runs on every reviewed commit. The prompt is
[the brief](../maintain-system-spec/rule-check.md#brief), slots filled. If it
fails twice, run the brief yourself in-process and say so. A rule check that
did not run is not a clean one. **No commit, mint or result block until the
check has returned its breaks or `none`.** If it has not returned, wait. If
it failed and the in-process run failed too, that is an open decision for
the user, asked like a paused break: run it again, or commit without it. With no subagents, say
**rule check in-process — subagents unavailable**. Which agent does each part
of the check, here and at the pull request:
[Who does what](../maintain-system-spec/rule-check.md#who-does-what).

**A break is any of these:**

- The change makes code do what a rule forbids, or stop doing what a rule
  requires.
- The change deletes or weakens a test, or other evidence, that a rule cites.
- The change edits a rule in a spec file, so the change rewrites its own
  rule.

Behavior no rule covers yet is not a break. Do not pause a commit because
something "could be documented".

**Each break either continues or pauses.** This skill never edits a system
spec and never decides what happens to a rule. A pull-request workflow skill,
when one is installed, asks about each rule once at the pull request. None is
included in this repository, and it is optional: without one, the person
settles rule changes by running `maintain-system-spec` themselves, and the
chart entries stay undecided until then.

**Continue** — record it in the [rule-change chart](#the-rule-change-chart)
and let the commit go ahead — when one of these holds:

- **A change doc approved it.** A change doc is an OpenSpec change
  (`openspec/changes/<name>/`: proposal, design, specs, tasks) or a spec-kit
  feature (`specs/<feature>/spec.md`, plan, tasks). It approves a break only
  when the text that records the decision is in `HEAD`, put there by a commit
  this conversation did not make. A `SPEC` or `DOCS` commit made earlier in
  this conversation does not count, whether you made it or the `commit` skill
  did when it split the change. Splitting the doc into its own commit first is
  the same change, in two commits. Text written with the change approves
  nothing, because an agent can write both the code and the doc that
  justifies it. When you cannot tell, it is not approved. Status:
  `recorded`.
- **The user already acknowledged it in this conversation**, in a reply to a
  question that named the rule ID: this skill's own pause, a pull-request
  workflow skill's rule question when one is installed, or the person's
  answer in a hand run of `maintain-system-spec`. When this skill runs inside
  another agent, a
  brief that names the rule ID and the person's answer is that reply. Apply
  this one yourself; the subagent cannot see the conversation, so its brief
  lists the commits this conversation made, and it judges only change docs.
  Your reading of an earlier request is not a reply. Status: `acknowledged`.

An answer of *update the spec*, *keep the old behavior* or *skip for now* is
the decision itself: the commit that carries it gets no new chart entry.
Whoever asked the question — the workflow skill when installed, otherwise the
person in their hand run — writes the decision into the existing entry, in
that same commit. A skip puts the rule back to its text at the merge base, and the
brief does not count that restore as a break.

**Pause** on any other break. A bug fix should not break a rule, so a break
nobody approved is the case that needs a person —
[Step 9](#a-system-spec-rule-break-pauses-the-commit).

### The rule-change chart

A committed log beside the spec index, one file per branch:
`system-spec-changes/<branch>.md`, the branch name made path-safe. Its path
rule, entry format and lifecycle are in
[rule-check.md](../maintain-system-spec/rule-check.md#the-rule-change-chart).
Entries are never removed; a decision is written into each when the rule is
settled (at the pull request by a workflow skill, or in a hand run).

**Written before the mint, committed with the code.** For each break that
continued, the main agent extends this branch's entry for that rule when
the entry is undecided, or adds a new entry when there is none or the last
one is decided. An extension adds a behavior as its own `- new:` line, and
not one the entry already lists. Then it
`git add`s the chart file with the rest of the change — after the user's
answer to any pause, before prose's first call when prose is installed, and
before `commit-with-trailer.sh` or `caller-result.sh`. The entry is then part
of the staged tree, so the binding is minted over a tree that includes it,
and the commit that carries the code carries its record. Nothing is staged
after the mint, as always. Under *caller commits* the entry is staged too,
and the caller commits it with the rest; the result block does not change. A
run that does not commit — report-only, an abort, *stop and fix* — writes no
entry.

**A chart file is never a spec and never approval.** A commit that touches
only `system-spec-changes/` is a docs change: triage skips it, and no rule
check runs. An `acknowledged` status in the chart is not a reply in this
conversation; a later run asks again.

## Steps 4–7 — Prove, Refute, Fix, Verify

**Read [reference.md](reference.md#steps-47-in-detail) before doing any of
these.** It carries the procedure; below is only the part you cannot get wrong.

**Step 4 — Prove.** Write the regression test, run it against the *unfixed* code,
and require it to fail **for the predicted reason** — not an import error, not a
missing fixture. A candidate that cannot be driven red is dropped and its test
deleted. Never leave a failing or discarded test in the tree. This is the whole
contract: without an observed red, a finding is a guess. **Do not delegate this**
— Step 3's merged list already carries the concrete input and the expected wrong
outcome, so writing one test in the project's existing framework is translation,
not investigation. Do not re-open the source to hunt again while you write it.
Write and run it in the loop you are already in, and a **small, cheap model** is
sufficient. The red is the check, and it is empirical.

**Step 5 — Refute.** A *separate* agent that has not seen the finder's reasoning
tries to kill each proven bug — unreachable, guarded upstream, intentional, or
asserting something the code never promised. Only survivors get fixed; refuted
findings are dropped and their tests deleted. Use the **`refuter` role's
model** ([Models by role](#models-by-role)), including the rule that finders
and refuters never all run on your model. Its default list puts accuracy
ahead of cost: a refuter runs only on proven bugs, and its verdict decides
which of them get fixed.

**Refuters run concurrently.** Each one judges its own finding and must not see
the others' reasoning, so there is nothing to serialize — **launch them all in
one message**, not one per bug after the last returns. Same launch as the
finders: on Cursor, one `Task` per proven finding, `subagent_type:
generalPurpose`, `model:` the refuter slug, `run_in_background: true`.
The cap of 4 is the find, not a
license to drop refuters; this count is the number of proven bugs. A Cursor
subagent does not see this conversation, so each prompt is the Step 5 brief in
[reference.md](reference.md#step-5--refute) with the header filled in — repo
path, the finding, the failing test, which spec text predates the change.
The one question that waits is the cross-finding one below, which needs the
surviving set.

**A refuter judges findings, never proposals.** It is told to default to
skepticism, which is right for "is this bug real" and wrong for anything else:
pointed at a proposed design change, its disposition defends whatever exists
today ([DECISIONS.md](DECISIONS.md#a-refuter-judges-findings-not-proposals) —
it cost eight iterations). So: findings to the refuter, **design decisions to the
user** via Step 9's picker. The one question about fixes that belongs here is
factual rather than evaluative — *do any of these fixes fight each other?* Give
it the codebase's record of rejected approaches too — the same files Step 6
reads — so it can say whether a finding re-treads ground already recorded as
rejected.

**Tell the refuter which spec text predates the change.** A refuter cannot see
when a document was written, so it reads spec, design and task text as
pre-existing intent — and documentation authored in the same session as the code
is not that. It is the implementer describing what they just wrote, and it has
killed a reproduced finding as "a deliberate, documented design choice". So the
brief names the committed spec separately from the in-flight text, and the refuter
checks provenance — `git log -S "<phrase>" -- <file>`, `git diff`, `git blame` —
before treating any passage as a decision. **A sentence that exists in no commit
refutes nothing**; the procedure is in
[reference.md](reference.md#step-5--refute), the incident in
[DECISIONS.md](DECISIONS.md#documentation-written-in-the-same-session-is-not-evidence-of-intent).

**Step 6 — Fix.** **Resume this iteration's Step 3 finder** — it already read
its files, traced reachability, and ran its candidates, and nothing has
changed them since. One finder: resume that one. Several slices: resume each
slice finder that still has a survivor, in one message, and give it only its
survivors. On Cursor that resume is the Task tool's `resume` with the finder's
id. On Claude Code it is `SendMessage`. Pass the surviving findings, the
refuter verdicts, and Step 5's fix-conflict notes. If those notes put two
fixes in the same file, one of those finders writes both and the other does
not write. The parent does not re-read the source to invent the fix. Spawn a
fresh agent on the **slug Step 3 passed its finders** only if that finder is
no longer reachable. Do not pass `model` on a resume — the finder already
runs on that slug. The mechanics are in
[reference.md](reference.md#step-6--fix).

**Read the codebase's record of rejected approaches first, if it keeps one** —
a `DECISIONS.md`, an ADR directory, the `design.md` of the OpenSpec change that
covers this code; the same places Step 9
[writes to](#write-down-what-was-rejected-before-you-commit). Check two things:
whether this approach is already recorded as rejected, and — for any lesson you
are about to apply — whether its recorded *scope* covers your case. A lesson
applied outside its scope is a fresh bug wearing the authority of an old fix.

Then answer: *is there a better approach that would have prevented bugs like this
from ever happening?* Prefer simpler code, simpler architecture, fewer moving
parts. Confine the fix to the change under review; if the real cause sits outside
it, that is a root cause for Step 9, not something to fix in passing.

**Step 7 — Verify.** Every new test passes. **The full suite runs once per run,
not once per iteration** — at Step 2 for the baseline, and again immediately
before the Step 9 report, which nothing ships without. In between, run the new
regression tests plus whatever existing tests cover the files the fix touched;
that is what catches a fix breaking its neighbours while it is still cheap to
attribute. **Never modify, weaken, delete or skip an existing test to reach
green.** If a pre-existing test now fails, the fix broke it — fix the fix, or
revert it and report it unresolved. Running tests and comparing counts to the
baseline — a **small, cheap model** is sufficient.

**Then stage what this iteration wrote**: every fix and every kept
regression test, by path (`git add <paths>`, never `-A`). The next
iteration's finders read the staged tree, and a fix left in the working tree
is invisible to them — and is the Step 0 divergence that stops a run.

## Step 8 — Iterate

**A run and an iteration are different things, and the counter resets.**

- An **iteration** is one Step 3 → Step 7 pass over the current state of the
  change, including the fixes just written. In a light run, iterations 2 and
  3 read the fixes' delta rather than the whole change ([The delta
  pass](#the-delta-pass)).
- A **run** is up to three iterations. It ends when an iteration comes back
  clean, or at the abort — three iterations that each found something, followed
  by the root-causes report and one decision per cause (Step 9), **never a
  fourth iteration**. **The full suite belongs to the run, not to the
  iteration**: whichever ending applies, run it before the report and hold the
  report until it is no worse than the Step 2 baseline.
- **Whatever the user then asks for starts a new run at iteration 1.** Applying a
  root cause, taking a recommendation, building something they picked: that is
  new code, and new code gets its own three-iteration budget.

So a long session is a sequence of short runs, not one endless run. Count and
report within the run — `Bug-hunter: 2 iterations, 3 bugs fixed` means this run,
not this week.

**An iteration that fixed something is never the last one.** Stop only after a
pass that **finds nothing**. A fix is new code written minutes ago by someone who
was just thinking about a different problem, so stopping straight after writing
one stops where the change is least reviewed — "I fixed four bugs" and "this code
is clean" are different claims, and only the second is what anyone wanted. The
measurements behind that are in
[DECISIONS.md](DECISIONS.md#an-iteration-that-fixed-something-is-never-the-last-one).

**If an iteration still yields bugs**, before writing more fixes, ask why the
previous pass missed them. Is the finding approach looking in the wrong place? Is
the code's design the reason bugs keep appearing here? Rethink the approach, then
continue. If the answer is a design change larger than the change under review,
take it to Step 9 as a root cause and let the user decide.

### The delta pass

**In a light run, iterations 2 and 3 read only what the last fixes changed.**
Iteration 1 reads the whole change. A heavy run never uses a delta.

At the start of every iteration's Step 3, after Step 7 staged the last
iteration's work, record the staged tree:

```bash
git write-tree        # T1 at iteration 1, T2 at iteration 2, T3 at iteration 3
```

The delta for iteration k is the change from the tree the last pass read to
this one, on reviewable files:

```bash
git diff -M --numstat <T(k-1)> <Tk> -- ':(top)' ':(top,exclude)system-spec-changes/**'
git diff -M <T(k-1)> <Tk> -- ':(top)<reviewable path>' ...
```

The numstat prints paths from the repository root, so each one goes back in
as `':(top)<path>'`; from a subfolder, a plain path would name the wrong
file, and a plain `.` would hide every fix outside that folder.

- **Size it with the same table** ([Light or heavy](#light-or-heavy)), on
  the delta's changed lines, counted the same way.
- **An empty delta ends the run clean.** The last iteration fixed nothing,
  so the code is exactly what a full pass just read. Its settled findings
  are in the report.
- **Each delta finder gets, after the template**: the whole change for its
  files, for context (`git diff --cached -- <paths>`), and the findings the
  last iteration fixed — scenario, test, and what the fix changed — so it
  checks that each fix closes its bug without opening a neighbour. It still
  reads each touched file in full.
- **A delta finder may report a bug anywhere in the files it reads.** When a
  survivor of a delta pass sits outside the delta's lines, the next
  iteration is a full pass over the whole change, sized by the whole change:
  the first pass missed something, and the delta cannot be trusted to show
  the rest. On iteration 3 there is no next iteration and none is asked
  for: fix the survivor as usual, and the run's `budget` root cause (below)
  covers the whole change, not only iteration 3's fixes.

The budget does not change. Iteration 3's fixes still never get a pass of
their own, and that remainder is still a root cause (below). Why a light run
reads less:
[DECISIONS.md](DECISIONS.md#light-passes-after-the-first-read-only-the-fixes-delta).

### The settled list

**A candidate is hunted once.** Keep one list per run, in both modes, of
every candidate already settled: dropped at Step 4 because its test passed,
refuted at Step 5, or reported-not-fixed because no test can show it. Each
entry keeps the tree its iteration recorded at Step 3, the code it was
settled against. Give the list to every later finder after the template, one
line each — `file:line — scenario — how it was settled — tree <T>` — with:
*do not report these again unless `git diff <T> <current tree> --
':(top)<file>'` changes their lines.* That is the only test. A full pass
reads `git diff --cached`, which shows every line of the change, settled or
not; that diff does not reopen anything. A settled candidate appears in the
report once, in the iteration that settled it. Reported again with its lines
unchanged since it was settled, it is not a new finding, and it does not
keep the run going.

### The abort is an ending, not a request for more budget

When the third iteration finishes and something is still unresolved, **the run is
over**. Do not run a fourth iteration and do not offer one. Everything still open
becomes a numbered root cause in the Step 9 report, each with its three choices
attached — and choice 1 is a **new run at iteration 1**, scoped to that one
cause. That is not a fourth iteration renamed: the counter resets for new work,
so a fresh finder reading the fixed code gets a fresh three-iteration budget.

**The commonest unresolved cause is the run's own remainder.** Iteration 3 fixed
something, so by this step's own rule it cannot be the last iteration — and it
is, because the budget is spent. Iteration 3's fixes are code written minutes ago
that no finder pass has ever read. Report it as a root cause in those words:
*iteration 3's fixes never got a finder pass — the budget ended before one
could run*, naming what those fixes touched.

**That is a different kind of cause from Step 6's, and the report says which.**
Step 6's root cause is about **place** — the real cause sits outside the change
under review, so fixing it there would exceed the scope. The remainder is about
**budget** — the cause sits squarely inside the change under review, and the pass
that would have found it does not exist. Do not conflate them; the user is
weighing a different thing in each case. Both get the same three choices, because
the shape of the decision is the same either way. The shape of the entry is in
[reference.md](reference.md#when-the-run-aborts); the incident behind this rule,
and why a fourth iteration is not the fix, are in
[DECISIONS.md](DECISIONS.md#there-is-no-fourth-iteration-the-abort-reports-root-causes).

## Step 9 — Report and commit

**Every run ends with the report. Always, unasked, in the reply the user can
see.** A run ends when an iteration comes back clean or when the third one
aborts — those are the only two endings, and both print it. Never ask whether the
user wants one, and never defer one to "next time": that is the same evasion as
asking permission to run the check. If a run happened, its report is owed.

**Prose is not the report.** Print the format — headline counts, root causes,
per-iteration findings, result — and put any commentary around it, not instead of
it. One report per run, covering every pass. No interim reports (Step 8).

**Anything still open goes in this report, with its question attached.** A
decision the user has not been given cannot be made, and a run that ends with an
unasked question has not ended.

**A run that aborted reports one root cause per unresolved thing, and asks about
each.** Step 6's out-of-scope causes and the run's own unreviewed remainder are
both entries, each labelled as the kind it is (Step 8), each carrying the three
choices below through the picker. Describing the gap accurately and stopping
there is not the report — an accurate description of something nobody was asked
to decide is choice 3 taken on the user's behalf.

**The full report format, with a worked example and the rules for each section,
is in [reference.md](reference.md#the-report). Read it before writing one.** The
commit itself — what to stage, the trailer, splitting — is in
[reference.md](reference.md#committing).

**No commit, mint or result block while a paused system-spec rule break
waits for the user's answer.** See [below](#a-system-spec-rule-break-pauses-the-commit).

**Commit through the script. Never assemble `git commit -m … --trailer …` by
hand — not for a fix, not for a skip, not for a one-line docs change.** Scope:
first letter capital when inventing; reuse `git log` tokens as-is. Stage
everything first — this branch's [rule-change chart](#the-rule-change-chart)
entries included — then, standing in the project:

```bash
BH=~/.agents/skills/bug-hunter/scripts/commit-with-trailer.sh
[ -x "$BH" ] || BH=~/.claude/skills/bug-hunter/scripts/commit-with-trailer.sh
"$BH" "Handle empty input in the parser" "Body text here." \
  "1 iteration, 1 bug fixed" "Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

Four arguments: subject, body (`""` if none — never a trailer in it), the
`Bug-hunter:` value — ending `, heavy` for a heavy run, as in `2 iterations,
3 bugs fixed, heavy`; a light run adds nothing — and optionally the `Co-Authored-By` value. Each trailer is
passed as `--trailer`, so where it lands is git's problem; and for any value that
is not `skipped …` the script runs `mint-trailer.sh` against the tree staged at
that instant and adds the `Bug-hunter-Tree` binding — the one line a hand-typed
commit cannot produce, and the one the hook checks. It runs the repository's
pre-commit hook before minting, so a formatter there cannot change the tree
after it is bound; if the hook fails, nothing is committed — review what it
changed, stage what belongs, and run the script again. The path *to the script* is
absolute because `scripts/` is relative to this directory, not to your project;
the git it runs is not. Verify with `git log -1 --format='%(trailers:key=Bug-hunter)'`;
while the commit is still local, `git commit --amend --no-edit --trailer "…"` is
the repair. The mechanics the script wraps, and what the binding does and does
not attest to: [reference.md](reference.md#committing),
[DECISIONS.md](DECISIONS.md#the-commit-is-assembled-by-a-script-not-by-hand).

**When prose is installed, the same commit carries its `Prose:` trailer.**
prose is a separate skill and is not included in this repository; when
`manage-skills` does not list it as installed, skip the prose steps below and
commit with the plain command above.
Skills that sign commits through the shared library commit once, with every
installed skill's trailer
([the rule](../../lib/commit-trailer/DECISIONS.md#every-installed-skills-trailer-on-one-commit)).
To learn whether prose is installed, ask the `manage-skills` skill (its
`list`): prose is installed when its row says `installed`. prose's SKILL.md
gives its scripts directory, written `$S` below.

If it is, after the last fix and the final `git add`, write the message (subject,
a blank line, body) to `msg.txt`, unstaged, and:

1. Run prose's first call. It lists the prose in the change and prints the
   rules and a pass token:
   `python3 "$S/prose.py" check -F msg.txt --goals "review the fix; check it is safe to merge"`
2. Rewrite the listed comments, docs and message by those rules; restage.
3. Run the second call, which prints the `Prose:` trailer:
   `python3 "$S/prose.py" check -F msg.txt --pass <token>`
4. Commit once, passing the text after `Prose: ` as a family before `--`:

```bash
"$BH" --verified-value "$S/verify-staged.sh" Prose "✓ 4d593e935186:9138830a72a2" -- \
  "Handle empty input in the parser" "Body text here." \
  "1 iteration, 1 bug fixed" "Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

The subject and body are `msg.txt`'s text. Stage and edit nothing between the
second call and the commit: the script runs prose's verifier first and refuses
the commit if the tree or the message changed. A skip gets the prose pass too.

**A prose pass that touches only comments, docs or the message needs no new
hunt.** The `Bug-hunter-Tree` binding is minted at commit time, over the tree
that lands, so it covers the rewrite. If the pass changes code, code was
written since the last clean pass, and a hunt is owed.

Three things are required every run, and they are the ones agents drop first:

- **The headline counts.** Iterations, fixed, refuted, reported — and, whenever
  anything is open, how many decisions the user owes.
- **Root causes above the findings**, numbered so the user can say "do ①". A
  cause buried under a dozen symptoms is a cause nobody acts on.
- **A `why not` on every finding that was not fixed.** "Reported" with no reason
  is a shrug.

**A skipped run is one line, and it is worth printing.**

```
🔍 bug-hunter · skipped at triage — docs only, no executable code
```

That is the whole *report* — it is not the whole job. Knowing the check ran and
why it stopped is useful, and at one line it costs nothing to skim. The commit
is still made the same way as any other (under *caller commits*, handed back
the same way — [When the caller commits](#when-the-caller-commits)), and the same sentence is the third
argument to the script above:
`"$BH" "Fix a typo in the README" "" "skipped at triage (docs only, no executable code)"`.
Keep no-op output proportional — the expensive thing is never a short line
saying nothing happened, it is a long report demanding work that does not need
doing.

### A system-spec rule break pauses the commit

**A break no change doc approved, and the user has not acknowledged, waits
for the user.** Do not run `commit-with-trailer.sh`, `mint-trailer.sh` or
`caller-result.sh` until the user has answered every paused break. A minted
binding says this tree is done, and it is not done while a break nobody
wanted might be a bug.

The hunt still runs to its end. A break does not stop the iterations and
does not earn an interim report. It goes in the Step 9 report, above the
root causes, one entry per break: spec path, rule ID, the rule quoted as
committed at `HEAD`, what the change does to it, and the `file:line` ranges.
Each paused break counts in the headline's `N to decide`. Ask each one
through the picker, one question per break, with exactly two options:

1. **continue** — the break is intentional. Record it in the chart as
   `acknowledged`, then commit as usual.
2. **stop and fix** — no commit. Unless the user says they will fix it,
   resume the rule-check subagent that found the break, with the
   [fix brief](../maintain-system-spec/rule-check.md#fix-brief) and "return;
   do not commit". It already read the rule, the diff and the break, the way
   Step 6 resumes a finder. Spawn a fresh one, on the `rule_check` role's
   slug, only if it cannot be resumed. Stage what it changed. Then the hunt runs again on the
   fixed diff: a new run at iteration 1, started without asking again, as
   with *fix it now*.

Neither answer edits a spec or settles the rule. *Continue* says only that
the break was meant. Whether the spec changes or the code goes back is
decided once, later: at the pull request by a workflow skill when one is
installed, otherwise when the person runs `maintain-system-spec`.

**Under *caller commits*, a pending pause means no result block.** Do not
run `caller-result.sh`. End with the report. A caller that finds no block
has nothing to commit with; it holds the commit and takes the breaks to a
person. A later run, whose brief carries the person's answer for each rule
ID, applies them and prints the block.

**Every break that continued goes in the chart**, with its status —
`recorded` with the change doc and the commit that put the approving text
there, or `acknowledged` — staged before the mint and committed with the
code ([The rule-change chart](#the-rule-change-chart)). The report shows the
same entries ([reference.md](reference.md#in-the-report)). Why a committed
log, one file per branch:
[DECISIONS.md](DECISIONS.md#rule-changes-go-to-a-committed-log-one-file-per-branch).

### Write down what was rejected, before you commit

A run that reverted a fix, refuted a finding, or chose one approach over another
has produced knowledge that does not survive in the diff — the diff shows what
the code is, never what it stopped being. That knowledge is about the code under
review, and it goes **where this codebase keeps rejected approaches**. This
skill's own `DECISIONS.md` is about this skill — a run writes to it only when
the skill is the code under review:

1. **Its stated convention first.** An `AGENTS.md`, `CLAUDE.md` or
   `CONTRIBUTING.md` that says where decisions go settles it.
2. **Then a home it already has**: a `DECISIONS.md` or ADR directory, the
   `design.md` of an OpenSpec change that covers this code, a decisions section
   in an architecture doc.
3. **A rejection about one site — one fix, one function — goes in a comment at
   that site**, in the codebase's own idiom: present tense, a warning rather
   than a history. That is where the next person tempted back to it will be
   standing.
4. **Create only when none of those exist**: `DECISIONS.md` beside a skill's
   `SKILL.md`; `docs/decisions.md` anywhere else.

An entry says four things: the decision, why, **what was tried and rejected**,
and **where the lesson stops applying**. That last field is not optional; a
lesson recorded without its boundary gets applied outside it. A comment at the
site carries the same in a sentence — the alternative, and what breaks when it
is taken. The shape of each: [reference.md](reference.md#where-a-record-goes).

Three reverts in this skill's own history — recorded in its `DECISIONS.md`
because there the skill *was* the code under review — exist only because they
were written down within minutes of happening. Nothing else would have kept them.

### The commit waits for the run, exactly as the report does

One commit at the end, after the last iteration — not one per iteration. The
fixes from an unfinished run are unverified by definition; a commit says "this is
done", and mid-run it isn't. Work in progress lives in the working tree between
iterations, which is what the abort clause already assumes.

**There is no exception**, and an earlier draft invented one. What an invented
exception provides is a documented reason to do the thing the rule forbids, which
is how every other rule here has been walked around
([DECISIONS.md](DECISIONS.md#the-commit-waits-for-the-run-and-the-iteration-counter-resets)).

What does need saying, because it is a real distinction rather than an escape:
**the rule is about the change under review.** A commit that touches any file the
run is reviewing waits for the run. A genuinely separate change — different
files, its own triage, its own trailer — is its own commit and is not covered.
That test is checkable; "it felt unrelated" is not.

### When the caller commits

**If the brief says "caller commits", the run is the same; only the commit
moves.** A caller that builds its own commits — through an API, in a pipeline,
anywhere this skill does not run `git commit` — says so in the brief:
*caller commits: return the result, do not commit.* A brief that also says
`mode: heavy` makes the run heavy ([Light or heavy](#light-or-heavy)). Steps 0–8 run as written,
and every rule under *Do not evade this skill* still applies. Step 9 ends
differently:

1. **Do not commit.** Leave the change staged: everything the run reviewed,
   every fix and test it added, and every record it wrote under *Write down
   what was rejected*.
2. **Print the report**, as in any run.
3. **Run the result script last, after the final `git add`.** It mints the
   binding over what is staged and prints the whole block. Its arguments are
   the `Bug-hunter:` value — what the commit script's third argument would
   have been — and the open decisions, one per line, without numbers:

```bash
BR=~/.agents/skills/bug-hunter/scripts/caller-result.sh
[ -x "$BR" ] || BR=~/.claude/skills/bug-hunter/scripts/caller-result.sh
"$BR" "1 iteration, 1 bug fixed" --decisions - <<'EOF'
refund state is rebuilt on every read — 1 fix it now · 2 write it down · 3 skip
EOF
```

   With nothing open, drop `--decisions` and the heredoc. A skip passes its
   `skipped at triage (<reason>)` value and mints nothing.
4. **End the reply with the script's output, whole and unedited.** The caller
   parses it and passes the trailer lines through unchanged:

```
=== bug-hunter result ===
Bug-hunter: 1 iteration, 1 bug fixed
Bug-hunter-Tree: <the hash the script minted>
=== bug-hunter open decisions: 1 ===
① refund state is rebuilt on every read — 1 fix it now · 2 write it down · 3 skip
=== end bug-hunter ===
```

**Never type the block.** The script is the only way to make it, for the same
reason commits go through `commit-with-trailer.sh`: hand-assembled trailers
went wrong until a script took the assembly away
([DECISIONS.md](DECISIONS.md#a-caller-that-commits-gets-the-result-not-the-commit)).
The binding signs the snapshot the run worked on; the caller commits exactly
that tree, or the binding is false. So nothing is staged after the script
runs. If something must be, run the script again.

**Open decisions go to the caller, in that block, never through a picker.**
Nobody can answer a picker in a headless run. The block replaces the hand-off
footer: the caller acts on it — asks a person, lists the decisions in its pull
request, or holds the commit. Choosing for the user is still not yours: an
open decision is never answered 2 or 3 because nobody could be asked. Format
detail and a worked example: [reference.md](reference.md#the-caller-commits-result).

### Then ask, one recommendation at a time

Whenever the report carries a recommendation — a root cause, a finding too large
for the change under review, or anything an abort left unresolved — **stop and
ask the user what to do with it. Each one separately.** Do not apply them
silently, and do not decide on their behalf that they are out of scope. A
recommendation is where a small change prevents a class of bugs rather than one
instance of one.

**Use the host's interactive picker if it has one**, one question per
recommendation, in severity order. Offer only the options that honestly apply:
"implement it now" belongs there when you have a fix you would defend, and when
you do not, say so and offer the other two. Padding the menu with an option you
have no confidence in is how a run ends with a hopeful patch on a problem nobody
understood. A worked example is in
[reference.md](reference.md#asking-about-a-recommendation).

**If the report reached you from an agent you spawned, the asking is yours.**
Its picker could not reach the user and its text asked nobody; see [Whose
decision it is](#whose-decision-it-is) — next reply, before anything else.

Take the answers per item — "1 for ①, 2 for ②" is a normal reply, and so is
"all 1". If the user answers once for everything, that applies to everything.

**1 — fix it now.** Apply the change, then **start the loop over it immediately,
without asking again.** The user already said yes; asking "shall I now check the
fix?" is asking the same question twice and invites a no the second time. A
root-cause fix is the code most in need of checking, not least: written in one
pass, minutes after the analysis, usually touching more than the original change
did — that breadth is what made it a root cause. Every time this skill has
skipped that pass, the next run found something. Say what the fix will touch
before starting it, then apply, loop, and report once at the end.

For a cause the abort left unreviewed rather than unfixed, there is nothing to
apply and **the pass itself is option 1**: a new run at iteration 1, scoped to
that cause — the fixes iteration 3 wrote, and the files they touched. Say
`1 — new run` rather than `fix it now` when that is what the option is, and
never count it as a fourth iteration, in the report or in the trailer.

**2 — write it down.** Record it as a known, accepted gap where this codebase
already keeps them — the same lookup as
[Write down what was rejected](#write-down-what-was-rejected-before-you-commit),
stated convention first and a new file last, but the home is the one for open
questions rather than decisions: a spec's Open Questions or Roads Not Taken
section, an existing OpenSpec change, a `docs/` or ADR entry, a
`DECISIONS.md`-style file if the thing under review keeps one, then the closest
README. Only if none of those exist, create `docs/open-questions.md`. One entry:
the cause, which findings it produced, the recommendation, the odds, and the
date. Commit it with the rest of the change. A recommendation that lives only in
a terminal report is gone when the tab closes, which is choice 3 with extra
steps.

**3 — skip.** Nothing happens. Still name it in the report so the run's record is
complete, and do not raise it again in this session.

What is not on the list is deciding for them. Reporting a cause, moving on, and
letting it evaporate — when the user would have said "fix it" — is the same
failure as never running this skill at all. Relaying that a cause exists, with
no options under it, is the same thing one hop later.

## Never

- Run inside a git `pre-commit` hook.
- `git stash`, amend, or rebase.
- Weaken, skip, or delete an **existing** test to reach green.
- Leave a failing or discarded test in the tree.
- Report a bug with no failing test, or a style opinion of any kind.
- Apply a refactor larger than the change under review.
- Write to this skill's own files — `DECISIONS.md` included — unless they are
  the change under review.
- Commit, mint, or print the result block while a paused system-spec rule
  break waits for the user's answer.
- Edit a system spec, or decide what happens to a rule. That is the pull
  request's, once.
- End a reply holding a decision from the user's list. Written is not asked;
  relayed to you is not relayed to them.
