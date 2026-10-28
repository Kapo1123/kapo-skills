# OpenSpec summarize-archive skill — setup and usage

Writes a one-page `SUMMARY.md` into archived OpenSpec changes, so you (or an
agent) can find out what a past change did without opening `proposal.md`,
`design.md`, `tasks.md`, and the delta specs one by one.

> Looking for the agent-facing instructions? Those live in [SKILL.md](SKILL.md).
> This file is for humans.

---

## One-time setup

### 1. Install the skill

Ask the agent: **"Install the openspec summarize-archive skill"** — try it in
this tab; open a new one only if it's not picked up.

If the agent doesn't know how, you haven't set up the skill manager yet — do
[Install](../../../README.md#install) in the repo root first.

### 2. Have the OpenSpec CLI available (optional)

The skill reads files directly, so it works without the CLI. It's only needed if
you also want the agent to list or archive changes for you:

```bash
npm install -g openspec   # or however you install it in your repo
openspec list --json      # confirm it works
```

---

## Using it

From a repo with an OpenSpec archive, ask:

> Summarize the OpenSpec archive

Other phrasings that trigger it: "back-fill summaries for archived changes",
"summarize archived OpenSpec changes", "the archive has too many files to read".

You can also point it at one entry:

> Summarize the 2026-01-15-add-user-auth archive entry

### What it actually does

1. Lists entries in `openspec/changes/archive/` and finds the ones with no
   `SUMMARY.md` yet
2. Asks whether you want one entry or all of the unsummarized ones
3. Reads whichever artifacts exist in each entry — proposal, design, tasks,
   delta specs, and `.openspec.yaml` (for reviewer names)
4. Writes a `SUMMARY.md` into the archive entry with what was built, the
   approach, implementation highlights, specs affected, and key decisions
5. Reports which entries it summarized and which it skipped

### What you get back

A `SUMMARY.md` per archive entry, under 60 lines, weighted toward *why*
decisions were made rather than restating every task checkbox.

---

## Things worth knowing

**It never overwrites an existing summary silently.** If an entry already has a
`SUMMARY.md`, the skill skips it and tells you, rather than regenerating it. Ask
explicitly if you want one rebuilt.

**It only reads the archive; it never edits the original artifacts.** The
proposal, design, and tasks files in an archive entry are left untouched.

**Non-OpenSpec folders get skipped.** If your archive contains entries from a
different spec tool (say, something with `plan.md` and `contracts/` but no
`proposal.md`), the skill reports them as skipped instead of trying to summarize
them.

**Batch runs can be long.** Summarizing a large archive means reading several
files per entry. If you have dozens of unsummarized entries, consider doing them
in a few passes.

---

## Troubleshooting

**"No archive entries found"** — check that `openspec/changes/archive/` exists
and has entries. If your repo keeps archives somewhere else, tell the agent the
path.

**Summaries feel too shallow** — that's the design (one page, decisions over
detail). If a specific entry deserves more, ask the agent to expand that one
section rather than raising the limit globally.

**The agent doesn't seem to know about the skill** — ask it directly in this
tab first; it may already be there. If it's still missing, open a new agent
tab, then ask the agent to "check my skills installation".
