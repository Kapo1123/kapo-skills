# Grill-me skill — setup and usage

Turns the agent into a relentless interviewer that pressure-tests a plan or
design before you build it. It walks the decision tree one branch at a time,
recommends an answer for every question it asks, and reads the codebase instead
of asking you things it could find out itself.

This is the general version. It works on any plan you describe in the
conversation and does not need OpenSpec or spec-kit. If the repo uses OpenSpec,
use `opsx-grill-me`. If it uses spec-kit, use `speckit-grill-me`.

> Looking for the agent-facing instructions? Those live in [SKILL.md](SKILL.md).
> This file is for humans.

---

## One-time setup

Ask the agent: **"Install the grill-me skill"**.

If the agent doesn't know how, set up the skill manager first — see
[Install](../../../README.md#install) in the repo root.

There's nothing else to configure.

---

## Using it

The skill only runs when you ask for it. Say:

> Grill me

Or: "stress-test this design", "pressure-test this plan before I build it".

It asks one focused question at a time, in dependency order, with a recommended
answer and a short reason for each. When every branch is settled, it sums up the
agreed design.

---

## Things worth knowing

**It doesn't write files.** The result is a summary in the chat. Save it where
you want.

**It's meant to be uncomfortable.** Expect questions about failure modes, edge
cases, and hidden assumptions.

**It asks things it should have looked up?** Tell it to read the code for that.

---

## Credits

The opening of [SKILL.md](SKILL.md) and its description come from [Matt
Pocock](https://github.com/mattpocock)'s `grill-me` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c)
2026 [Matt Pocock](https://github.com/mattpocock)).
