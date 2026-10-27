# maintain-system-spec

Keeps a repo's system specs true. A system spec lists the rules a change in
its area must not break. Agents and reviewers read it instead of the whole
repo, so a stale one misleads all of them. This skill checks each spec
against the code, fixes the spec where the code changed on purpose, and
reports code that breaks a rule as a probable bug. It never edits product
code and never commits.

It works in any repo set up by
[`create-system-spec`](../create-system-spec/README.md): one
`SYSTEM_SPECS.md` index at the root, and `<concern>.system-spec.md` files
next to the code.

> Agent instructions: [SKILL.md](SKILL.md). Spec format:
> [format.md](format.md). Sub-agent prompts: [records.md](records.md). The
> system-spec rule check other skills run: [rule-check.md](rule-check.md). Why
> it works this way: [DECISIONS.md](DECISIONS.md).

## One-time setup

Ask the agent: **"Install the maintain-system-spec skill"** — try it in this
tab; open a new one only if it's not picked up.

If the agent doesn't know how, you haven't set up the skill manager yet — do
[Install](../../../README.md#install) in the repo root first.

`create-system-spec` needs this skill installed, and `bug-hunter` needs it
for its system-spec rule check. The skill manager does not install
dependencies for you, so install this one alongside them.

## Using it

Ask for a check:

> Check the system specs
> Check the session and billing system specs
> Check every system spec

With no names, it checks the specs that are due: code in their scope changed
since they were last verified, or they were last verified 4 or more weeks ago,
or their last check was partial.

For a check that moves the "last verified" commit in `SYSTEM_SPECS.md`, run it
on `main` at `origin/main`. On another branch it still checks and edits
specs, but leaves that column alone.

**Every pull request (optional).** A pull-request workflow skill can run this
skill in branch mode on the specs your branch touches, and stop to ask you if
it changes a spec or finds a broken rule. No such workflow skill is included
in this repository; without one, ask for a check before you open the PR.

**Every commit, the rule check.** `bug-hunter` (and a pull-request workflow
skill, if you add one) runs a lighter check from this skill,
[rule-check.md](rule-check.md): which rules a change breaks, and whether a
committed change doc approved that. `bug-hunter` records what it let through
in a rule-change chart, a committed log under `system-spec-changes/` with one
file per branch. A workflow skill would ask you about each rule once at the
pull request and write your decision into it. None is included here, so you
settle rule changes by running this skill yourself; until then the entries
stay undecided. Entries are never removed, so the log shows when and why
each rule changed.

**Other things to ask for:**

> Add a system spec for `src/pages/invoices/`
> Split the notifications system spec
> Move the rules from the archived `add-csv-export` OpenSpec change into the system specs
> Confirm the looser `BILLING-04`, it was intended

## Reading the report

**Open changes come right after the first word.** When a rule was left
open — you answered *skip for now* and recorded the skip, at the pull
request through a workflow skill or in a hand run — its spec carries an
`Open change:` line under that rule. Every run lists those before
anything else. When you
ask for a check, it then asks you to settle each one: update the rule, or
change the code back. Until you do, it asks again on every run.

The report starts with one word:

- **clean** — every spec checked matches the code. Nothing to do.
- **changed** — it edited specs. They are uncommitted. Review and commit them.
- **blocked** — something needs you: a rule the code breaks, or a looser rule
  waiting for your OK.

Then come, when they apply:

- **Code breaks a rule** — a probable bug, with the rule ID and `file:line`.
  The spec is left as it is. Fix the code, or tell the agent the rule should
  change.
- **Held for confirmation** — the code now allows more than the rule says.
  That might be a regression, so it is not written until you confirm.
- **Proposals** — new specs for uncovered code, splits for oversized specs,
  and tests or types that could enforce a rule. Nothing here is done until
  you approve.

## Troubleshooting

**Skill not found** — ask again in this tab first; if it's still not there, a
new agent tab or checking the skills installation is next.

**"No system specs" or it suggested create-system-spec** — the repo has no
`SYSTEM_SPECS.md` with the format marker. Run `create-system-spec` once.

**"Last verified" did not move** — it moves only on `main` at `origin/main`,
when the whole scope was read, and when no rule is broken or held. Pull
`main`, resolve what the report lists, and check again.

**It reported a bug instead of fixing the spec** — on purpose. A spec rewritten
to match broken code turns the bug into a rule. If the code is right, say so
and the agent changes the rule.

**It checked nothing in my pull request** — no changed file matched a spec's
scope, so it returned "skipped: no specs touched". That is expected.

**It keeps asking about an open change** — a rule still has an `Open change:`
line. Answer *update the rule*, or change the code back; once an on-demand
run reads the whole scope and finds the rule holds, it removes the line. A
pull-request workflow skill adds these lines when installed; without one,
one is added only when you record a skip in a hand run.
