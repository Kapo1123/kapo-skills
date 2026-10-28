---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
disable-model-invocation: true
---

# Grill Me

Interview me relentlessly about every aspect of this plan until
we reach a shared understanding. Walk down each branch of the design
tree resolving dependencies between decisions one by one.

If a question can be answered by exploring the codebase, explore
the codebase instead.

For each question, provide your recommended answer.

## How to run the interview

- Ask one focused question at a time, or a tight cluster of tightly
  related questions. Do not dump a long list at once.
- Before asking, resolve anything you can yourself by exploring the
  codebase (read files, search, trace dependencies). Only ask the user
  what genuinely requires their judgment, preference, or external context.
- Treat the design as a tree. Start at the root decision, then walk into
  each branch it unlocks. Fully resolve a branch's dependencies before
  moving to the next.
- For every question, state your recommended answer and a one-line
  rationale, so the user can simply confirm or redirect.
- Surface trade-offs, hidden assumptions, edge cases, failure modes, and
  decisions the user has not yet considered.
- Keep going until every open branch is resolved and you and the user
  share the same mental model. Then summarize the agreed design.

## When to use

Use when the user wants to stress-test a plan, pressure-test a design,
or explicitly says "grill me".
