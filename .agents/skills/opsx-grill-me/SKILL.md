---
name: opsx-grill-me
description: >-
  Interview the user relentlessly about an OpenSpec proposal or design until
  reaching shared understanding, resolving each branch of the decision tree. Use
  when the user wants to stress-test an OpenSpec change, pressure-test a plan
  before implementing, get grilled on their design, or says "grill me" in the
  context of a proposal, spec, or feature plan.
---

# Grill Me

Interview me relentlessly about every aspect of this plan until we reach a
shared understanding. Walk down each branch of the design tree resolving
dependencies between decisions one by one.

If a question can be answered by exploring the codebase, explore the codebase
instead.

For each question, provide your recommended answer.

---

## OpenSpec awareness

At the start, check what's in flight:

```bash
openspec list --json
```

If a change is active or named by the user, read its artifacts before grilling:

- `openspec/changes/<name>/proposal.md` — what & why
- `openspec/changes/<name>/design.md` — how
- `openspec/changes/<name>/tasks.md` — implementation steps

Use these as the starting surface. Grill on what's missing, ambiguous, or not
yet decided.

If the `openspec` CLI isn't available or the repo doesn't use OpenSpec, don't
stop — grill against whatever plan the user has described in conversation.

## How to grill

- **One thread at a time.** Resolve a decision before opening the next, so
  dependent choices are made in the right order.
- **Follow dependencies.** When an answer invalidates a later assumption, say
  so and revisit it rather than plowing ahead.
- **Always recommend.** Never ask a bare open question — state the option you'd
  pick and why, so the user can react instead of composing an answer from
  scratch.
- **Prefer evidence over opinion.** Read the code before asking about how
  something currently works.
- **Push on the uncomfortable parts.** Edge cases, failure modes, migration and
  rollback, who owns the data, what happens at 100x volume.

## After the grilling

When understanding is shared, offer to capture decisions:

| What was resolved | Where to capture |
|---|---|
| Scope change | `proposal.md` |
| Architecture decision | `design.md` |
| New tasks discovered | `tasks.md` |

Offer — don't auto-write. The user decides.

If no change exists yet, offer: "Ready to turn this into a proposal?" and hand
off to the OpenSpec propose step.
