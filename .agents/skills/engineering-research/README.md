# engineering-research

Researches a software problem before you build: searches GitHub,
StackOverflow, Reddit, package registries, and official docs, checks that
each candidate is still maintained, and returns a short summary with a
recommendation and links.

The idea: most problems are already solved, or 90% solved. Find that, then
adapt it.

> Agent instructions: [SKILL.md](SKILL.md).

## Setup

Ask the agent: **"Install the engineering-research skill"**. Try it in this
tab. Open a new tab only if it is not picked up.

If the agent does not know how, set up the skill manager first. See
[Install](../../../README.md#install) in the repo root.

It needs a web search tool. Nothing else.

## Using it

The skill only runs when you ask for it by name:

> "Use engineering-research: best way to rate-limit per user in Express"
> "Use engineering-research to compare X and Y"

## When something looks wrong

**It recommended an abandoned package.** Every option must pass the
maintenance check (not archived, no deprecation notice, recent activity).
Point it out and ask for the maintained fork or an alternative.
