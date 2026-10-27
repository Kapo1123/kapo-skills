# System spec format

The one format for system specs in every repo. `create-system-spec` writes
it, and `maintain-system-spec` checks and keeps it. Why each rule is the way
it is: [DECISIONS.md](DECISIONS.md).

A system spec records the rules a change must not break. It does not
describe the code. Code shows what the system does; the spec says what must
stay true.

## File names

- **Specs:** `<concern>.system-spec.md`, with a kebab-case concern name such
  as `session.system-spec.md` or `rate-limit.system-spec.md`. Put it in the
  folder that holds most of that concern's code. Several specs may share a
  folder.
- **Master index:** `SYSTEM_SPECS.md` at the repo root. It is the only list
  of specs. `AGENTS.md` and other rule files link to it instead of keeping
  their own list. See [Links from rule files](#links-from-rule-files).
- **Old names:** `system_spec.md` and specs written before this format are
  renamed and restructured by `create-system-spec`.

## Split rules

1. **Split by concern, not by layer or folder.** A concern is a set of rules
   that can be broken together: session, billing, request signing, rate
   limiting. A spec for `service/` or `model/` is a layer, not a concern.
2. **Size cap.** About 300 lines and 20 rules per spec, covering at most
   about 50 files or 8k lines of code. Past that, split by sub-concern.
   Count code with `git ls-files ':(glob)<glob>' | xargs wc -l`. A spec
   whose rules are all repo-wide has no file cap.
3. **Each rule has one home.** A cross-cutting rule, such as error
   presentation or request signing, gets its own spec. Other specs link to
   it by rule ID. They do not restate it.
4. **Repo-wide rules say so.** Mark them `Scope: repo-wide`. They are
   checked with a search of the whole repo, not only the spec's globs.
5. **No spec where there are no rules.** The master lists larger source
   folders with no spec under `Uncovered`, so gaps stay visible.
6. **Names** as in [File names](#file-names).

## Spec template

```markdown
# Session

When the session ID is made, rotated, and sent. Prefix: `SESSION`.

## Scope

- `src/session/**`
- `src/api/client.ts`

## Rules

- **SESSION-01.** Every sign-in makes a new session ID.
  - Reason: the server keys each user's recent activity to the session, so a reused ID shows one account's activity to the next.
  - Enforced by: `test/session/session.test.ts:42`
  - Evidence: `src/session/session-service.ts:88`
- **SESSION-02.** A request without a session ID is never sent.
  - Enforced by: unenforced
  - Evidence: `src/api/client.ts:120`

Retired: SESSION-04

## Contracts

- **SESSION-03.** The `Session-Id` header is a UUID v4 string. The server rejects anything else with 400.
  - Enforced by: `src/session/session-service.ts:52`
  - Evidence: `src/session/session-service.ts:52`

## Failure behavior

- **SESSION-05.** If rotation fails, the old ID is kept and the next request retries rotation. The user is not signed out.
  - Enforced by: unenforced
  - Evidence: (inferred)

## Security and privacy

- **SESSION-06.** The session ID is never written to a log.
  - Scope: repo-wide
  - Enforced by: unenforced
  - Evidence: `src/util/logger.ts:31`

## Links

- [auth](../auth/auth.system-spec.md): `AUTH-02` decides when sign-in finishes, which triggers `SESSION-01`.
```

### Sections

Every spec has these sections, in this order. Leave a section out only when
it has nothing in it.

| Section | Holds |
|---------|-------|
| Scope | Globs this spec covers, one per line |
| Rules | What must stay true inside the scope |
| Contracts | APIs, events, and data shapes that other code or repos rely on |
| Failure behavior | What happens when a dependency fails or input is bad |
| Security and privacy | Who can reach the code, and what must never be logged or exposed |
| Links | Specs this one depends on, each with the rule IDs that matter |

The first line under the title says what the spec is about, in one
sentence, and names its ID prefix.

**Scope globs** are relative to the repo root and read as git `:(glob)`
pathspecs, so `**` works and `git ls-files ':(glob)<glob>'` lists what a
spec covers. A spec whose rules all apply everywhere puts `Scope: repo-wide`
in this section, then lists the globs of its home code.

### Rule entries

Every entry under Rules, Contracts, Failure behavior, and Security and
privacy is a rule, with the same fields:

- **ID.** `<PREFIX>-<NN>`, such as `SESSION-03`. The prefix is set once per
  spec. An ID is never renumbered and never reused. IDs are unique across the
  repo. A new rule takes the next number above the highest one used with that
  prefix anywhere in the repo, `Retired` lines included.
- **The rule.** One or two sentences: what must stay true.
- **Reason:** one line, only when the rule is not obvious.
- **Scope: repo-wide:** only when the rule applies outside the spec's globs.
- **Enforced by:** what fails when the rule is broken. One of: a test
  (`path:line`), a type, a lint rule, a runtime check (`path:line`), or
  `unenforced`.
- **Evidence:** the `file:line` that shows the rule holds today. A rule with
  no citation has `Evidence: (inferred)`. An inferred rule is a claim to
  check, never a rule. Reviewers and other skills do not hold a change to it.

### Open changes

A rule can carry one more field, last:

```markdown
- **SESSION-02.** A request without a session ID is never sent.
  - Enforced by: unenforced
  - Evidence: `src/api/client.ts:120`
  - Open change: dev/someone/guest-requests, 2026-10-26 — guest requests are sent without a session ID
```

- **Form:** `Open change: <branch>, <YYYY-MM-DD> — <the new behavior, one
  sentence>`. The branch is the one whose pull request left the rule open.
  One per branch: a rule two pull requests skipped carries two lines, oldest
  first. A second skip on the same branch replaces that branch's line, so it
  names the newest behavior.
- **What it says:** the code and this rule disagree, and the person has not
  decided which gives way. The rule above it is unchanged and still the
  rule. It is not a rule edit, and it is not approval.
- **Who writes it:** a pull-request workflow skill, when one is installed
  and the person answers *skip for now* for that rule. None is included in
  this repository; without one, the person adds it in a hand run of
  `maintain-system-spec`, and only when they choose to record a skip. It is
  committed on that branch, so it survives the merge.
- **Who clears it:** updating the rule removes its lines in the same edit.
  When the code is changed back instead, an on-demand `maintain-system-spec`
  run removes them once a check with full coverage finds the whole rule
  holds. A branch-mode check, or one with partial coverage, reads only part
  of the code, so its `holds` leaves them. A fix commit leaves them too,
  because the code that broke the rule may reach beyond that fix.
- **The chart records the same skip, as history.** The chart entry says
  when the rule was skipped and why; this line says, next to the rule, that
  it is still open. This skill reads the line, not the chart.
- **It is the one note about pending work a spec may carry.** The ban on
  `TEMPORARY` notes and plans below is about text that describes what is not
  true yet. An open change describes what is true now: the code does not keep
  the rule. `maintain-system-spec` lists every one at the top of each report
  until none remain.

**Retired:** when a rule is removed, its ID goes on the `Retired:` line at the
end of its section, so no one reuses it. Only the ID: no reason, no date.

**A rule that moves** to another spec keeps its ID. The prefix says where the
rule was first written, not where it lives now.

**Cite rules by ID**, such as `AUTH-02`, with a link to its spec. Never by position
("invariants 1–2") and never by range ("`AUTH-01`..`AUTH-05`"). Positions and
ranges break when rules are added or retired.

**Prefer encoding over prose.** A rule that a test, a type, or a lint rule
enforces cannot quietly go stale. When a rule could be encoded, maintain
suggests how. `unenforced` rules are where maintain spends its effort.

## What not to record

| Do not record | Why |
|---------------|-----|
| Function signatures, class or endpoint lists, config copies | They are already in the code and go stale the day it changes |
| Generic principles ("Fail Secure", "Single Responsibility") | They are not checkable against this code |
| Ticket, PR, or change history | Git has it |
| `TEMPORARY` notes, status tables, future plans | They describe what is not true yet. An `Open change:` line is not one of these; see [Open changes](#open-changes) |
| `Version` or `Last updated` headers | They drift from git; the master records the last verified commit |

An endpoint belongs in Contracts only as a rule others rely on, such as "returns
409 when the same request is already running", never as an entry in a list.

## Master index

`SYSTEM_SPECS.md` at the repo root:

```markdown
# System specs

<!-- system-specs format: 1 -->

Kept by the create-system-spec and maintain-system-spec skills. Each spec
lists the rules a change in its scope must not break. Before changing code,
read the spec that covers it. Change a spec in the same pull request as the
behavior change.

| Spec | Covers | Purpose | Links | Last verified | Last check |
|------|--------|---------|-------|---------------|------------|
| [session](src/session/session.system-spec.md) | `src/session/**`, `src/api/client.ts`, repo-wide | When the session ID is made, rotated, and sent | auth | `a1b2c3d` 2026-10-12 | full |
| [billing](src/billing/billing.system-spec.md) | `src/billing/**`, `src/pages/invoices/**` | Invoice totals and the charge sent to the payment provider | session, payments | never | — |

## Uncovered

Larger source folders with no spec.

- `src/pages/demo/`
- `src/widgets/reports/`
```

- **Format marker.** The line `<!-- system-specs format: 1 -->` tells the
  skills this repo uses this format. `create-system-spec` refuses to run when
  it is present.
- **Spec:** a link to the spec file, named by its concern.
- **Covers:** the spec's Scope globs. Add `repo-wide` when any rule in the
  spec is repo-wide.
- **Purpose:** one line.
- **Links:** the concern names of the specs in its Links section.
- **Last verified:** short commit (7 or more characters) and date of the last
  check that read the whole scope and found no rule broken, on the default
  branch. `never` until then.
- **Last check:** `full` or `partial`, for the most recent check on the
  default branch. `—` before the first one.
- **Uncovered:** larger source folders with no spec. A folder leaves the list
  when a spec covers it.

## The rule-change chart

`system-spec-changes/` at the repo root, beside `SYSTEM_SPECS.md`, holds a
committed log of rule changes: one Markdown file per branch, named after the
branch with each `/` turned into `--` and any other character outside
`A-Z a-z 0-9 . _ -` turned into `-`, then `-` and the first 8 characters of
the branch name's git hash, so two branches never share a file
([rule-check.md](rule-check.md#the-rule-change-chart) has the command).
`bug-hunter` adds an entry, in the same
commit as the code, for each rule change it lets through. A pull-request
workflow skill, when installed, writes each decision into it at the pull
request; without one, entries stay undecided until the person settles them
in a hand run. Entries are never removed.
The entry format and lifecycle are in
[rule-check.md](rule-check.md#the-rule-change-chart).

The chart is not a spec. Nothing under it is a rule, nothing reads it as
approval, and edits to it are never a spec edit. This skill may read it for
context, such as when and why a rule changed, and never edits it.

## Links from rule files

Each rule file points to `SYSTEM_SPECS.md` and does not keep its own list.
This covers `AGENTS.md`, `CLAUDE.md`, `.cursorrules`,
`.github/copilot-instructions.md`, `.cursor/rules/*.mdc`, and constitutions
such as `.specify/memory/*.md`. Keep the rule file's own wording of the
obligation, and replace its list with a link:

```markdown
## System specs

[SYSTEM_SPECS.md](SYSTEM_SPECS.md) lists every system spec and what it covers.
Before changing code, read the spec that covers it. Do not break a rule in it
unless the person asks for the behavior change. Then change the spec in the
same pull request.
```

A code comment or doc that points at a spec links the spec file and names
rule IDs, never positions.

## System specs and OpenSpec

A system spec holds the rules the current code must keep. OpenSpec holds
changes: proposed ones in `openspec/changes/`, archived ones under
`openspec/changes/archive/`, and their merged requirements in
`openspec/specs/`. When an OpenSpec change is archived, its lasting
rules move into the system spec that covers that code. `maintain-system-spec`
does this when asked. The OpenSpec files stay as they are, as the record of
the change.
