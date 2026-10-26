# Decisions

Why system specs exist, and why the format is the way it is, is in
[maintain-system-spec's DECISIONS.md](../maintain-system-spec/DECISIONS.md).
This file covers only what is specific to setting them up.

Some entries name `weekly-security-check`. That skill is not in this
repository; it lives in the team skills repo this copy came from.

## It runs once per repo

Running create again would re-split the repo and hand out new ID prefixes,
which breaks every link and rule citation made since the first run. So the
format marker in `SYSTEM_SPECS.md` stops it. Everything after the first run,
including specs for code that has none, goes through `maintain-system-spec`,
which adds to the existing split instead of replacing it.

A `SYSTEM_SPECS.md` without the marker is someone's own list, not this
format, so create treats it like any other old list and replaces it.

## It needs maintain-system-spec installed

The format lives in one file, `maintain-system-spec/format.md`, so the two
skills cannot drift apart. Create also reuses maintain's draft prompt and
runs maintain to prove its result. The skill manager has no way for a skill
to declare that it needs another one: `install` links only the skill it is
given. So create checks that the format file can be read and stops if it
cannot, and both READMEs say to install maintain alongside it.

## It runs only at origin/main with no tracked changes

Every rule cites a `file:line`, and the master records the commit the specs
were verified at. Specs written from a branch would cite lines that may never
reach `main`, and the recorded commit might not exist in other clones. Untracked
files do not block it, because it reads only tracked files. This is the same
check as `weekly-security-check`, for the same reasons.

## Interview the repo, not the person

The person knows intent; the code knows behavior. Asking what the code can
answer wastes their time and gets answers from memory, which is how the old
specs went wrong. Questions are kept to what the code cannot show, such as
whether a behavior is intended.

## Survey before splitting

A split decided from folder names gives layer specs, which is what the old
`service/` and `model/` specs were. The survey reads the code first and
reports rules with the concern each belongs to, so the split groups rules
that break together. Each area is small enough for one sub-agent to read in
full, the same size cap as a spec. The survey also compares the code with
old specs, so the proposal can say which old rules no longer hold.

## The person approves the split before any drafting

The split decides every rule's home and every ID prefix. Changing it after
specs are drafted and linked means renumbering, which is what IDs exist to
prevent. It is also the one place the person's judgement matters most: which
concerns are risky and which behaviors are intended.

## Start with the riskiest few

Every one of the 23 existing specs was incomplete, and none was reliably
current. A large set written at once is a large set nobody verifies. So the
first run writes specs for the 3 to 5 concerns where a broken rule does the
most harm, plus the old specs restructured, and lists the rest as
`Uncovered`. That list keeps the gaps visible, and `maintain-system-spec`
proposes specs for them as their code changes.

## Old specs are restructured, not kept beside the new ones

Two formats in one repo means two places to look and two lists to keep, and
every hand-kept list was already incomplete. So each old spec is renamed,
merged, split, or retired in this same change. Its content is checked against
the code like a new draft, because the old specs were not reliably current.

Restructuring drops signatures, inventories, history, and plans by design.
Real rules are never dropped silently. The draft prompt makes each sub-agent
account for every statement in the old spec, and any real rule left without
a home is shown to the person.

## Links are updated in the same change

Old paths in `AGENTS.md`, rule files, constitutions, code comments, and docs
break the moment the old specs are renamed. Old position references, such as
"invariants 1–2", point at nothing once rules have IDs. Leaving them for later
means agents follow dead links in the meantime. Rule files keep their own
wording of the obligation, and only their lists are replaced by a link to the
master, so no rule file holds a list that can go stale again.

Code comments are the one product-code edit allowed, because they hold those
references. Only the comment text changes.

## Sub-agents draft; the main agent writes

Drafting reads a lot of code per spec, so each spec gets its own sub-agent,
in parallel. Only the main agent writes, so it can see every draft at once
and catch a rule claimed by two specs or an old rule claimed by none. Drafts
come back as text for the same reason. The sub-agent type follows the same
table as `weekly-security-check` and `maintain-system-spec`.

## No staging, no commit

`git mv` stages the rename, and staging is the first half of a commit the
person did not ask for. So old specs are moved or deleted with plain file
commands, and the person stages and commits through a pull request. The
whole set is one reviewable change.

## Prove it before handing over

A spec nobody has checked against the code is a draft. Drafting sub-agents
make mistakes, and the main agent cannot re-read every cited line. So create
runs `maintain-system-spec` once over every new spec before it reports. That
also records each spec's first Last verified commit, so the first later run
has a base to diff from.

## OpenSpec specs are input, not a source of rules

OpenSpec records proposed and archived changes. The survey reads
`openspec/specs/` for hints about intent, but a rule enters a system spec
only with a citation in the current code. Later, when an OpenSpec change is
archived, `maintain-system-spec` moves its lasting rules into the system
spec that covers the code.
