# bug-hunter — decisions

**Read this before changing anything in this skill** — `scripts/`, or the rules
in `SKILL.md`. Not because it explains how either works; the code and the rules
do that. Because most of what looks like an obvious improvement here has already
been tried, and the reason it was reverted is not visible from the line you would
be editing.

Every entry is a decision, why it was made, and what was tried and rejected. The
rejected column is the load-bearing one: twice in this file's history a solved
problem was re-solved differently a few lines away, because the record of the
first solution lived at the first site only.

Some entries name `prose` and `commit`. Those skills are not in this
repository; they live in the team skills repo this copy came from. Every rule
that involves them applies only when they are installed.

This copy also omits the pull-request workflow skill (`open-pr-workflow` in
the team repo) that asks about each rule change and writes chart decisions.
It is optional. Until one is added, rule changes are settled by hand: the
person runs `maintain-system-spec`, and chart entries stay undecided until
then. Entries below that name it describe that skill when it is installed.

**The hook and mint mechanics are shared** with other skills, and their
decisions live with them, in
[`.agents/lib/commit-trailer/DECISIONS.md`](../../lib/commit-trailer/DECISIONS.md):
reading git state rather than commands, the reflog cursor, the submodule walk,
and why the trailer is minted from the tree. What stays here is bug-hunter's
own: two decisions about its hook's behaviour, then the skill's rules.

---

## A skip is a value for the trailer, not an exemption from it

**Decision.** Two texts reach an agent that never invokes this skill: the
frontmatter `description`, before it decides, and the hook's report, after the
commit lands. Both state that a skip is a trailer value, and neither states the
trailer requirement in a form conditional on the commit containing code.

**Why.** On 2026-09-11 one session made three doc-only commits to a backend repo
— an OpenSpec proposal, its design and spec, and a prose correction, zero code —
each with a bare `git commit -m`, no trailer. The hook fired after each. The
agent read it, reasoned correctly that a doc-only commit has nothing to hunt,
and moved on. Three times, the third after two reports saying so.

Every doc in this skill already had the right answer. `SKILL.md` said a skip
commits through the script "as in Step 9"; the triage table gave the amend; Step
9 carried a worked `"$BH" "DOCS(Readme): fix typo" "" "skipped at triage (docs
only, no executable code)"`. **The agent read none of it, and that is not a
reading failure.** A doc-only commit never invokes this skill, so `SKILL.md` was
never in its context — the only two texts that were are the ones above.

The `description` said `Skips docs, specs, tests, and work-in-progress commits`.
That is the whole basis on which an agent decides whether this skill applies to
the commit it is about to make, and read at that moment it says: not this one.

The report then closed with *Every commit containing code should go through the
bug-hunter skill, and record what happened in a Bug-hunter: trailer.* The
trailer clause is subordinate to "containing code", so a doc-only commit
falsifies the antecedent and the sentence exempts the trailer along with the
hunt. The agent's no-op was that sentence read correctly. Restating the rule
louder somewhere it was already stated would have changed nothing; both edits
are to text that was actually in front of it.

**What this cost, and why it is not a documentation nit.** A trailer that says
`skipped at triage (docs only)` and no trailer at all are the same commit to
everyone except the audit — `git log --invert-grep --grep='Bug-hunter:'` cannot
tell "considered, nothing to review" from "never checked", so a repo that
accumulates the first stops being able to see the second.

**Rejected: having the hook classify the diff** and print `3 of these changed
only documentation`, or amend the trailer itself. Beyond *The report states facts
and stops* above — the command-constructing half produced 28 findings across
eight iterations, and a post-commit hook cannot know the named sha is the
reader's HEAD — a classifier in the hook is a second copy of `reference.md`'s
skip-category table, living in a file that cannot import it. Two copies of that
table drift, which is what this file's opening is about. Listing the categories
in the sentence and letting the reader place its own commit costs no machinery
and cannot disagree with the table, only go stale against it.

**Rejected: lower-friction skip path in the script.** There is nothing to
lower — a skip is three arguments, mints nothing, stages nothing. *The commit is
assembled by a script, not by hand* already built that path for this exact
habit, the "trivial docs commit" arriving with `-m` composed. This incident is
upstream of it: the agent had no reason to think the script applied at all.

**Where this stops applying.** This does not license remedies in the hook's
report. What went in is the standard — unconditional, context-free, naming no
sha and no repair — which is the same line *The report states facts and stops*
drew for trailer placement. The remedy for a commit that already landed stays
in `SKILL.md`'s triage table, which runs in the reader's own frame. Nor is it a
general rule that every doc gets the same sentence: the two edited here are the
only ones read by an agent that has not invoked the skill.

---

## The hook is never told that a run is in progress

**Decision.** Nothing marks "a bug-hunter run is in flight". A commit that lands
mid-run is reported exactly like any other commit without a trailer.

**Why.** A marker file was sketched for this and deferred, and the reason on
record was only sequencing — new code, so its own run. That is not a reason, so
this entry is the real one, worked out afterwards.

The marker would be a file the *agent* writes to tell the hook not to report the
agent. Every other thing this hook trusts is asked of git, which records what
happened rather than what someone intended; the marker would be the single input
supplied by the party being checked, and the failure mode is not a bug but a
habit — a flag that suppresses a report is a flag that gets set early, and the
skill's whole history here is of exceptions being widened until the rule is gone.

**Rejected, and once already deleted.** The `Bug-hunter: run in progress, N
iterations so far` trailer, removed in `6551f4a` with the note that an invented
exception "does provide a documented reason to do the thing the rule forbids,
which is how every other rule here has been walked around". The marker file is
that same exception moved from the message into a dotfile, where it is less
visible rather than more.

**What it would have bought, honestly.** Nothing. `SKILL.md` already says the
commit waits for the run, so a commit landing mid-run is a rule being broken and
reporting it is correct, not a false alarm. The distinction the marker would
draw — *mid-run* versus *skipped entirely* — is one the reader does not need,
because the response to both is the same.

**Where this stops applying.** If a run were ever attested by something the agent
cannot write at will — a signature, or a record git itself keeps — the objection
is about forgeability, not about the feature, and it would not apply.

---
# The skill's rules

Everything above is about `scripts/`. What follows is about `SKILL.md`: why its
rules say what they say. The wording is load-bearing in a way the rule alone does
not show, and each of these is a revert.

## Every anti-evasion rule was added after it was walked through

**Decision.** `SKILL.md` states the evasion rules under one heading, with the
evidence for each compressed to a clause. The evidence is here.

**What was walked through.**
- *Enumerating the moments a run is owed.* An agent finished a loop, committed,
  and asked whether to start the next one — not on the list, functionally
  identical, and asked exactly when the user was most likely to say no. Replaced
  with a property of the code: if code has been written since the last pass that
  came back clean, a pass is owed.
- *Announcing in the future tense.* "That's running next unless you want to stop
  here" · "I'll kick that off if you're happy with it". Each ends the turn with
  the check not running, which hands the decision back as plainly as asking.
- *Interim reports.* A report between iterations made an unfinished run look
  finished and invited stopping early.
- *Deferring the report*, or asking whether one was wanted. The answer to a
  question nobody wanted asked is usually no.
- *Prose instead of the format.* Reads fine; not scannable, countable, or
  comparable to the last run.
- *Committing mid-run.* Sixteen times, before the rule below existed.

**Rejected.** Stating the rules separately, one per situation. An agent looking
for a way out of a check reliably finds the seam between separately-stated rules;
they are one heading because the evasions were one behaviour.

**Where this stops applying.** These are rules about the agent's own conduct
inside a run, not about the user. A user asking for a commit is an instruction
and needs no licence from this skill. These rules do not start a run. The
start condition is the next entry.

## The hunt starts only when the user asks to commit, or asks for it

**Decision.** This skill starts in two cases. The user tells the agent to
commit the code now, or the user asks for bug-hunter by name. A summary, an
explanation, or a request for the commit message does not start it. The
agent's own guess that a commit is coming does not start it.

**Why.** On 2026-10-14 Harsh asked an agent for a summary of a change and for
the commit message. The code was still open to edits. The agent started a full
hunt, and kept it running after he asked why. The description and rule 2 told
it to. "Code has been written" and "a commit message was requested" were
treated as "commit this". He was still reading.

Once a run has started, the anti-evasion rules above stay. After he has asked
to commit, the agent does not ask permission, does not stop between
iterations, and does not announce a future run instead of starting it.

**Rejected.** Starting on every turn that mentions a commit, including "what
should the commit message be". That phrase asks for text, not for a commit.
Also rejected: leaving the start rule as "if code exists, a pass is owed".
That is what made a question about the change start the finders.

**Where this stops applying.** It does not weaken the hook. A commit that
lands without a trailer is still reported. It does not change triage: a
commit he did ask for still skips docs, specs, tests, and checkpoints.

## An iteration that fixed something is never the last one

**Decision.** A run stops after a pass that finds nothing — never after one that
finds and fixes.

**Why, measured here.** Iteration 1 found 8 and fixed 6; iteration 2 found 7
more, two of them created by iteration 1's own fixes. Separately, a state where
all 32 tests passed still held 11 bugs, one of them silent on the most common way
an agent commits. A fix is new code, written minutes ago under time pressure by
someone who was just thinking about a different problem, so stopping straight
after writing one stops where the change is least reviewed.

**Rejected.** Treating "I fixed four bugs" as an ending. It is a different claim
from "this code is clean", and only the second was ever wanted.

**Where this stops applying.** The three-iteration cap overrides it, and that
collision is deliberate rather than an oversight: a run whose third iteration
fixed something ends anyway, on an iteration this rule says can never be the
last. The pass it owes is not cancelled, it is handed to the user as a root
cause with a new run behind option 1 — see *There is no fourth iteration; the
abort reports root causes*.

## The commit waits for the run, and the iteration counter resets

**Decision.** One commit at the end of a run, never one per iteration. A *run* is
up to three iterations; whatever the user asks for next starts a new run at
iteration 1.

**Why.** Three commits were made mid-run claiming "1 iteration, 5 bugs fixed" and
"2 iterations, 11 bugs fixed", and the very next iteration found four bugs in
those fixes each time. A commit says "this is done"; mid-run, it is not. The
reset exists because without it the count climbed to "7 iterations, 45 found",
which reads as though the cap had been ignored and hides that each run got its
own clean decision point.

**Rejected, and deleted once already.** The `Bug-hunter: run in progress` trailer
— the same exception in another form as the marker file, and refused for the same
reason. See *The hook is never told that a run is in progress*.

**The real distinction, which is not an escape.** The rule is about the change
under review. A commit touching any file the run is reviewing waits; a genuinely
separate change — different files, its own triage, its own trailer — is its own
commit. That test is checkable; "it felt unrelated" is not.

## There is no fourth iteration; the abort reports root causes

**Decision.** Three iterations is the whole budget. When the third ends with
something still unresolved, the run ends in the Step 9 report with one numbered
root cause per unresolved thing and the same three choices on each — a new run at
iteration 1 scoped to that cause, write it down as a known gap, or skip. Never a
fourth iteration, and never an offer of one.

**Why.** Adam: *"We don't do 4th iterations in bug-hunter."* An open "want
another pass?" at the cap is the future-tense announce this file already records
under *Every anti-evasion rule was added after it was walked through*, arriving
at the moment the user is most likely to say no, and it makes a fixed budget
read as an opening offer. The three choices are the same information with the
decision made answerable: each is an action, the user picks one per cause, and
nothing evaporates because nobody was asked.

**The remainder is a root cause of a different kind, and the report says which.**
Step 6's root cause is about *place* — the real cause sits outside the change
under review, so fixing it there would exceed the scope. The abort's remainder is
about *budget* — the cause sits squarely inside the change under review and the
pass that would have found it does not exist. They are not the same thing and the
report labels each (`kind: scope` / `kind: budget`), because the user is weighing
a different question in each: whether to spend a larger change on something
outside the diff, versus whether to keep looking inside it. What they share is
only the shape of the answer, which is why one set of choices covers both.

**Rejected.**
- **A fourth iteration when the third fixed something.** The argument is
  identical at four, and at five: a run that ends on a fix always leaves an
  unreviewed remainder, so every cap has this edge and moving the cap only moves
  the edge. What actually closes it is a *new run* — cold finder, fresh budget,
  scoped to the remainder — which the reset above already makes the correct
  shape.
- **Reporting the remainder and moving on.** That is choice 3 taken on the
  user's behalf, which `SKILL.md`'s own closing line already names as the same
  failure as never running the skill at all. An accurate description of
  something nobody was asked to decide is not a report, it is a shrug with
  detail.
- **Calling the new run a "4th pass"** in the report, the reply, or the trailer.
  It is iteration 1 of a new run. Counting it onward from three is exactly what
  the reset exists to stop — the count that once climbed to "7 iterations, 45
  found" started as one honest continuation.
- **Exempting the remainder from the pass-is-owed rule** instead of re-homing
  it. "No pass is owed here, the budget ran out" is an invented exception, and
  this file's record is that an invented exception is a documented reason to do
  the thing the rule forbids. The pass is owed; what ran out is the budget for
  taking it inside this run.

**Where this stops applying.** This bounds the *agent's* budget, not the user's.
A user who asks for another pass gets one without argument — that is an
instruction, and it starts a new run at iteration 1 like any other new work.

## A question is asked when the user sees it, not when an agent writes it

**Decision.** The user's decisions — the user's list in `SKILL.md`'s *Whose
decision it is* — count as asked only when they are in a reply the user
reads or a picker the user answers. An agent that receives a report from an
agent it spawned has received Step 9's input, not discharged Step 9: it asks
every open decision in its next reply, before anything else, through its own
picker. The report carries this itself — a headline count of open decisions
and, on any text-form report, a footer addressed to whoever holds it — and the
Step 3 background rule now says what happens when the pass comes back.

**Why.** The skill is written in one voice, to "you", and every rule about the
report assumes your reply is the user's screen: *in the reply the user can
see*, *a run that ends with an unasked question has not ended*, *use the host's
picker*. Delegate the run to a sub-agent and each of those is satisfied one hop
short. The sub-agent writes the report in its reply — to the coordinator. It
would use the picker, but a sub-agent's picker does not reach the user, so it
falls back to text, and the text looks exactly like a question that has been
asked. The coordinator receives a finished-looking report and does what a
finished report invites: it summarises. Two shapes of this, both with a capable
coordinator that had read `SKILL.md` and run the hunt correctly:

- an abort relayed as a status line — *the run aborted* — with the numbered
  causes and their three options nowhere in the reply, so the user had to ask
  what they were meant to decide;
- a capped run's root causes arriving from a backgrounded pass while the
  coordinator was mid-way through other work, and sitting in its context across
  turns until the user found them.

Neither is a reading failure, and neither is evasion. The text saying otherwise
was in `SKILL.md`, read thousands of tokens earlier, and nothing in front of the
coordinator at the moment it decided what to do with the report said the
decision was still open. That is the same shape as *A skip is a value for the
trailer, not an exemption from it*: the fix goes in the text that is provably in
front of the agent when it fails, which here is the report itself. Hence the
footer — the report tells its holder that printing it has asked nobody — and
the headline count, which makes "it aborted" a visibly incomplete summary of a
line that says `3 to decide`.

The picker is why this is more than prose. It is the one mechanism in the skill
that is structural — a turn with a picker open cannot end until the user
answers — and it was already mandated. It failed to fire because it sat with
the wrong agent: the one running the skill had no picker to the user, and the
one with the picker did not know the question was still its to ask. The rule
moves the picker to the hop that has one; it does not add a mechanism.

**Rejected.**
- **A host hook that blocks the turn while a decision is owed** — a `Stop`
  hook scanning for the footer, or similar. It is the genuinely structural
  version, and it is the one thing here that depends on a particular harness.
  Other people's agents run this skill, and the reasoning in *The trailer is
  minted from the tree* about hooks that cannot be tested from the session
  that wires them applies unchanged.
- **A file of owed decisions** the run writes into the tree. The user is not a
  reader of the working tree, so it reaches nobody; and it is the agent writing
  a marker to itself, which *The hook is never told that a run is in progress*
  already declines.
- **Forbidding delegation of the run.** The architecture belongs to whoever
  invokes the skill, and the skill delegates its own steps; a rule against
  running it inside an agent would be ignored by exactly the setups it was
  written for.
- **Stating the rule more loudly in `SKILL.md` alone.** It was already there
  three times, and the agent that failed had read all three. Restating a rule
  where it was already stated changed nothing the last time either (*A skip is
  a value for the trailer*). What went into `SKILL.md` is the distinction that
  was missing — reached an agent versus reached the user — and the checklist
  line, which is the one part of `SKILL.md` an agent carries forward as its own
  artifact.
- **Letting the runner pick a default** — write every open cause down (choice
  2) when nobody can be asked. That is a choice made on the user's behalf, and
  *There is no fourth iteration* records why an accurate record of something
  nobody decided is not a report.
- **Asking about more.** Pulling the agent's own decisions — whether to run,
  iterate, commit a clean run — into the picker would make the picker
  something the user learns to click through, and the decisions that matter
  would be skimmed along with the ones that do not. The two lists exist so the
  boundary is checkable rather than felt.

**Where this stops applying.** Only to the user's list. It does not license
asking whether to run, whether to iterate, or whether to commit a run that
ended clean with nothing open — the anti-evasion rules stand. The footer is for
the text form: a report whose questions went through the user's picker in the
same reply drops it. And nothing here verifies anything — an agent that reads
the footer and summarises anyway has no hook behind it, and the deferred
delegation-verification mechanism would not catch it either, since it would
attest that a pass ran, not that its output reached anyone.

## The full suite is a gate on the run, not on the iteration

**Decision.** The full suite runs twice a run: at Step 2 for the baseline, and
once more immediately before the Step 9 report. An intermediate iteration's Step 7
runs the new regression tests plus whatever existing tests cover the files the fix
touched.

**Why.** Contract item 4 is a claim about what gets reported and committed —
nothing leaves the run without the closing full run, so it is still checked before
anyone is told the code is clean. What changed is how many times it is checked on
the way there. A three-iteration run used to pay for four full suites and now pays
for two — the last iteration's was always the closing gate; the two before it
gated work nobody outside the run can see yet. On a project whose suite takes
minutes that was the largest fixed cost in the loop. The signal an intermediate
iteration actually needs is narrow: a fix breaking something is nearly always a
fix breaking something near itself, minutes after it was written.

**Rejected.** The full suite every iteration, which is what this replaces. It pays
for breadth at the moment the breadth is least likely to fire, and the run pays
again at the end regardless. Also rejected: dropping the intermediate run to the
*new tests alone*. Then a fix that breaks a neighbour survives to the closing
gate, where three iterations of fixes sit in the tree at once and nothing says
which one did it — the targeted run is bought precisely to keep that attribution
cheap.

**Consequence, accepted.** A break in a file no iteration touched surfaces later
than it used to — at the closing gate rather than the iteration that caused it.
The response is unchanged (fix the fix, or revert it and report it unresolved),
and the run does not end until it holds.

**Where this stops applying.** It assumes the closing gate really runs before the
report, which is the whole of its safety — a run that reports without it has
dropped contract item 4, not economised on it. It also assumes the project can
select a subset cheaply. Where it cannot — no selection, or a suite whose only
meaningful signal is end-to-end — the targeted run *is* the full run and nothing
here changes.

## A refuter judges findings, not proposals

**Decision.** Findings go to the refuter; design decisions go to the user.

**Why.** A refuter is told to default to skepticism, which is correct for "is
this bug real" and wrong for anything else — pointed at a proposed design change,
that disposition defends whatever exists today. It cost eight iterations here: a
proposal to stop emitting git commands was refuted on a plausible argument, and
the machinery it defended went on to produce 28 findings before the proposal was
adopted anyway.

**Where this stops applying.** One question about fixes is factual rather than
evaluative — *do any of these fight each other?* — and does belong with the
refuter, because a conflict found there costs a sentence and found afterwards
costs both fixes.

## Documentation written in the same session is not evidence of intent

**Decision.** A refuter's brief says which spec, design or task text predates the
change under review, and the refuter checks provenance — `git log -S "<phrase>" --
<file>`, `git diff`, `git blame` — before treating any passage as a deliberate
decision. Text that exists in no commit refutes nothing.

**Why.** Iteration 1 of a run fixed three findings; one added an in-pass circuit
breaker to a scheduled backfill job, bounding the blast radius of a systemic
failure. The implementer then documented that fix in the project's OpenSpec
`design.md` and `tasks.md` — same session, uncommitted. Iteration 2's find pass
found a real gap in the new breaker: it counted only *thrown* transport failures,
so the same failure class escaped it whenever it arrived shaped as an HTTP 200 with
an empty result, and an alternating-failure outage never accumulated enough
*consecutive* throws to trip it. Both were reproduced, with tests observed red.

The refuter assigned to that finding quoted the implementer's own fresh
`design.md` sentence — "reset the moment any call is answered … a no-result is
equally good proof the upstream is alive" — plus the matching `tasks.md` line, and
ruled it REFUTED as "a deliberate, documented design choice … the code correctly
implements what was specified, including the specific reasoning the finder is now
second-guessing." Nothing in that verdict's wording or confidence distinguishes it
from a refutation on the merits, which is what makes it expensive: a proven finding
was dropped for the one reason that cannot be checked by reading the code. It was
caught by asking git instead — `git log -1 --format=%h -S "equally good proof" --
<design.md>` returned nothing, because the sentence existed in no commit, only as
an unstaged `+` line written minutes earlier. With the "intentional" leg void, the
finding stood, and was fixed.

A second, generalizable error rode along in the same verdict: it quoted a spec rule
governing a *different decision* than the finding was about — what to write for a
row that was attempted, versus whether to keep attempting further rows — and
treated it as dispositive. Hence the second rule in `reference.md`: a passage
refutes a finding only when it governs the same decision.

**Rejected.** Keeping spec and design docs out of the refuter's brief altogether.
That gives up the refutation this step is most valuable for — a finding that
asserts something the code never promised, killed by the contract saying so — to
fix a dating problem. Also rejected: telling the refuter to discount documentation
generally, which is the same loss by degrees. What the refuter lacked was not
skepticism, it was the timestamp, and supplying that is cheaper than blinding it.

**Not a claim that refuters can no longer be fooled.** This closes one failure
mode — circular intent, where the change under review is quoted back as its own
justification. A refuter can still be wrong about reachability, about what a caller
guarantees, or about what a genuinely committed spec means.

**Where this stops applying.** Only to doc text authored in the same session as the
code, or otherwise uncommitted and in flight. Refuting a finding against genuinely
pre-existing, committed spec is exactly what a refuter is for, and nothing here is
a licence to discount it: a committed contract saying the behavior is intended is a
real refutation, and provenance checked once and found to predate the change settles
the question rather than reopening it.

## Step 6 resumes the finder; the refuters and the next find pass stay cold

**Decision.** Within an iteration, Step 6 does not spawn a fresh fixer by
default. It resumes that iteration's Step 3 finder — the one finder, or each
slice finder that still has a survivor when the find was split (see *The find
runs in parallel slices*) — passing the surviving findings, the refuter
verdicts, and Step 5's fix-conflict notes. On Cursor the resume is the Task
tool's `resume`; on Claude Code it is `SendMessage`. A fresh agent call —
the slug the find ran on, full brief — is the fallback, used only when that
finder is no longer reachable (errored, session ended, or it belongs to an
earlier iteration).

**Why.** Nothing mutates the source between Find and Fix: Step 4 only adds test
files, Step 5 only reads. The finder has already read its files in full —
every changed file when it was the one finder, its slice when the find was
split — traced each candidate's reachability, and run the candidates. That is
the most expensive context in the loop, and exactly what a cold fixer spends
its first tokens rebuilding. There is no independence to protect here: the
fixer was never a check on the finder — it is handed the surviving findings as
facts to fix, and the refuters have already done the checking.

**Consequence, accepted.** A finder fixing its own findings is anchored on the
framing it built — it may defend its diagnosis rather than notice a simpler
fix. Two things bound that: Step 6's prevention question ("is there a better
approach?") is asked either way, and Step 8 guarantees the fixes get a fresh
pair of eyes — the next iteration's finder is cold by this entry's own scope
rule, and a run never ends on an iteration that fixed something.

**Rejected.** Spawning a fresh fixer every time, which is what
the earlier wording implied — it re-billed the finder's whole investigation for
no independence gain. Also rejected: retiring the byte-stable prompt prefix
rule shared between Steps 3 and 6 as obsolete. It still governs the fallback
path and the Step 3 spawns themselves, which repeat every iteration.

**Where this stops applying.** This is within-iteration reuse only, and it does
not extend in either direction. A split find does not change that: each slice
finder is resumed only to fix its own survivors, and two of them do not write
the same file.

- **Not to Step 5's refuters.** Their entire value is independence — an agent
  that has not seen the finder's reasoning (see *A refuter judges findings, not
  proposals*). Resuming the finder as a refuter, or letting one refuter see
  another's reasoning, destroys the step to save its cost. Every refuter stays
  fresh, every time, no exceptions.
- **Not to the next iteration's Step 3 finder.** Step 6 rewrites the files, so
  a resumed finder's context describes code that no longer exists — findings
  against a stale version are worthless (Step 3's own backgrounding rule), and
  the record in *An iteration that fixed something is never the last one* is
  that iteration 2 finds bugs iteration 1's fixes created, which only a fresh
  read of the fixed code catches.

## The find runs in parallel slices

**Decision.** The parent scopes the staged diff, launches the finders
together, and merges their lists. It does not hunt, and it does not re-read
the files those finders read. How many finders comes from the changed-line
count (*Light by default, heavy on request*), at most four. Two or four
split by area when the change has at least as many areas as finders, and by
bug class otherwise. Never both.
Cursor launches them as `Task` subagents, `subagent_type: generalPurpose`,
`run_in_background: true`, all in one message. Each prompt is the Step 3
template, filled in, because a Cursor subagent cannot see the parent
conversation.

**Why.** Harsh reported the skill much slower than Bugbot. Bugbot is one
single-shot reviewer: the review-bugbot skill launches exactly one subagent
and returns. This skill was one finder walking every file and every question,
then the parent reading those files again at Step 0 before that finder
started. The wall-clock was the sum. No Slack message of Harsh's turned up
to quote; the report this change answers is that one, as relayed: the
slowness is the single agent, and the fix is parallel independent work, not
a thinner hunt.

**Rejected.**
- **Skipping a step, or a cheaper model than the role's, to go faster.**
  The contract is unchanged: reachability, an observed command, a red test, a
  separate refuter, the suite. A faster run that files guesses is a different
  skill. Which model each step uses is the next decision, and an agent does
  not get to reopen it by skipping down a role's list.
- **One finder per file, or area slices that are then split by class.** That
  is dozens of agents on a short diff, and it cuts a caller off the code it
  calls. The cap is 4. Up to 50 changed lines is always one finder in a
  light run (*Light by default, heavy on request*).
- **The parent re-reading each slice "to be sure".** That puts the serial
  read back in front of the parallel one. Merge is a union and a dedupe
  (same file, same wrong outcome). Disagreement is not a refutation; Step 5
  still is.
- **`explore` or any read-only subagent for the find.** A finder that cannot
  run its candidate reports the false bugs this skill exists to drop.
- **Resuming the previous iteration's finders for the next find.** Step 6
  rewrites the files. The next find stays cold, as the entry above already
  says.

**Where this stops applying.** Prove, the refute judgment, and the suite are
not sliced away. Step 4 stays in the parent because the merged candidate is
already a specification and a fresh agent would rebuild it. Refuters stay
one per proven finding, launched together, and the cap of 4 does not drop
any of them. A host that cannot nest subagents runs one in-process find and
says so — that is the same hunt, not a skip.

## Light passes after the first read only the fixes' delta

**Decision.** In a light run, iteration 1 reads the whole staged change.
Iterations 2 and 3 read the delta: `git diff -M` between the tree the last
pass read and the tree staged now, both recorded with `git write-tree`, plus
each touched file in full, the whole change for those files as context, and
the findings the last fixes closed. An empty delta ends the run clean. A
delta-pass survivor outside the delta's lines makes the next iteration a
full pass; on iteration 3, which has no next pass, the `budget` root cause
covers the whole change instead. A heavy run re-reads the whole change every
iteration. In both modes a settled list — candidates dropped as unproven,
refuted, or reported because no test can show them — goes to every later
finder, which does not report them again unless their lines changed since
the tree they were settled against. Step 7 now ends by
staging the iteration's fixes and tests, so the next pass can see them.

**Why.** A second full read of an unchanged change is the most expensive
part of a run that found something, and most of what it reads is code a
finder just read. The bugs a later pass exists for are in the fixes (*An
iteration that fixed something is never the last one*), and the delta is
exactly the fixes. The settled list stops a loop: the same untestable
candidate reported every iteration, keeping the run going with
nothing to fix. The staging step was missing before this change: iteration
2's finder reads `git diff --cached`, so a fix left in the working tree was
invisible to it.

**Accepted cost, said plainly.** The measurement in *An iteration that fixed
something is never the last one* is iteration 2 finding 7 bugs, only two of
them created by iteration 1's fixes. The other five were misses in the
original code, and a delta pass is less likely to find those. Three things
bound the loss: the first pass is sized to the change, the delta finder
reads every touched file in full and may report anything in them, and a
survivor outside the delta sends the next pass back to a full read. A user
who wants the second full read asks for heavy.

**Rejected.**
- Re-reading the whole change on every light pass, as before. That is heavy
  mode, now on request.
- Reading the delta hunks alone, without the files. A fix's bug is usually in
  how it meets the code around it, the reason every finder reads whole files.
- Deriving the delta from the working tree. Step 4's tests and unstaged edits
  would pass for fixes; the staged trees are what the commit will contain.
- Reopening a settled candidate when the pass's own diff shows its lines. A
  full pass reads `git diff --cached`, which shows every line of the change,
  so every settled candidate would reopen on the first full re-read. The test
  is whether the lines changed since the tree it was settled against.
- A fourth iteration when iteration 3's delta finds a survivor outside it.
  There is no fourth iteration (*There is no fourth iteration; the abort
  reports root causes*); the whole change goes to the user as a `budget`
  cause instead.
- `.` pathspecs on the delta. From a subfolder they hide every fix outside
  it, and an empty delta ends the run clean.

**Where this stops applying.** The anti-evasion rules are about whether a
pass runs, and a delta pass still runs after every fix — rule 2's "code
written since the last clean pass" is the delta. It does not change the
budget: iteration 3's fixes are still a `budget` root cause. Heavy is not
affected.

## Light by default, heavy on request; the finder count follows size

**Decision.** A run is light unless the user asks for a heavy hunt in the
conversation, or a caller's brief says `mode: heavy`. The finder count comes
from the reviewable changed lines, counted with `git diff --cached -M
--numstat` over `:(top)` pathspecs, the rule-change chart excluded: 1 finder
up to 50 lines, 2 up to 300, 4 above. A plain `.` would count only the
folder the agent stands in. A heavy run uses 4 on every iteration, on the `finder_heavy`
model. Two or four finders split by area when there are enough areas, and by
bug class otherwise, never both. Only a heavy run says so in the trailer,
as `, heavy` at the end of the value.

**Why.** The old sizing rule had two branches and four conditions (under 40
lines; or one area, at most 3 files, under 150 lines and one class), and
past them the count came from how many areas or classes the agent could
name, so the same diff could get one finder or four. A count from git is the
same every time and can be checked from the report's `scope` line. The steps
— 50 and 300 — keep a typical small commit on one agent and give a large one
the full four. Heavy exists for the change the user is worried about: they
pay for four readers and a stronger finder model on purpose, so the agent
neither picks it for them nor drops it to save time.

**Rejected.**
- The agent choosing heavy when the change "looks risky". Cost is the user's
  call, and a mode an agent can raise is a mode it can lower.
- Recording `light` in every trailer. Light is the default, so every old
  value already means light, and a new word on every commit adds noise.
- The finder count in the trailer. The hook does not check counts, and the
  report already has them.
- Excluding files from the count without naming them. An agent that wants
  one finder can drop files to get under 50; naming them in `scope` is what
  makes that visible.

**Where this stops applying.** The count picks how many finders read, not
whether the hunt runs: a one-line change still gets the full hunt from one
finder (*Every anti-evasion rule was added after it was walked through*).

**Follow-ups, not built.**
- *Heavy by default for risky paths*, from a path list in the same config
  key. It needs a list someone maintains and a rule for when a path counts.
- *Callers forward heavy.* The `commit` and pull-request workflow skills,
  where installed, run this skill for the user; when the user said "heavy", their brief should
  carry `mode: heavy`. One line in each, outside this skill.

## Models by role, from settings

**Decision.** Each subagent runs on its role's model: `triage`,
`finder_light`, `refuter`, `rule_check`, `mechanical`. `scripts/models.py`
holds one ordered list per role and prints it. The agent passes the first
entry the host lists: an exact slug, a family word (its highest version,
`high` then `thinking` on a tie), or `inherit`, which ends every list. A
person overrides a role in the kapo-skills config file, under the
`bug-hunter` key. A resume does not pass `model`; the finder was already
started on its slug. A launch that fails moves to the next entry that
resolves to a different slug: `grok-4.7-high-fast` then `grok` is the same
model on a host that lists it, and retrying it would spend the retry on the
slug that just failed.

The defaults: finders and triage on Grok first (`grok-4.7-high-fast`, then
any Grok). Refuters on Sonnet, then Opus. The rule check on Grok, then
Sonnet. Mechanical work on Grok, then Haiku. Steps 4 and 7 stay in the
parent loop, as before.

**Why the finders stay on Grok, and nothing defaults to the heaviest
model.** On 2026-10-15 Harsh reported that the skill always picked the model
with the most weights. That was Fable, and a run through it was slow and
burned the budget fast enough that people stopped running the skill. The
instruction those agents were obeying was "strongest available model", with
"omit `model` only when you cannot tell which slug is strongest". Read as
written, that is Fable whenever Fable is listed. Grok 4.7 is the model the
team wants for the find: strong enough for the hunt, and cheap and fast
enough that the skill still gets run.
No list puts the heaviest model first, and a list can only be walked down,
never skipped past.

**Why the refuter moved off Grok.** The refuter decides which proven bugs get
fixed and which get dropped, so its accuracy matters most of any judgment in
the run. It also runs only on proven bugs, a handful per run at most, so a
more careful model there costs little next to the find. The earlier version
of this entry pinned the refuter to Grok, rejecting "a capable model" because
each refuter, free to pick, would pick Fable. A fixed list answers that
worry: Sonnet first, Opus only when Sonnet is missing, never "whatever is
strongest".

**Why a setting, and why there.** A team without Grok, or with another
host's slugs, has to be able to run the skill without editing `SKILL.md`.
The defaults live in one script, so `SKILL.md` never repeats a slug and the
two cannot drift. A team changes them in its clone; one person overrides a
role in `~/.config/kapo-skills/config.json`, the file `manage-skills`
already keeps, which preserves keys it does not own. A damaged config warns
and falls back to the defaults; it never blocks a hunt.

**Rejected.**
- Leaving "strongest available" in place and trusting the agent to notice the
  cost. That sentence is what selected Fable.
- A per-repo config file. The code under review would choose its own
  reviewer: the single input supplied by the party being checked, which is
  the objection in *The hook is never told that a run is in progress*.
- An environment variable as the setting. Agent shells do not reliably
  inherit one, and nobody can read it back from the report.
- Moving prove and verify onto a subagent model. Those steps are cheap on
  purpose, and the red test is the check.
- Repeating the default slugs in `SKILL.md`. Two copies drift.

**Where this stops applying.** An agent that is itself the finder, because
the host has no subagents, cannot switch its own model. It says so and runs
the hunt. A role's list is not a reason to skip a step, drop a refuter, or
pick an entry further down to finish sooner — that rejection is in the entry
above.

## Finders and refuters never all run on the main agent's model

**Decision.** When the finder role and the refuter role would both resolve to
the model the main agent runs on, the refuters move to the next entry in the
`refuter` list that is a different model. If none is, the report says so.
"The main agent's model" is the slug the host runs it on, and `inherit`
counts as that slug. It is not the `Co-Authored-By` value, which is a display
name such as `Cursor <cursoragent@cursor.com>` and never matches a slug.

**Why.** The main agent usually wrote the change under review. A model is
likelier to miss a bug it wrote, for the same reason it wrote it, and the
refuter, defaulting to skepticism about findings, is likelier to wave one
away as intended. The default lists already keep finders on Grok and
refuters on Sonnet, so this rule rarely fires with them. It guards the setup
where every role falls back to one model: a host with no Grok and no Opus, or
a config that lists the same slug everywhere, where `inherit` would put the
whole run on the author's model. This rule is new; the Grok pin above was
about cost and speed, never about independence.

**Rejected.** Requiring every role to differ from the main agent's model. On
a host with two models that cannot be met, and triage and mechanical work
are not judgments about the author's code.

**Where this stops applying.** In-process, when the host has no subagents,
there is only one model; the report says so. Independence in the sense of
*Step 6 resumes the finder* — a refuter that has not seen the finder's
reasoning — is a separate rule and does not change.

**Follow-up, not built.** A stricter form: the refuter always differs from
the main agent's model when its list allows, not only when the finders also
match. The refuter judges the author's code, so it is the step where shared
blind spots matter most. Deferred until a run shows the looser rule letting
a bug through.

## Triage applies to the hook's own reports

**Decision.** A hook report is an input to triage, not an instruction to run the
whole skill.

**Why.** It sets the price of a false alarm. A hook that fires wrongly and costs
a thirty-minute run is one people uninstall; one that costs ten seconds of triage
plus an amended trailer is one people tolerate while it gets fixed.

**Not a licence.** It does not make a wrong report harmless — repeated misfires
are a bug in the hook to be fixed, not a cost to absorb. It stops one wrong
report from costing a working session, and nothing more.

## The trailer rule is stated inline, not only pointed at

**Decision.** `SKILL.md` states at the commit step that the trailer is passed as
`--trailer` and never typed into the message. `reference.md` keeps the
explanation, the shapes table and the worked examples.

**Why.** Two commits in one week landed with a hand-written `Bug-hunter:` line
and no trailer git could see, and the hook reported both. One was the main
agent, one an independently-run subagent on an unrelated fix; both were repaired
after the fact with `git commit --amend --trailer`. `reference.md` already said
all of this, correctly — neither agent had opened it, because `SKILL.md`'s
commit step only pointed at it, and a pointer gets followed after the mistake
rather than before. By the time an agent reaches the commit it has the whole
message composed in its head and runs `git commit -m` with the line already in
it. Nothing in the main flow said that step had a sharp edge, so nothing
interrupted that.

**Rejected.** Copying the trailer-placement section into `SKILL.md`. What failed
was not a missing explanation but a rule that was absent from the flow, and two
copies of a table drift apart — the failure this file's opening is about. What
went inline is the rule, the verify command, and the repair; the *why* stays
here in one place.

**Measured, because the received account was wrong.** "A blank line before it
makes it a new paragraph" is not the failure — a `Bug-hunter:` line alone in the
last paragraph parses fine, blank line and all. The shapes that actually lose it
are anything landing after it in a later paragraph (the mandated
`Co-Authored-By` footer is the common one), a prose line beside it in the same
paragraph, and an unindented wrap. `reference.md` asserted the blank-line
version and is corrected. Run the shapes against a scratch repo before writing
this kind of claim down.

**Where this stops applying.** Only to rules an agent *executes* at a named step,
where getting one wrong produces a wrong artifact. Procedure — how to drive a
test red, how to shape a report — stays in `reference.md`. Inlining that class
too is how `SKILL.md` becomes the document nobody finishes.

## The mint script is located with a two-target fallback, not one hardcoded path

**Decision.** Every instruction that names `mint-trailer.sh` tries
`~/.agents/skills/bug-hunter/scripts/mint-trailer.sh` first and falls back to
`~/.claude/skills/bug-hunter/scripts/mint-trailer.sh` — a two-line
`MINT=...; [ -x "$MINT" ] || MINT=...` in both code examples, and both paths
named in the prose mention.

**Why.** Adam watched agents struggle to find the script at the commit step.
The docs hardcoded the `~/.agents/skills` path alone, but `manage-skills`
installs every skill into two independent targets (`~/.agents/skills` for
cross-tool agents, `~/.claude/skills` for Claude Code) and its own docs warn
that a real install can populate only one — its examples hedge every path with
an explicit `# or` between the two for exactly this reason. An agent whose
install only populated `~/.claude/skills/bug-hunter` was sent to a path that
does not exist, with no fallback, and had to guess. Both targets symlink the
whole skill directory, so the script sits at the same relative location under
each — the fallback is safe by construction.

**Rejected.** Searching the filesystem as the primary instruction — the two
documented targets cover every install `manage-skills` produces, and a search
is slower and vaguer than two known paths. A one-line "if neither exists,
search under both" escape hatch stays in `reference.md` for installs made by
some other mechanism.

**Where this stops applying.** This is only about *locating* the script. The
minting mechanism — `git write-tree` over the staged index, run after the last
`git add`, output passed as `--trailer` — is unchanged, and so is the rule that
only the path to the script is absolute, never the git command it runs.

## The commit is assembled by a script, not by hand

**Decision.** `SKILL.md`'s commit step names one command —
`scripts/commit-with-trailer.sh <subject> <body> <Bug-hunter value>
[<Co-Authored-By value>]` — for every commit this skill makes, skips included.
The hook's report names the same script wherever it used to show a
`git commit … --trailer …` example. `--trailer` and `mint-trailer.sh` are still
the mechanism; `reference.md` now documents them as what the script does, not
as what the agent types.

**Why.** The previous two entries were each a response to the same failure —
a `Bug-hunter:` line typed into the message body — and each was correct: the
rule went inline, in bold, with the exact command shown twice, and the mint
step got a path that resolves. Agents kept typing the trailer into `-m` anyway,
several times in one evening, in a session with `SKILL.md` loaded. So the
failure is not ignorance of the rule. It is assembly under time pressure: a
"trivial docs commit" arrives with the message already composed, `-m` is the
habit, and the trailer goes where the `Co-Authored-By` footer goes — the body.
A rule that says "assemble it differently" competes with that habit at the
moment the habit is strongest and attention is lowest, and it loses some
fraction of the time no matter how it is worded.

A script removes the assembly. The trailer value is an argument, and the only
way to supply it is the right way; the skip-or-mint decision is read off that
value rather than remembered; the `Co-Authored-By` — the footer that actually
pushes a hand-written trailer out of the block — is an argument too; and the
two-target lookup happens once, for the wrapper, because it finds
`mint-trailer.sh` next to itself. What is left to get wrong is the one thing
that was never the problem: which path the skill is installed at.

The hook names the script for a different reason. Its report is the one text an
agent provably reads at the moment of failure — every one of the repaired
commits was repaired because the report said so — and its own example was a
hand-built `git commit -m … --trailer …`. An agent acting on the report re-did
the assembly step, by hand, that had just gone wrong. Naming the script there
stays inside *The report states facts and stops*: a placeholder call with a path
under `~` is context-free in exactly the way the old example was, and the text
describes how this skill commits, not what to do with the named sha.

**Rejected.**
- Stronger prose, or a third example. Two bold statements and two examples had
  already failed on the same agent in the same session; this file's opening is
  about not re-solving a solved problem the same way a few lines away.
- Having the script stage as well as commit. What to stage is a judgement
  (*Committing*: never `git add -A`), and folding it in would make a
  correctness tool decide scope.
- Having the hook print the exact repair for the reported commit. That is the
  remedy machinery *The report states facts and stops* removed, and the reason
  it was removed — the hook cannot see the reader's HEAD — is unchanged.
- Keeping the hand-typed `git commit … --trailer` form in `SKILL.md` beside
  the script "for when the script is not installed". A second documented way
  is the one that gets used under pressure, and both install targets carry
  the script whenever they carry the skill.

**Found by running this skill over the script before it landed.** Four
reproduced, one refuted; each is a rule the script now enforces rather than a
one-off patch:

- **A `$(...)` inside another command's argument list is not covered by
  `set -e`.** `set -- "$@" --trailer "$("$mint")"` carried on when the mint
  failed, because `set` itself returned 0, and handed `git commit` an empty
  `--trailer ""` — which git 2.54 refuses and every earlier git with `--trailer`
  (Apple's 2.50.1 on this machine included) accepted, landing the commit with
  its binding missing or its block split. Capture to a variable with `|| exit`
  first; never let a failing-capable substitution ride inside `set --`.
- **The values are validated before anything with a side effect runs.** An
  empty or whitespace-only value became `Bug-hunter:` with nothing after it,
  which git reads as no trailer. A line break inside argument 3 *or* 4 landed
  an unindented continuation that ended the trailer block for everything after
  it — the freshly minted binding included — with the wrapper exiting 0 and the
  hook then advising "use the wrapper". Both are refused with exit 2; trailing
  whitespace is trimmed rather than refused, because a heredoc-built value ends
  in a newline and git trims it anyway. *Rejected:* indenting the continuation
  so git reads one folded trailer — a legitimate shape the hook already
  `unfold`s, but a more generous contract with more surface, and a two-line
  reason belongs in the report, not the trailer.
- **The commit pins `trailer.ifexists`, `trailer.ifmissing` and
  `trailer.separators` for that one command.** git matches trailer tokens by
  prefix, so `Bug-hunter-Tree` "already exists" whenever `Bug-hunter` does: a
  user's `ifexists=replace` made the mint overwrite the `Bug-hunter` trailer,
  `doNothing` dropped the mint, `ifmissing=doNothing` dropped all three. The
  write side of the same principle the hook's `g()` applies with
  `log.showSignature=false`: git means git, not git plus the user's config.
- **Refuted, and why:** a skip value with a leading space (`" skipped …"`)
  missed the `[Ss]kipped*` test and got minted. Cosmetic — the binding is a
  true statement about the landed tree, the hook and the audit ignore it, and
  the input is a typo. The trim above removes it incidentally; no code exists
  for it on purpose.

The second pass, over those fixes, found two more of the same kind — a value
the script trusted without looking at it:

- **The subject is checked for emptiness too.** `git commit -m ""` is refused
  by git; `git commit -m "" --trailer "Bug-hunter: …"` is not, because the
  trailer makes the message non-empty — and then the trailer *is* the title
  paragraph, so git reads no trailer at all. The wrapper had turned a refusal
  git would have made into a landed, unchecked commit. Refused with exit 2; the
  trim is used for the test only, and the subject reaches `-m` as given.
- **The value the script mints is held to the same standard as the two it is
  handed.** `mint-trailer.sh` captured `git write-tree 2>&1`, so anything git
  said on stderr while succeeding — `GIT_TRACE=1`, a `core.fsmonitor` hook
  path from another machine — arrived ahead of the hash, and the wrapper passed
  that two-line value straight to `--trailer`. It now requires exactly one line
  of `Bug-hunter-Tree: <hex>` and exits 1 otherwise, naming what it got. The
  `2>&1` itself was the cause, in a committed sibling this change did not
  originally touch — reported rather than fixed in that pass, and fixed as its
  own follow-up (see below).

The third pass, over those two guards, came back clean. Its one candidate —
a `#`-first subject under a user's `commit.cleanup=strip`, which git deletes
after the wrapper accepted it — was refuted: plain `git commit -m "#123 …"` is
refused by git under that setting, so nobody who has both ever reaches this
script. No guard was added; a `-c commit.cleanup=whitespace` pin would be the
shape if one ever is, since `core.commentChar` makes any textual check a
guess.

**Where this stops applying.** The script creates a commit; it does not amend
one. Adding a trailer to a commit that already landed — the triage table, a
hook report on a local commit — stays `git commit --amend --no-edit --trailer
"…"`, because amend is exactly the case where "which commit is HEAD for the
reader" matters and that judgement belongs to the reader. Nor does this change
what the binding attests to: an agent that calls the script with counts it
invented still passes, as *The trailer is minted from the tree* already says.
And the `commit` skill's own path when bug-hunter is not installed has no
script to call and keeps `--trailer`.

**Both root causes the run reported were fixed as a follow-up, same day.**
`mint-trailer.sh` now captures `git write-tree`'s stdout and stderr
separately — a temp file for stderr, read back only for the failure message —
so a successful write-tree can no longer leak anything onto the same line as
the hash, regardless of `GIT_TRACE` or a stale `core.fsmonitor` path. And the
hook's `g()` now pins `trailer.separators=:` alongside `log.showSignature=false`,
closing the read-side half of the trailer-config problem the write-side pin
above only ever covered half of: a repo configured without `:` in that set no
longer blinds the hook to a real, correctly-bound trailer. Both are exercised
by their own tests (`test_mint_trailer_does_not_leak_stderr_into_a_successful_binding`,
`test_a_nondefault_trailer_separators_config_does_not_blind_it`), not just
described here.

## A run writes to the code under review, never to this skill's own files

**Decision.** What a run learns — an approach reverted, a finding refuted, a gap
the user chose to accept — is knowledge about the codebase under review, and it
is recorded there. This skill's `DECISIONS.md` is about this skill's design; a
run touches it, or any other file of the skill's, only when the skill is itself
the code under review. Stated in `SKILL.md`'s *Never* list, at Step 9's
write-down, and in the header, which no longer sends Step 6 here before a fix.
Where in the codebase: its stated convention (`AGENTS.md`, `CLAUDE.md`,
`CONTRIBUTING.md`) first, then a home it already has, then a comment at the
site for a rejection about one site, and a new file only when none of those
exist — `DECISIONS.md` beside a `SKILL.md`, `docs/decisions.md` elsewhere. Step
5's refuter brief and Step 6's pre-fix read name the same record.

**Why.** `SKILL.md` said "add it to the skill's `DECISIONS.md` (create one if
there is none)", and its header sent Step 6 to this file "before writing a fix".
Both sentences were written while this skill was developed by running it on
itself, where the code under review and the skill are one directory and "the
skill's `DECISIONS.md`" and "the codebase's record" name the same file. Pointed
at anything else, the two meanings split, and the sentences resolve to the wrong
one: a run over an ordinary TypeScript project reverted two approaches, and the
agent following Step 9 proposed creating a `DECISIONS.md` for it — a note about
that project's behaviour, headed for a file about how bug-hunter works, where
nobody debugging that project would read it. The project's own `AGENTS.md`
already said rejected alternatives belong in an OpenSpec change's `design.md`,
and its source recorded one-site rejections as comments in a settled idiom.
Neither passage led there; the user had to ask what the agent meant.

The defect is one of kind, not of a missing fallback. Seventy lines below, option
2 had a placement chain for accepted gaps — a spec's Open Questions, an existing
change, `docs/`, the closest README — and the chain was fine; what it lacked was
the first stop, the codebase's stated convention, and any notion of a comment at
the site, which for a rejected implementation approach is where the record is
read: by the person about to make the opposite choice, standing at that line.

**Rejected.**
- Reading it as a gap and adding a chain under "the skill's `DECISIONS.md`, or
  the codebase's equivalent". The phrase presumes a referent most subjects lack,
  and it keeps the wrong default; the addendum is what gets skipped under
  pressure.
- One chain for both kinds of record. They differ in reader: a rejection is read
  by someone about to make the opposite choice, which is why it can live at the
  site; a gap is read by whoever picks it up later, who is standing nowhere in
  particular. One lookup, two lists of homes.
- A root `DECISIONS.md` as the fallback for any codebase. That imports this
  repository's convention into someone else's; `docs/decisions.md` sits beside
  the `docs/open-questions.md` option 2 already creates.
- Moving the chain to `reference.md` and pointing at it. Placement is a rule an
  agent executes at a named step, and getting it wrong produced a wrong
  artifact; per *The trailer rule is stated inline, not only pointed at*, the
  rule is inline and `reference.md` keeps the shapes.

**Where this stops applying.** When the subject under review is this skill, it
is the codebase, and every rule above lands here: a run over `scripts/` or
`SKILL.md` writes its reverts to this file, as this file's history shows. Nothing
here changes what an entry contains — the decision, why, what was tried and
rejected, and where it stops applying — only where it goes.

---

## A caller that commits gets the result, not the commit

**Decision.** A brief that says "caller commits" runs the whole skill and stops
at Step 9 before the commit. The run leaves the change staged, prints the
report, and ends with a fixed result block that `scripts/caller-result.sh`
mints and prints: the `Bug-hunter:` and `Bug-hunter-Tree:` lines, then the open
decisions with a count. The caller commits, passing the two lines through as trailers.

**Why.** Some callers build commits themselves — Igor
(adamstallard/igor#139) creates them through GitHub's API after an LLM step and
never runs `git commit` locally. The skill already had the pieces: Step 9's
"commit or leave it for review", and the hand-off footer for a run inside
another agent. What it lacked was a contract a program can rely on: a trigger,
a place to stop, and output in a shape a parser reads.

The mint moves with the commit, not ahead of it. A skill signs the snapshot it
worked on, and whatever creates the commit makes its tree equal that snapshot —
the same rule the commit script follows, where minting and committing happen
at the same moment. Here they are two moments, so the caller carries the
obligation the script used to discharge.

Open decisions go into the block because a headless run has no picker that
reaches anyone. *A question is asked when the user sees it* already says a
report that reached an agent has asked nobody; the block makes that hand-off
explicit and parseable.

**A script prints the block; the agent never types it.** `scripts/caller-result.sh`
takes the `Bug-hunter:` value and the open decisions, runs the mint itself
(none for a skip), and prints the block through the shared library's
`result-block.sh`, the format's one definition. The first version of this mode
had the agent write the block by hand, copying the mint's output into it. That
is the assembly *The commit is assembled by a script, not by hand* removed:
hand-typed trailers went wrong under pressure however the rule was worded, and
a block a program parses fails the same way — a line retyped, a count off by
one, a tree line from an earlier mint. Decided by Adam, 2026-09-27, for every
skill that ends this way, which is why the format lives in the library.

**Rejected.**
- **A prompt-only convention in the caller** — "run bug-hunter, but don't
  commit, and print the trailer". It drifts: each caller words it differently,
  and nothing in this skill says where to stop, when to mint, or what to print.
  It also fights Step 9, whose commit step is written to be hard to skip; a
  caller's sentence against that text loses some of the time, the same way
  prose lost to the habit in *The commit is assembled by a script*.
- **Reusing report-only mode.** It leaves the change for a person to review
  and prints nothing a program can take. It mints nothing, so the caller would
  have to mint itself — recalling the step the binding exists to make
  unrecallable.
- **Answering open decisions by default when nobody can be asked.** A choice
  made on the user's behalf; *A question is asked when the user sees it*
  rejects it for the same reason.
- **The block written by hand from a documented format.** The first version
  of this mode. See the paragraph above.

**Where this stops applying.** Only when the brief says so. A run inside
another agent with no such phrase commits as usual — the `commit` skill relies
on that. The mode moves the commit and nothing else: triage, the loop, the
full-suite gate and the report are unchanged, and a caller cannot use it to
skip them. The binding attests to the tree at the mint; it says nothing about
a commit whose tree differs, which the hook reports as it would any other.
The script ends at its own output: the agent still relays that output into
its reply, and a caller parsing the reply gets whatever the relay kept. SKILL.md
says to end with it whole and unedited; nothing enforces it.

---

## Other skills' trailers ride on this skill's commit

**Decision (Adam, 2026-10-01).** Step 9 commits once with every installed
trailer skill's value, under the shared library's rule
([Every installed skill's trailer, on one commit](../../lib/commit-trailer/DECISIONS.md#every-installed-skills-trailer-on-one-commit)).
When prose is installed, Step 9 runs its two `check` calls and passes the
`Prose:` value to `commit-with-trailer.sh`.

**The script's argument rule.** Leading `--verified-value <verifier> <Key>
<value>` families, any number, passed to the library unchanged, which
validates them; then `--`, required after a family; then the four positional
arguments as before. Why each part:
- **Only `--verified-value`.** The script adds the Bug-hunter family and
  `Co-Authored-By` itself. A `--minted` or `--minted-by` family would be a
  second mint path the script does not vouch for, and `--co-authored-by` a
  second way to pass the fourth argument. Any other word in front is read as
  the subject, so the library's option names are refused there, exit 2.
- **`--` required after a family.** Each family takes three words, so an empty
  unquoted variable inside one, or a forgotten `--`, shifts the subject, body
  and value one place. Requiring `--` refuses that, as the library does for
  its own options.
- **`--` allowed with no family,** so the separator means the same in both
  forms; a subject of exactly `--` is refused.

**Rejected.** The library's other options passed through as well: nothing
needs them, and each is a way to land a family this skill did not mint.

---

## Triage reads the diff, not a label

**Decision.** Triage classifies a change by what its diff touches —
formatting only, a pure rename or move, only docs, tests or specs, git's own
revert or merge — and reviews everything else. Nothing in this skill asks for
a commit message first or reads a subject prefix. Decided by Adam, 2026-10-01.

**Why.** The public skills impose no commit convention, and
triage built one in: agents were told to write the message first with an honest
label (`WIP:`, `STYLE:`, `CHORE(move):`, `DOCS:` and so on) so triage could use
it as a skip signal. The label was never decisive. "A label only skips if the
diff agrees with it" meant the diff already made every call; the label was a
hint that cost a convention in every repository that ran the skill.

**The exception: work in progress.** It is the one intent a diff can't show —
half-finished logic looks exactly like finished logic. So a checkpoint is
skipped only when the user asked for one in the conversation, never because a
subject says so. It still defers rather than exempts: the code is reviewed when
it lands in a commit that is not a checkpoint.

**Rejected.**
- **Labels as an optional hint.** Any label triage reads is a convention agents
  learn to write, and a repository with a different one gets wrong skips or
  reviews it can't explain. The hint added nothing the diff didn't already
  decide.

---

## A system-spec rule break continues or pauses; the pull request decides

**Decision.** In a repo with system specs (`SYSTEM_SPECS.md` or any tracked
`*.system-spec.md`), a separate system-spec rule check reads the rules that
cover the change, as committed at `HEAD`, and reports each break: code that
does what a rule forbids or stops doing what it requires, a cited test or
other evidence removed or weakened, or a rule edited in its own spec file.
Each break has one of two outcomes at commit time:

- **Continue**, when a change doc committed before the code approved it
  (in `HEAD`, by a commit this conversation did not make), or when the user
  already acknowledged it in this conversation, in a reply to a question that
  named the rule ID. It goes in the rule-change chart and the commit
  proceeds.
- **Pause**, for any other break. The user answers *continue* (intentional;
  recorded as `acknowledged`) or *stop and fix* (no commit; the code is
  fixed and a new run checks it). Until then, no commit, no mint, no result
  block.

Commit time never edits a spec and never decides a rule's outcome. A
pull-request workflow skill, when installed, asks once per rule at the pull
request: update the spec, keep the old behavior, or skip for now. Without
one, the person settles each rule in a hand run of `maintain-system-spec`. The check runs in its own subagent
beside the finders, on checkpoints too, and on any skip that edits a spec.
In a repo with no system specs it is skipped with one line that points at
`create-system-spec`; without `maintain-system-spec`, which holds the brief,
with one line that says to install it.

**Why.** A system spec says what must stay true, and a change that breaks a
rule is either a bug or a decision. Only the user knows which. The hunt
cannot tell: a red test proves the code does something, not that the
something was unwanted. Most commits are bug fixes, and a bug fix should not
break a rule, so an unexplained break is worth one question. Whether the
rule or the code should give way is a larger question, and it belongs where
the code and the spec can land together — the pull request. Asking it at
every commit would ask it again for each commit that touches the same rule,
and the user wants one approval per rule, not one per commit.

The approval rule is the refuter's rule applied to a new question.
*Documentation written in the same session is not evidence of intent* found
an agent's own fresh design text quoted back as the reason a finding was
wrong. Here the same text would be quoted back as the reason a rule could
break. An agent can write both the code and the doc that justifies it, so
only text that existed before the code says a person wanted the change.

Holding the mint is what makes the pause real. The binding is the one thing
here an agent cannot produce from memory, and every commit path in this
skill goes through a script that mints it. A rule that said "ask first" with
the mint still available would be advice.

**Closed on purpose, because each is a way around the pause:**
- **A triage skip still runs the check when the diff edits a spec.** A
  spec-only commit is a docs skip, and it would let a rule be loosened in one
  commit and broken in the next, with the second commit reading the already
  loosened rule. The same goes for the hook-report amend of a skip-category
  commit.
- **A checkpoint runs the check.** The hunt on a checkpoint is deferred to
  the next commit that is not one. The rule check cannot be deferred that
  way: the next commit reads its rules at `HEAD` and diffs against it, so a
  break that landed in a checkpoint is invisible to every later commit-time
  check. The hunt's checkpoint rule is unchanged.
- **A `SPEC` or `DOCS` commit made earlier in this conversation does not
  approve.** The `commit` skill puts spec and doc slices first, so a change
  doc written with the code would otherwise be "committed before the code"
  by the time the code slice runs.
- **Rules are read as committed, never from the working copy.** Editing the
  spec in the working tree changes nothing the check reads; it shows up as a
  rule edited.

**Rejected.**
- **A per-rule decision at commit time** — update the spec, keep the old
  behavior, or accept the new behavior, with no mint until each was picked.
  This was the first draft. It decided the rule's outcome commit by commit,
  had the skill edit specs, and asked the same question again at the pull
  request, where the code and spec edits have to land together anyway. Two
  outcomes at commit time, and one decision per rule at the pull request,
  ask each thing once.
- **Treating a broken rule as an ordinary bug the hunter fixes.** A finding
  is fixed without asking because the code was meant to do otherwise. A rule
  break may be the change the user asked for, and fixing it would revert
  their feature.
- **Letting the hunter edit the spec to match.** That turns a bug into a rule,
  and the next agent then protects the bug — the reason
  `maintain-system-spec` never rewrites a rule to match code that breaks it.
- **Folding the check into each finder.** A finder hunts one slice or one bug
  class; a rule covers whatever files it covers, across slices. Every finder
  would read the same specs, and no finder would own the answer. One subagent
  reads the specs once, and the finder template stays byte-stable.
- **Counting spec or change-doc text written with the change as approval.**
  It is the change restating itself, as above.
- **Blocking commits in repos with no system specs.** The check is useful
  only where rules are written down. Blocking there would make the skill a
  gate on a format most repos have not adopted.
- **Stopping the hunt the moment a break is found.** That is the interim
  report and the check-in between iterations that *Every anti-evasion rule
  was added after it was walked through* removed. The pause waits in the
  Step 9 report with every other decision.
- **Counting the agent's reading of the conversation as acknowledgement.**
  "They asked for this" is a paraphrase made by the party being checked. A
  question that names the rule ID costs the user one answer and leaves no
  doubt.

**Where this stops applying.** Behavior no rule covers is not a break, and a
commit is never paused because something could be documented. A rule marked
`Evidence: (inferred)` is a claim, not a rule, as `maintain-system-spec`'s
format says, so breaking one is a note. Nothing verifies the check ran: the
binding attests to the tree, as it does for the find and refute passes. And
the "not made in this conversation" test rests on the agent listing its own
commits honestly. A doc committed in an earlier session by the same agent
passes it. That is accepted: the pull request still asks the user about
every rule change.

## Rule changes go to a committed log, one file per branch

**Decision.** Every break that continued gets an entry in
`system-spec-changes/<branch>.md`, beside `SYSTEM_SPECS.md`, the branch
name made path-safe (`/` to `--`, anything else outside `A-Za-z0-9._-` to
`-`) plus 8 characters of its git hash: rule ID, spec path, branch, the old rule quoted, the new behavior, the
lines, and the status (`recorded` with its change doc, or `acknowledged`).
The main agent writes it and stages it before the mint, so it lands in the
same commit as the code. A pull-request workflow skill, when installed,
reads this branch's entries, merges them with a fresh branch re-check, asks
once per rule, and writes the decision into each entry, in the same commit
as the decision's effect. Without one, entries stay undecided until the
person settles them in a hand run.
Entries are never removed. The format and lifecycle are defined once, in
[`maintain-system-spec/rule-check.md`](../maintain-system-spec/rule-check.md#the-rule-change-chart).

**Why.** The user wants the repo to keep a record of when and why each rule
changed, and that record has to survive the merge. A committed file lands on
`main` with the pull request, travels to every clone, and can be read by
anyone later, `maintain-system-spec` included. Writing the entry into the
commit that makes the change ties the two together: the entry's commit is
found from the file's own history, so the entry needs no sha field, and the
binding minted over the staged tree covers the entry as well as the code.
A later break extends only an undecided entry; once the pull request has
decided an entry, a new break of that rule is a new entry, so it gets its
own question.
The pull request also has to know which breaks the user already called
intentional, or it asks again what was already answered.

One file per branch, because many branches append at once. Parallel branches
never touch the same file, so the log never conflicts. A branch's entries are
the ones its file did not have at the merge base, so a reused branch name
starts clean and keeps the older entries as history.

**Not approval, and not a marker the hook trusts.** *The hook is never told
that a run is in progress* declines a file the agent writes to excuse itself.
This log excuses nothing. An `acknowledged` entry is not a reply in a later
conversation, and the pull request re-checks the branch from git and asks the
user about every rule, logged or not. Files under `system-spec-changes/` are
never a spec, never a break, and a commit touching only them is a docs skip.

**Why the binding still holds.** The entry is staged before the mint, like
any other file in the change, and nothing is staged after it. The binding
attests to the tree that landed, which includes the entry; it does not
attest that the entry is honest, any more than it attests to the counts in
the `Bug-hunter:` trailer. Under *caller commits* the entry is staged before
the result block is minted, and the caller commits it with the rest. The
block's format does not change, because a caller parses it for trailers,
not for a log.

**Rejected.**
- **An untracked file in the git dir.** The previous design. It was per
  clone, so a teammate's pull request could not see it, and it was gone after
  the merge, which leaves no record.
- **One shared file for the whole repo.** Every branch would append to it,
  and every pull request would conflict with every other.
- **Removing an entry once decided.** Then the log only lists what is still
  open, and nothing records how a rule came to read the way it does.
- **The commit message** — a trailer or a body line. The agent writes it, a
  new trailer key needs script, hook and library changes, and prose rewrites
  the body while a caller that commits replaces it.
- **No file, only the report and git.** Git can show that a rule broke, but
  not that the user called it intentional, so the pull request would ask that
  again before asking what to do. The user wants one approval only.
- **Writing the entry after the commit, with its sha.** That needs a second
  commit, or an amend, for every rule change, and splits the record from the
  change it records.
- **The path-safe name alone**, the first draft. The first hunt of this
  change showed `dev/a/b` and `dev--a--b` fold to one file, and merging both
  branches conflicts. The hash of the exact name keeps them apart.
- **Finding an entry's commit with `git log -S` on its heading**, also the
  first draft. It misses a later commit that extends the entry. The entry's
  commits come from `git log -L` over its lines. The second hunt showed the
  first range assumed one blank line between entries; it now ends at the
  entry's last non-blank line.
- **Appending a behavior the entry already lists**, the first fix. Two
  commits that made the same change wrote it twice, and the pull request no
  longer matched the entry and called it gone. Found by the second hunt. An
  extension adds only a behavior that is not there yet.
- **Joining behaviors with `; `**, the second fix. A sentence can hold
  `; `, so one behavior read as two. Found by the third hunt. Each behavior
  is its own `- new:` line.

**Where this stops applying.** A rename of the branch before the pull request
leaves its entries in the old file; the re-check finds those rules again and
marks them `not seen at commit time`. A rebase changes the shas a status line
cites; the heading and the re-check still match an entry. A run that does not
commit writes nothing, so an abandoned change leaves no entry behind.

## The rule check stays Grok-first, and stop and fix resumes it

**Decision.** The rule-check subagent runs on the `rule_check` role, whose
default list is Grok-first, the same as the finders': `grok-4.7-high-fast`,
then any Grok, then Sonnet. On *stop and fix*, the subagent that found the
break is resumed with the fix brief from `maintain-system-spec`'s
rule-check.md to write the code change; a fresh one on the `rule_check` slug
only if it cannot be resumed. The main agent keeps every step that asks the
user, the commit, and the chart.

**Why.** Deciding whether a rule governs a change is a judgment, but unlike
the refuter it runs on every reviewed commit in a repo with specs, not only
on proven bugs. That cost and speed are what set the find on Grok, for the
reasons in *Models by role, from settings*, and they apply here too. The
resume follows *Step 6 resumes the finder*: the agent that read the rule,
the diff and the break holds exactly the context a fix needs. The new run
after the fix is cold, as every new run is.

**Rejected.** A heavier model first for the rule check: the check runs on
every reviewed commit, which is the cost that set the finders on Grok.
Sharing the refuter's list: the refuter moved to Sonnet because it runs only
on proven bugs, and that reason does not carry over. A subagent for the
pause or the chart: the pause must ask and wait, and the chart entry must be
staged before the mint, which the main agent runs.

## Fixes from the fourth hunt of the rule check

A fourth hunt, over all three skills at once, found 29 gaps. The user chose
ten to fix before the first commit; these four are in this skill.

**The spec check reads from the root, and from the commit.** The check for
system specs ran `git ls-files` with plain pathspecs, so from a subfolder it
found none, and it read only the index, so staging the deletion of every
spec made the repo look like it had none. It now uses `:(top)` pathspecs
and also lists specs in `HEAD`, or in the parent of a commit that already
landed, so the hook's amend path sees them too. Rejected: only `HEAD`. A
new spec staged with the change would then be missed until its commit.

**A missing check holds the commit.** A rule check that failed, or had not
returned, did not block anything, because the gate waited only on paused
breaks. Now nothing is committed or minted until it returns its breaks or
`none`, and a check that fails twice is an open decision for the user.

**A later iteration stages its fixes before the re-check.** The check reads
`git diff --cached`. A fix left in the working tree was re-checked against
the old staged diff, then staged and committed unchecked.

**A skip is a decision too.** A Step 2a commit for *skip for now* now adds
no new chart entry, like *update the spec* and *keep the old behavior*. Its
restored rule text is the skip, not a new break.

## Known gaps after the fourth hunt

Found by that hunt, not shown by a failing test, and left by the user for a
later change:

- Stop and fix on a commit that already landed reads the rules at `HEAD`,
  the loosened rule, so the repair itself pauses. Read the rules at that
  commit's parent instead.
