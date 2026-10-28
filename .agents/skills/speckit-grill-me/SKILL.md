---
name: speckit-grill-me
description: Interview the user relentlessly about a spec-kit feature spec until reaching shared understanding, resolving each branch of the decision tree. Use when the user wants to stress-test a spec-kit spec, get grilled on their plan or data model, or mentions "grill me" in the context of a feature spec, requirements, or implementation plan.
---

Interview me relentlessly about every aspect of this plan until
we reach a shared understanding. Walk down each branch of the design
tree resolving dependencies between decisions one by one.

If a question can be answered by exploring the codebase, explore
the codebase instead.

For each question, provide your recommended answer.

---

## Spec-Kit Awareness

At the start, check what's in flight by looking for active specs:

```bash
ls specs/ 2>/dev/null
```

If a spec is active or named by the user, read its artifacts before grilling:

| File | What to look for |
|---|---|
| `specs/<name>/spec.md` | Requirements and scenarios to stress-test |
| `specs/<name>/plan.md` | Implementation decisions to challenge |
| `specs/<name>/data-model.md` | Data shape, relationships, edge cases |
| `specs/<name>/tasks.md` | Missing tasks, unclear steps |
| `specs/<name>/research.md` | Assumptions that haven't been validated |
| `specs/<name>/contracts/*.md` | API/data contracts — grill on edge cases |

Use these as the starting surface. Grill on what's missing, ambiguous, or not yet decided.

## After the Grilling

When understanding is shared, offer to capture decisions:

| What was resolved | Where to capture |
|---|---|
| New or changed requirement | `spec.md` |
| Implementation decision | `plan.md` |
| Data model change | `data-model.md` |
| New tasks discovered | `tasks.md` |
| Research finding | `research.md` |
| API shape decided | `contracts/<name>.md` |

Offer — don't auto-write. The user decides.

If no spec exists yet, offer: "Ready to turn this into a spec? I can scaffold one."
