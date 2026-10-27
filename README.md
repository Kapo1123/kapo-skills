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

`.agents/lib/commit-trailer/` is shared code that `bug-hunter` uses to sign
and check its commit trailer.

## Requirements

- macOS or Linux. Skills are installed as symlinks. Windows is not tested.
- Python 3.8 or later, as `python3`.
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
Contributors: Adam Stallard, Harsh, Cristian Cantu, Evan Luong, and Kapo Kwok.
