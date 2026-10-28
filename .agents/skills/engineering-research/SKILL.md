---
name: engineering-research
description: Research software engineering problems by searching GitHub, Reddit, StackOverflow, package registries, and documentation to find existing solutions and proven approaches. Use when exploring feature implementation options, evaluating packages or libraries, discovering APIs or services, or deciding how to approach a problem. Core philosophy: every problem is probably already solved — find it, understand it, then adapt it.
disable-model-invocation: true
---

# Engineering Research

The foundation: software engineering is not rocket science. Every problem you face has almost certainly been solved — or a 90% solution exists that needs a small twist. Research before building.

## Research Workflow

### 1. Frame the Problem

Before searching, distill the question into:
- **What**: The concrete thing you need (e.g., "deduplicate a stream of events", "paginate a GraphQL cursor", "rate-limit per user per endpoint")
- **Constraints**: Language, framework, scale, licensing, hosted vs self-hosted
- **Non-goals**: What you are explicitly NOT trying to solve

### 2. Search Strategy

Run searches in parallel across sources. Use `WebSearch` for all of these.

**GitHub**
- `site:github.com <problem> <language/framework>`
- Search GitHub issues for error messages verbatim
- Look at "Used by" count and recent commit activity on repos
- Check the Issues tab for known pain points before committing to a library

**StackOverflow**
- `site:stackoverflow.com <problem>`
- Sort by votes, not recency — old accepted answers are often still correct
- Check the comments on accepted answers; often the real nuance is there

**Reddit**
- `site:reddit.com <problem>` or search directly on reddit.com
- Good subreddits: r/programming, r/webdev, r/devops, r/node, r/java, r/python, r/aws, r/golang, r/rust — pick the relevant one
- Reddit threads often surface "we tried X and switched to Y because Z" real-world experience that docs never mention

**Package registries**
- npm: `npmjs.com/search?q=<keyword>`
- PyPI: `pypi.org/search/?q=<keyword>`
- Maven Central: `search.maven.org`
- Crates.io: for Rust
- Filter by: weekly downloads, last published date, GitHub stars
- **Always check the npm/PyPI page for deprecation notices** — look for "Package no longer supported", "deprecated", or "archived" banners before recommending

**Official docs / changelogs**
- Go to the source when evaluating a specific package or API
- Always check the changelog / migration guide for the version you'd actually use

**Maintenance health check (mandatory for every candidate)**

Before including any option in the summary, verify all of the following:
- GitHub: Is the repo archived? (`archived: true` on the repo page = dead)
- GitHub: When was the last commit? Last issue response? (>12 months with no activity = red flag)
- npm/PyPI: Is there a deprecation warning on the registry page?
- GitHub Issues: Are bug reports being closed as "not planned" or left open indefinitely?
- Search `site:github.com <package-name> deprecated OR archived OR unmaintained` to catch indirect signals

If a package fails the maintenance check, **do not recommend it** — find the actively maintained fork or alternative instead, and note why the original was dropped.

### 3. Evaluate What You Find

For every candidate solution, check:

| Signal | Green | Yellow | Red |
|--------|-------|--------|-----|
| Maintenance | Active commits, issues responded to in <30 days | Slow but alive, last commit <12 mo | Archived / abandoned / deprecated |
| npm/registry status | No deprecation notice, actively published | Old version pinned | "Package no longer supported" warning |
| Adoption | Widely used in production | Niche but loved | Unknown / zero downloads |
| Fit | Solves the exact constraint | Needs a wrapper | Requires forking |
| Complexity | Drop-in or small integration | Moderate setup | Invasive / opinionated |
| License | MIT / Apache 2.0 | LGPL (check) | GPL / proprietary |

### 4. Synthesize and Recommend

Summarize findings with:

```
## Research Summary: <problem>

### TL;DR
<One-line recommendation>

### Options found
1. **<option>** — <what it does>, <adoption signal>, <tradeoff>
2. **<option>** — ...

### Recommended approach
<Why this option, given the constraints>

### Twist needed (if any)
<Any adaptation required for this specific context>

### References
- <URL> — <one-line description>
```

## Heuristics

- **Boring is good.** A 5-year-old library with 10k stars and zero recent churn is often better than a shiny new one.
- **Read the issues before the README.** The README sells; the issues tell the truth.
- **Check the registry page, not just GitHub.** A package can look alive on GitHub but carry a deprecation warning on npm/PyPI that only appears at install time.
- **"Official" does not mean "maintained."** Even first-party packages get archived (e.g. Anthropic archived their own MCP servers in 2025). Always verify.
- **Find the active fork when the original is dead.** Archived packages often have community forks that fix the exact bugs that caused the original to be abandoned — prefer those over the original.
- **Prefer composition over invention.** Two focused packages glued together usually beats one complex custom implementation.
- **"Prior art" is the goal.** If someone on StackOverflow already solved it, that's the answer. Adapt it.
- **When in doubt, search the error message verbatim.** Someone has hit it.

## Common Research Triggers

- "What's the best way to…" → research packages + StackOverflow
- "Is there a library for…" → research npm/PyPI/Maven + GitHub
- "How do people usually handle…" → research Reddit + GitHub discussions
- "Should we use X or Y" → compare both on GitHub stars, issues, and Reddit experience threads
- "This API doesn't support…" → search GitHub issues on that API's repo first
