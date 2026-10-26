# create-system-spec

Sets up system specs in a repo, once. A system spec lists the rules a change
in its area must not break, such as "every sign-in makes a new session ID".
Agents read the one short spec for the code they touch, instead of the whole
repo, and reviewers check changes against named rules.

The agent reads the code, proposes which concerns get a spec, and waits for
your approval. Then it writes the specs, a `SYSTEM_SPECS.md` index at the
repo root, and links to that index from `AGENTS.md` and other rule files. Old
`system_spec.md` and `*.system-spec.md` files are restructured into the new
format. It checks every new spec against the code before it hands over.
Nothing is committed.

After that, [`maintain-system-spec`](../maintain-system-spec/README.md) keeps
the specs current.

> Agent instructions: [SKILL.md](SKILL.md). Spec format:
> [format.md](../maintain-system-spec/format.md). Why it works this way:
> [DECISIONS.md](DECISIONS.md).

## One-time setup

Ask the agent: **"Install the create-system-spec and maintain-system-spec
skills"** — try it in this tab; open a new one only if it's not picked up.

**Install both.** This skill uses maintain-system-spec's format and runs it
to check its work. The skill manager does not install dependencies, so
installing only this one leaves it unable to run; it will say so.

If the agent doesn't know how, you haven't set up the skill manager yet — do
[Install](../../../README.md#install) in the repo root first.

## Using it

Check out `origin/main` with no changes to tracked files, then ask:

> Set up system specs for this repo

Untracked files are fine. If you have work in progress, run it from a
separate worktree instead and open it in your editor:

```bash
git fetch origin
git worktree add --detach ../<repo>-specs origin/main
```

**First it proposes.** You get a list of the specs it plans to write: the 3
to 5 riskiest concerns, plus every existing spec in the new format. For each
old spec it says where its rules go. Code with no spec yet is listed as
"Uncovered". Change anything you like, then approve.

**Then it writes and checks.** It drafts each spec from the code, writes
the files and the index, updates links, then runs maintain-system-spec once.
The report lists the specs, any rule the code already breaks (a probable
bug), and anything left for you.

**Afterwards, commit it.** Everything is left uncommitted. Create a branch
and open a pull request:

```bash
git switch -c docs/system-specs
```

## Troubleshooting

**Skill not found** — ask again in this tab first; if it's still not there, a
new agent tab or checking the skills installation is next.

**It says to install maintain-system-spec** — install it, then ask again.

**It said to use maintain-system-spec instead** — this repo already has a
`SYSTEM_SPECS.md` in the new format. Ask maintain-system-spec to add a spec
for the code you care about.

**It refused to run** — it needs `HEAD` at `origin/main` and no changes to
tracked files. With no work in progress, run `git switch main && git pull`.
Otherwise use a worktree, as in [Using it](#using-it).

**It left most of the repo "Uncovered"** — on purpose. A few checked specs
beat many unchecked ones. Ask maintain-system-spec to add specs for the
folders you care about next.
