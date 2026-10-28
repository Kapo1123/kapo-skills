---
name: openspec-summarize-archive
description: >-
  Generate a compact SUMMARY.md for one or more archived OpenSpec changes,
  distilling proposal, design, tasks, and delta specs into a single reference
  file. Use when the user wants to summarize archived OpenSpec changes, reduce
  archive file clutter, back-fill summaries for old archive entries, or make
  past OpenSpec work easier to look up.
---

# Summarize OpenSpec Archive

Generates a `SUMMARY.md` for archived OpenSpec changes. Each summary condenses
`proposal.md`, `design.md`, `tasks.md`, and delta specs into one compact
reference — so agents and developers can look up past work without loading 4+
files.

## When to use

- After archiving an OpenSpec change and wanting a quick-reference file alongside it
- In batch, to back-fill summaries for all existing archive entries that lack one
- When an agent needs to understand past work but loading all artifacts would be expensive

## Archive location

| Source | Path |
|--------|------|
| Archive | `openspec/changes/archive/YYYY-MM-DD-<name>/` |

This is OpenSpec's native archive path. If a repo has archive entries somewhere
else (an older layout, or a hand-rolled `archive/` directory), ask the user
where to look rather than guessing.

OpenSpec archive entries typically contain `proposal.md` / `design.md` /
`.openspec.yaml`. Skip any folder that clearly isn't an OpenSpec change — for
example one with `plan.md` / `contracts/` and no `proposal.md` — and report it
as skipped rather than summarizing it.

## Steps

1. **Select entries to summarize**

   List all archive entries that do NOT yet have a `SUMMARY.md`:

   ```bash
   ls openspec/changes/archive/ 2>/dev/null
   ```

   Filter to OpenSpec entries missing `SUMMARY.md`.

   If the user named a specific change, use it. Otherwise ask which they want
   (use a structured question tool if one is available):
   - A single entry
   - All unsummarized entries (batch)

2. **For each selected entry, read available artifacts**

   Read whichever of these exist (skip missing files silently):

   | File | Purpose |
   |------|---------|
   | `proposal.md` | What was built and why |
   | `design.md` | How it was built (technical decisions) |
   | `tasks.md` | Checklist of implementation steps |
   | `specs/*.md` | Delta specs (capabilities added/modified/removed) |
   | `.openspec.yaml` | Schema metadata and reviewers (if present); extract `reviewers` field if set |

3. **Generate `SUMMARY.md`**

   Write the file to the archive entry root using this template:

   ```markdown
   # <change-name>

   > Archived: YYYY-MM-DD · Schema: <schema-name> · Reviewers: <names from .openspec.yaml, or "—" if not set>

   ## What was built
   <!-- 2–4 sentences from proposal: problem, solution, scope -->

   ## Approach
   <!-- Key technical decisions from design.md. Bullet points. -->

   ## Implementation highlights
   <!-- Important files touched, extracted from task descriptions or design.md. -->

   ## Specs affected
   <!-- Capabilities added or modified from delta specs. Omit section if no delta specs. -->

   ## Key decisions & trade-offs
   <!-- Notable decisions, constraints, or rationale that future work should know. -->
   ```

   Rules for writing the summary:
   - **Be concise** — target 1 page (under 60 lines). Strip boilerplate.
   - **Preserve decisions** — capture the *why*, not just the *what*. This is what
     makes summaries useful months later.
   - **List files touched** in "Implementation highlights" — extracted from task
     descriptions or design.md.
   - **Skip empty sections** — omit a section rather than writing "None" or
     leaving it blank.

4. **Show completion**

   ```
   ## Summarize OpenSpec Archive Complete

   Generated SUMMARY.md for N entries:
   - openspec/changes/archive/2026-01-15-add-user-auth/SUMMARY.md
   - openspec/changes/archive/2026-01-20-add-dark-mode/SUMMARY.md

   Skipped M entries (already had SUMMARY.md):
   - ...
   ```

## Guardrails

- Never overwrite an existing `SUMMARY.md` without confirming with the user
- If an archive entry has no readable artifacts, note it as "empty — no
  artifacts to summarize" and skip
- Keep summaries under 60 lines — if tempted to write more, cut details ruthlessly
- Do not reproduce full task lists verbatim — summarize what was done, not every
  checkbox
- Only summarize; never modify the original artifacts in an archive entry
