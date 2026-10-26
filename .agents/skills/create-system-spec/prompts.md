# Survey prompt

The prompt `create-system-spec` gives each survey sub-agent in
[Step 3](SKILL.md#step-3--survey-the-code), and what it must return. Drafting
uses the [draft prompt](../maintain-system-spec/records.md#draft-prompt) in
`maintain-system-spec`, so both skills draft specs the same way.

Fill in the angle-bracket fields. Pass files by absolute path; do not paste
their text.

```text
Survey one source area of <owner/repo> for the create-system-spec skill, then stop.
Read only. Do not edit or create any file, run tests or builds, run a command that writes, commit, or start another agent.

Repository: <absolute path>
Commit: <full HEAD commit>
Area: <name>
Paths: <directories or globs in this area>
Existing specs and rule files that mention this area: <absolute paths, or "none">
OpenSpec specs that mention this area: <absolute paths, or "none">

The goal is to find the rules a change in this area must not break, so a later step can group them into system specs. Existing specs are claims to check, not facts.

Do this:
1. List the files with git ls-files for each path. Read them completely, the most central files first. Skip generated files.
2. Work out what the area does: its parts, how a request or event moves through them, and what it calls outside the area.
3. Find rules a change must not break: ordering, checks that must run, values that must never be sent or logged, contracts other code or repos rely on, what happens on failure. Each needs a file:line. A rule you cannot cite, mark (inferred).
4. Compare with the existing specs. Note where a spec says something the code does not do, and rules the code keeps that no spec states.
5. Do not copy function signatures, class lists, or config into your answer.

Return exactly these sections, as plain lines. No tables.
Components: the main parts, one line each, with the file that holds it
Flow: how a request or event moves through the area, in a few lines
Files read: files read completely out of files in the area; each file read partly or not at all
Boundaries: where the area is entered, and what it calls outside itself, each with file:line
Non-obvious rules seen: one line each: <rule>. <file:line or (inferred)>. <which concern it belongs to, in a word or two>
Spec mismatches: one line each: <spec path>:<line> says <claim>; the code <does what>, at <file:line>
Open questions: what only a person can answer, such as whether a behavior is intended
```
