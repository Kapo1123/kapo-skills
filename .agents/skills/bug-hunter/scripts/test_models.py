#!/usr/bin/env python3
"""Tests for models.py, which prints the model list for each bug-hunter role.

Standard library only:

    python3 test_models.py

Each test points SHARED_SKILLS_CONFIG at a file in a temp directory, so no
test reads or writes the real ~/.config/kapo-skills/config.json.
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "models.py"

DEFAULTS = {
    "triage": ["grok-4.7-high-fast", "grok", "haiku", "inherit"],
    "finder_light": ["grok-4.7-high-fast", "grok", "sonnet", "inherit"],
    "finder_heavy": ["sonnet", "opus", "inherit"],
    "refuter": ["sonnet", "opus", "inherit"],
    "rule_check": ["grok-4.7-high-fast", "grok", "sonnet", "inherit"],
    "mechanical": ["grok-4.7-high-fast", "grok", "haiku", "inherit"],
}


class ModelsTests(unittest.TestCase):

    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="bh-models-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.config = self.tmp / "config.json"

    def run_script(self, *args, config=None, env_value=None):
        env = dict(os.environ)
        env["SHARED_SKILLS_CONFIG"] = str(self.config) if env_value is None else env_value
        env["HOME"] = str(self.tmp / "home")
        if config is not None:
            self.config.write_text(config if isinstance(config, str) else json.dumps(config))
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True, env=env)

    def roles(self, result):
        """{role: (entries, source)} from the script's role lines."""
        out = {}
        for line in result.stdout.splitlines():
            if not line.startswith("role "):
                continue
            _, role, rest = line.split(" ", 2)
            entries, source = rest.rsplit("  (", 1)
            out[role] = (entries.split(", "), source.rstrip(")"))
        return out

    def warnings(self, result):
        return [l for l in result.stdout.splitlines() if l.startswith("warning ")]

    def test_no_config_file_prints_every_default(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        roles = self.roles(result)
        self.assertEqual({r: e for r, (e, _) in roles.items()}, DEFAULTS)
        self.assertTrue(all(s == "default" for _, s in roles.values()))
        self.assertEqual(self.warnings(result), [])

    def test_roles_print_in_a_fixed_order(self):
        result = self.run_script()
        order = [l.split(" ")[1] for l in result.stdout.splitlines() if l.startswith("role ")]
        self.assertEqual(order, list(DEFAULTS))

    def test_an_override_replaces_only_that_role(self):
        result = self.run_script(config={"repo": "/x", "bug-hunter": {"models": {
            "finder_light": ["sonnet", "inherit"]}}})
        roles = self.roles(result)
        self.assertEqual(roles["finder_light"], (["sonnet", "inherit"], "config"))
        self.assertEqual(roles["refuter"], (DEFAULTS["refuter"], "default"))
        self.assertEqual(self.warnings(result), [])

    def test_inherit_is_added_when_a_list_leaves_it_out(self):
        roles = self.roles(self.run_script(config={"bug-hunter": {"models": {
            "refuter": ["opus"]}}}))
        self.assertEqual(roles["refuter"], (["opus", "inherit"], "config"))

    def test_entries_after_inherit_are_dropped(self):
        result = self.run_script(config={"bug-hunter": {"models": {
            "refuter": ["opus", "inherit", "sonnet"]}}})
        self.assertEqual(self.roles(result)["refuter"], (["opus", "inherit"], "config"))
        self.assertEqual(len(self.warnings(result)), 1)

    def test_an_unknown_role_is_a_warning_not_a_failure(self):
        result = self.run_script(config={"bug-hunter": {"models": {"fixer": ["opus"]}}})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(self.warnings(result)), 1)
        self.assertIn("fixer", self.warnings(result)[0])
        self.assertEqual({r: e for r, (e, _) in self.roles(result).items()}, DEFAULTS)

    def test_a_bad_role_value_falls_back_to_that_role_default(self):
        for value in ("sonnet", [], [""], ["two words"], ["a\nb"], [1], None, {"x": 1}):
            with self.subTest(value=value):
                result = self.run_script(config={"bug-hunter": {"models": {"refuter": value}}})
                self.assertEqual(result.returncode, 0)
                self.assertEqual(self.roles(result)["refuter"], (DEFAULTS["refuter"], "default"))
                self.assertEqual(len(self.warnings(result)), 1)

    def test_a_damaged_config_uses_every_default_and_says_so(self):
        for text in ("{not json", "[]", '"x"', '{"bug-hunter": []}',
                     '{"bug-hunter": {"models": []}}'):
            with self.subTest(text=text):
                result = self.run_script(config=text)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual({r: e for r, (e, _) in self.roles(result).items()}, DEFAULTS)
                self.assertEqual(len(self.warnings(result)), 1)

    def test_a_config_without_the_key_is_silent(self):
        result = self.run_script(config={"repo": "/x", "hooks_off": ["prose"]})
        self.assertEqual(self.warnings(result), [])
        self.assertEqual({r: e for r, (e, _) in self.roles(result).items()}, DEFAULTS)

    def test_entries_are_trimmed(self):
        roles = self.roles(self.run_script(config={"bug-hunter": {"models": {
            "triage": ["  haiku ", "inherit"]}}}))
        self.assertEqual(roles["triage"], (["haiku", "inherit"], "config"))

    def test_the_config_path_is_printed(self):
        result = self.run_script()
        self.assertIn(f"config {self.config} (missing)", result.stdout)
        result = self.run_script(config={})
        self.assertIn(f"config {self.config} (read)", result.stdout)

    def test_an_empty_env_value_means_the_default_path(self):
        result = self.run_script(env_value="")
        default = self.tmp / "home" / ".config" / "kapo-skills" / "config.json"
        self.assertIn(f"config {default} (missing)", result.stdout)

    def test_the_script_writes_nothing(self):
        self.run_script(config={"bug-hunter": {"models": {"refuter": ["opus"]}}})
        self.assertEqual(json.loads(self.config.read_text()),
                         {"bug-hunter": {"models": {"refuter": ["opus"]}}})
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["config.json"])

    def test_warnings_come_after_the_role_lines(self):
        # SKILL.md, "Models by role": one `role` line per role, then any
        # `warning` lines.
        result = self.run_script(config={"bug-hunter": {"models": {"fixer": ["opus"]}}})
        kinds = [l.split(" ")[0] for l in result.stdout.splitlines()
                 if l.startswith(("role ", "warning "))]
        self.assertEqual(kinds, ["role"] * len(DEFAULTS) + ["warning"])

    @unittest.skipIf(os.geteuid() == 0, "root can stat inside a mode-000 directory")
    def test_a_config_that_cannot_be_reached_is_unreadable_not_missing(self):
        locked = self.tmp / "locked"
        locked.mkdir()
        inside = locked / "config.json"
        inside.write_text(json.dumps({"bug-hunter": {"models": {"refuter": ["opus"]}}}))
        locked.chmod(0)
        self.addCleanup(locked.chmod, 0o700)
        result = self.run_script(env_value=str(inside))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"config {inside} (unreadable)", result.stdout)
        self.assertEqual(len(self.warnings(result)), 1)

    def test_any_argument_is_refused(self):
        result = self.run_script("--mode", "heavy")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
