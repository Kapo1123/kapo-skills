# kapo-skills

Agent skills for Claude Code and Cursor. Install them once and use them in
every project. Each skill is a symlink back to one clone of this repository,
so `git pull` updates them all.

Licensed under the [MIT License](LICENSE).

## Skills

| Skill | What it does | Docs |
| --- | --- | --- |
| `manage-skills` | Installs, removes, updates, and checks the skills in this repo. Start here | [README](.agents/skills/manage-skills/README.md) · [SKILL.md](.agents/skills/manage-skills/SKILL.md) |
| `bug-hunter` | Catches bugs in code you asked to commit, before it is committed. Every bug is proven with a failing test first | [README](.agents/skills/bug-hunter/README.md) · [SKILL.md](.agents/skills/bug-hunter/SKILL.md) |
| `create-system-spec` | Sets up system specs in a repo once: proposes a split by concern, writes the specs and a root `SYSTEM_SPECS.md` index. Needs `maintain-system-spec` | [README](.agents/skills/create-system-spec/README.md) · [SKILL.md](.agents/skills/create-system-spec/SKILL.md) |
| `maintain-system-spec` | Checks system specs against the code: fixes stale specs, reports code that breaks a rule, and holds looser rules for your OK. Never edits code or commits | [README](.agents/skills/maintain-system-spec/README.md) · [SKILL.md](.agents/skills/maintain-system-spec/SKILL.md) |
| `midday-report` | Drafts a mid-day Slack update of work so far today, asks for review or feedback where it applies, and sends only after you say so | [README](.agents/skills/midday-report/README.md) · [SKILL.md](.agents/skills/midday-report/SKILL.md) |
| `openspec-propose` | Creates an OpenSpec change and writes its proposal, design, and tasks in one step. Needs the `openspec` CLI | [SKILL.md](.agents/skills/openspec-propose/SKILL.md) |
| `openspec-explore` | Thinking-partner mode: explores an idea or problem before or during an OpenSpec change, without writing code | [SKILL.md](.agents/skills/openspec-explore/SKILL.md) |
| `openspec-apply-change` | Works through the tasks of an OpenSpec change. Needs the `openspec` CLI | [SKILL.md](.agents/skills/openspec-apply-change/SKILL.md) |
| `openspec-archive-change` | Archives a finished OpenSpec change. Needs the `openspec` CLI | [SKILL.md](.agents/skills/openspec-archive-change/SKILL.md) |
| `openspec-summarize-archive` | Writes a one-page `SUMMARY.md` into archived OpenSpec changes so past work is quick to look up | [README](.agents/skills/openspec-summarize-archive/README.md) · [SKILL.md](.agents/skills/openspec-summarize-archive/SKILL.md) |
| `opsx-grill-me` | Interviews you about an OpenSpec change or plan, one decision at a time, until the open questions are settled | [README](.agents/skills/opsx-grill-me/README.md) · [SKILL.md](.agents/skills/opsx-grill-me/SKILL.md) |
| `speckit-grill-me` | The same interview for a spec-kit feature spec (`specs/<name>/`) | [SKILL.md](.agents/skills/speckit-grill-me/SKILL.md) |
| `grill-me` | The same interview for any plan or design. Use this one when the repo is not using OpenSpec or spec-kit | [README](.agents/skills/grill-me/README.md) · [SKILL.md](.agents/skills/grill-me/SKILL.md) |
| `engineering-research` | Researches a problem across GitHub, StackOverflow, Reddit, package registries, and docs, drops unmaintained options, and recommends one with links. Runs only when asked by name | [README](.agents/skills/engineering-research/README.md) · [SKILL.md](.agents/skills/engineering-research/SKILL.md) |
| `update-work-notes` | Drafts a daily entry for an Obsidian vault's `Work Notes/` log from Google Drive meeting notes and Cursor chats, and writes only after you confirm | [README](.agents/skills/update-work-notes/README.md) · [SKILL.md](.agents/skills/update-work-notes/SKILL.md) |

`.agents/lib/commit-trailer/` is shared code that `bug-hunter` uses to sign
and check its commit trailer.

`open-pr-workflow` is not in this repo. When a commit breaks a system-spec
rule, `bug-hunter` records it and pauses. To settle each rule, run
`maintain-system-spec` yourself: update the spec, keep the old behavior, or
skip for now.

## Commit messages

Skills that write commits pick the subject style in this order:

1. If the repo has a doc that states its naming convention, follow that.
2. If it does not, and `git log` shows one clear repeated pattern, follow that.
3. Otherwise use `TYPE(Scope): subject`, and add `(agentic)` when an agent
   wrote the commit.

## Requirements

- macOS or Linux. Skills are installed as symlinks. Windows is not tested.
- Python 3.8 or later, as `python3`, for most skills. `update-work-notes`
  needs Python 3.10 or later.
- git 2.32 or later. In a repo with a `pre-commit` hook, `bug-hunter` needs
  git 2.36 or later.

## Install

```bash
git clone https://github.com/Kapo1123/kapo-skills.git ~/kapo-skills
~/kapo-skills/install.sh
```

The clone can live anywhere; the installer records where it is. Don't move it
afterwards, since every installed skill points into it.

The installer adds one skill, `manage-skills`. Ask your agent for the rest:

> "What skills are available?"
> "Install the bug-hunter skill"

Each skill goes into both `~/.agents/skills/` and `~/.claude/skills/`. If the
agent doesn't see a new skill, start a new session.

Installing `bug-hunter` also turns on its hook, written to
`~/.claude/settings.json` and `~/.cursor/hooks.json`. To turn it off, see
[Skills that come with a hook](.agents/skills/manage-skills/README.md#skills-that-come-with-a-hook).

To update, ask the agent to "update my skills", or run:

```bash
python3 ~/.agents/skills/manage-skills/scripts/skills.py update
```

## Tests

```bash
python3 .agents/skills/manage-skills/scripts/test_skills.py
python3 .agents/skills/bug-hunter/scripts/test_hook.py
python3 .agents/skills/bug-hunter/scripts/test_caller_result.py
```

## Credits

Adam Stallard is the original author of `bug-hunter` and `manage-skills`.
`openspec-propose`, `openspec-explore`, `openspec-apply-change`, and
`openspec-archive-change` are generated by the
[OpenSpec](https://github.com/Fission-AI/OpenSpec) CLI (MIT) and kept as
generated.
`grill-me` starts from Matt Pocock's `grill-me` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT).
Contributors: Adam Stallard, Harsh, Cristian Cantu, Evan Luong, and Kapo Kwok.
