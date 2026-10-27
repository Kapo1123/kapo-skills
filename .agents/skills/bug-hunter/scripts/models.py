#!/usr/bin/env python3
"""Print the ordered model list for each bug-hunter role.

Standard library only. Takes no arguments:

    python3 models.py

The defaults live here and nowhere else; SKILL.md tells the agent to run this
script rather than repeating the slugs, so the two cannot drift. A person
overrides a role in the kapo-skills config file, under the "bug-hunter" key:

    {"bug-hunter": {"models": {"refuter": ["opus", "sonnet", "inherit"]}}}

That file is the one manage-skills keeps (SHARED_SKILLS_CONFIG, else
~/.config/kapo-skills/config.json). The lookup is repeated here rather than
imported from skills.py, so bug-hunter works without manage-skills installed.

The script cannot see which models the host offers. It prints the preference
order; the agent takes the first entry the host lists (SKILL.md, "Models by
role"). A damaged config never blocks a hunt: the script warns, uses the
defaults for whatever it could not read, and exits 0. Exit 2 for any argument.

Why the defaults are what they are: ../DECISIONS.md, "Models by role, from
settings".
"""

import json
import os
import pathlib
import re
import sys

ROLES = {
    "triage": ["grok-4.7-high-fast", "grok", "haiku", "inherit"],
    "finder_light": ["grok-4.7-high-fast", "grok", "sonnet", "inherit"],
    "finder_heavy": ["sonnet", "opus", "inherit"],
    "refuter": ["sonnet", "opus", "inherit"],
    "rule_check": ["grok-4.7-high-fast", "grok", "sonnet", "inherit"],
    "mechanical": ["grok-4.7-high-fast", "grok", "haiku", "inherit"],
}

INHERIT = "inherit"

# A slug, a family word, or "inherit". No spaces, commas or line breaks: each
# role prints as one line with ", " between entries, and the agent passes an
# entry verbatim as a model name.
ENTRY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]*")


def config_path():
    return pathlib.Path(
        os.environ.get("SHARED_SKILLS_CONFIG")
        or pathlib.Path.home() / ".config" / "kapo-skills" / "config.json"
    ).expanduser()


def read_overrides(path, warn):
    """(status, {role: raw value}) from the config file."""
    # Not path.exists(): it returns False when a parent directory cannot be
    # searched, which would report an unreachable config as missing and drop
    # the override with no warning.
    try:
        data = json.loads(path.read_text())
    except (FileNotFoundError, NotADirectoryError):
        return "missing", {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as err:
        warn(f"config is unreadable ({type(err).__name__}); using every default")
        return "unreadable", {}
    if not isinstance(data, dict):
        warn("config is not a JSON object; using every default")
        return "read", {}
    section = data.get("bug-hunter")
    if section is None:
        return "read", {}
    models = section.get("models") if isinstance(section, dict) else None
    if not isinstance(models, dict):
        if isinstance(section, dict) and "models" not in section:
            return "read", {}
        warn('"bug-hunter" must be {"models": {<role>: [<entry>, ...]}}; using every default')
        return "read", {}
    return "read", models


def clean(role, value, warn):
    """The role's list from a config value, or None to keep the default."""
    if not isinstance(value, list) or not value:
        warn(f"role {role} must be a non-empty list of model names; using its default")
        return None
    entries = []
    for item in value:
        entry = item.strip() if isinstance(item, str) else None
        if not entry or not ENTRY.fullmatch(entry):
            warn(f"role {role} has an entry that is not a model name ({item!r}); using its default")
            return None
        entries.append(entry)
    if INHERIT in entries:
        cut = entries.index(INHERIT) + 1
        if cut < len(entries):
            warn(f"role {role}: entries after inherit are never reached; dropped")
        entries = entries[:cut]
    else:
        entries.append(INHERIT)
    return entries


def main(argv):
    if argv:
        print("usage: models.py   (takes no arguments)", file=sys.stderr)
        return 2
    warnings = []
    path = config_path()
    status, overrides = read_overrides(path, warnings.append)
    resolved = {}
    for role, value in overrides.items():
        if role not in ROLES:
            warnings.append(f"unknown role {role!r} ignored; roles are {', '.join(ROLES)}")
            continue
        entries = clean(role, value, warnings.append)
        if entries is not None:
            resolved[role] = entries

    print("bug-hunter models: per role, pass the first entry the host lists")
    print(f"config {path} ({status})")
    for role, default in ROLES.items():
        entries = resolved.get(role, default)
        source = "config" if role in resolved else "default"
        print(f"role {role} {', '.join(entries)}  ({source})")
    for warning in warnings:
        print(f"warning {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
