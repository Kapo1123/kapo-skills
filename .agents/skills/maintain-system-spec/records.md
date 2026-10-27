# Sub-agent prompts

The prompts `maintain-system-spec` gives its sub-agents, and what each must
return. [SKILL.md](SKILL.md) says when each runs. The spec and master formats
are in [format.md](format.md). `create-system-spec` uses the
[draft prompt](#draft-prompt) too.

Fill in the angle-bracket fields. Where a field offers a quoted value, use it
as written. Pass files by absolute path; do not paste their text.

## Check prompt

One sub-agent per due spec.

```text
Check one system spec in <owner/repo> against the code, for the maintain-system-spec skill, then stop.
Read only. Do not edit any file, run tests or builds, run a command that writes, commit, or start another agent.

Repository: <absolute path>
Commit: <full HEAD commit>
Mode: <"on demand" or "branch">
Spec: <absolute path to the spec file>
Format: <absolute path to maintain-system-spec/format.md>
Scope files: <"for each Scope glob in the spec, set GLOB to it and run git ls-files -- \":(glob)$GLOB\"">
Rules to check: <"all", or "only the rules marked Scope: repo-wide">
Changed files in scope: <from git diff -M --name-status, or "first check, read all">
Other changed files: <changed files outside this spec's scope, or "none">
Linked specs: <absolute paths of the specs in its Links section, or "none">

The spec is a set of claims to check, not facts. A spec goes stale, and a rule marked (inferred) is only a claim.

Do this:
1. Read the format file, then the spec.
2. Read files. On demand: read every scope file completely, changed files first. Branch: read every changed file in scope completely, plus each file a rule cites. Do not skim, and do not read partial line ranges. You may follow calls out of scope, read-only.
3. In "Other changed files", read any file that calls into this scope or touches what a rule protects. A rule can be broken by a file outside the spec's scope.
4. For each rule to check, find the code that keeps it or breaks it. A rule marked Scope: repo-wide: on demand, search the whole repo (git grep); in branch mode, search the changed files.
5. Give one verdict per rule:
   - holds: the code keeps the rule.
   - code breaks it: the rule is still what the code should do, and the code does not do it.
   - spec is stale: the code changed on purpose and the rule no longer describes what it should do, or the rule cites lines that moved.
   - can't verify: the evidence is in another repo, at runtime, or not readable.
   When unsure between "code breaks it" and "spec is stale", say "code breaks it" and explain. Never suggest rewriting a rule to match code that breaks it.
6. For "spec is stale", say whether your suggested edit makes the rule stricter, looser, or only changes wording. Looser means it allows more, checks less, widens a contract, or removes the rule.
7. For a rule marked (inferred) that holds, give the file:line that shows it. For a rule with an Open change line, give the verdict as usual; the line says the code and the rule disagree, and your verdict says whether they still do.
8. Note behavior in scope that other code relies on and the spec does not state. Give file:line.
9. Note files outside Scope that keep or break a rule here, and Scope globs that match no file.
10. Note unenforced rules that a test, a type, or a lint rule could enforce, and how.
11. Note anything in the spec the format forbids: function signatures, class or endpoint lists, config copies, generic principles, ticket or PR history, TEMPORARY notes, status tables, future plans, Version or Last updated headers, rules cited by position or range, rules without an Enforced by or Evidence line. An Open change line in the form the format gives is allowed; note only one that is malformed or a second one from the same branch on the same rule.

Return exactly these sections, as plain lines. No tables.
Coverage: full or partial. Full means every file step 2 names was read completely and every repo-wide search ran. Give files read completely out of files to read, and list each file read partly or not at all.
Rules: one line each, in this form:
  <ID> <holds | code breaks it | spec is stale | can't verify> at <file:line>. Evidence: <cited line | reasoning only>. <one sentence>. Edit: <stricter | looser | wording>: <suggested text>, or Edit: none.
Inferred: one line each: <ID> confirmed at <file:line> | <ID> not shown, and why
Missing rules: one line each: <proposed rule> at <file:line>
Scope: files to add, each with the rule it keeps or breaks; globs that match nothing; or none
Encodable: one line each: <ID> <test | type | lint>: <how>
Format: one line each: <spec line or section>: <what the format forbids>
```

## Draft prompt

One sub-agent per new or restructured spec, after the person approves it.

```text
Draft one system spec for <owner/repo>, for the <create-system-spec | maintain-system-spec> skill, then stop.
Read only. Do not edit or create any file, run tests or builds, run a command that writes, commit, or start another agent. Return the draft as text.

Repository: <absolute path>
Commit: <full HEAD commit>
Format: <absolute path to maintain-system-spec/format.md>
Spec path: <repo-relative path the spec will be written to>
Concern: <name and one-line purpose, from the approved split>
ID prefix: <PREFIX>
Scope globs: <from the approved split>
Old specs to restructure: <absolute paths, or "none">
Rules that belong here from other old specs: <old spec path and the rule text or heading, or "none">
Rules that live in other specs: <spec path and rule IDs this one should link to, not restate, or "none">
Rules from archived OpenSpec changes to carry: <paths, or "none">
Highest number already used with this prefix: <number, or "none">

Do this:
1. Read the format file. Follow it exactly.
2. Read every file the Scope globs match, completely. Run git ls-files ':(glob)<glob>' to list them.
3. Read each old spec. Treat every statement in it as a claim to check against the code.
4. Write rules only from the code. Each rule cites the file:line that shows it holds. A rule you cannot cite is marked Evidence: (inferred).
5. For Enforced by, look for a test that fails when the rule breaks. Cite it only if you read it and it asserts the rule. Otherwise write unenforced.
6. Keep to the size cap: about 300 lines and 20 rules. If the concern needs more, return the draft for the most important rules and list the rest under Overflow.
7. Number new rules from one above the highest number already used.
8. Do not restate a rule that lives in another spec. Link it by ID.

Return exactly these sections:
Draft: the full spec text, in a fenced markdown block.
Carried: one line per statement in an old spec: <old spec>:<line> -> <new ID> | merged into <ID> | not a rule (signature, list, history, principle, plan) | dropped, and why | belongs in <other concern>
Inferred: IDs marked (inferred), and what would show them
Code that breaks an old rule: one line each: <old spec>:<line> rule, <file:line> where the code does not do it
Overflow: rules that did not fit, or none
Open questions: what only a person can answer, such as whether a behavior is intended
```
