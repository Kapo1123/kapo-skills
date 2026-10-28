# Grill-me skill — setup and usage

Turns the agent into a relentless interviewer that pressure-tests a plan before
you build it. It walks the decision tree one branch at a time, recommends an
answer for every question it asks, and reads the codebase instead of asking you
things it could find out itself.

Useful when a proposal *looks* finished but you suspect it hasn't been thought
all the way through.

> Looking for the agent-facing instructions? Those live in [SKILL.md](SKILL.md).
> This file is for humans.

---

## Why it's called `opsx-grill-me`

`opsx` is OpenSpec's own command namespace — `opsx:propose`, `opsx:apply`,
`opsx:archive`, and so on, though the exact slash-command spelling varies by
tool. This skill isn't part of OpenSpec; we wrote it. The name just follows
OpenSpec's convention so it sits naturally alongside the real commands.

There's no OpenSpec equivalent shipped today. A comparable `opsx:clarify`
command has been proposed upstream but is still an unmerged pull request, and
it's narrower anyway — single-artifact ambiguity Q&A rather than an interview
across the whole plan. OpenSpec's `explore` skill is also a different thing: it's
deliberately open-ended brainstorming ("open threads, not interrogations"),
whereas this one is the opposite stance.

---

## One-time setup

### 1. Install the skill

Ask the agent: **"Install the opsx-grill-me skill"** — try it in this tab; open a
new one only if it's not picked up.

If the agent doesn't know how, you haven't set up the skill manager yet — do
[Install](../../../README.md#install) in the repo root first.

That's it — there's nothing else to configure. The OpenSpec CLI is used if it's
present, but the skill still works without it.

---

## Using it

The simplest version:

> Grill me

If you have an OpenSpec change in flight, name it:

> Grill me on the add-user-auth change

Other phrasings that trigger it: "stress-test this design", "pressure-test this
plan before I build it", "poke holes in this proposal".

### What it actually does

1. Runs `openspec list --json` to see what changes are active
2. Reads the relevant `proposal.md`, `design.md`, and `tasks.md` for context
3. Interviews you one decision at a time, in dependency order, with a
   recommended answer attached to each question
4. Explores the codebase to answer its own questions where it can
5. When you've reached shared understanding, offers to write the resolved
   decisions back into the right artifact

### Where decisions land

| What was resolved | Where it gets captured |
|---|---|
| Scope change | `proposal.md` |
| Architecture decision | `design.md` |
| New tasks discovered | `tasks.md` |

---

## Things worth knowing

**It offers, it doesn't auto-write.** Nothing gets saved into your OpenSpec
artifacts unless you say yes.

**It works without OpenSpec.** If the repo doesn't use OpenSpec, or the CLI isn't
installed, it grills against whatever plan you've described in the conversation
instead of bailing out.

**It's meant to be uncomfortable.** Expect questions about failure modes,
migration and rollback, data ownership, and what breaks at 100x volume. If it
feels like it's pushing, it's working.

**Use it before `apply`, not during.** The point is to settle decisions while
they're still cheap to change. Once you're mid-implementation, the openspec apply
step is the better place to be.

---

## Troubleshooting

**It asks things it should have looked up** — tell it so ("read the code for
that"). The skill is instructed to prefer exploring over asking, but a nudge
helps on a big codebase.

**It's grilling the wrong change** — name the change explicitly: "grill me on
`<change-name>`". Without a name it infers from conversation context or picks the
only active change.

**The agent doesn't seem to know about the skill** — ask it directly in this
tab first; it may already be there. If it's still missing, open a new agent
tab, then ask the agent to "check my skills installation".
