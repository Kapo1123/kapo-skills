#!/usr/bin/env python3
"""Tests for the window snippet in ../SKILL.md, section "1. Window".

Standard library only:

    python3 test_window.py

The snippet is read out of SKILL.md and run as written, with "now" faked,
so the test guards the text an agent copies. Each case runs in its own
process with TZ set, because time.tzset() changes the whole process.
"""

import json
import pathlib
import re
import subprocess
import sys
import textwrap
import unittest

SKILL = pathlib.Path(__file__).resolve().parent.parent / "SKILL.md"

# Installs a fake datetime module whose datetime.now() returns a fixed UTC
# instant, then runs the snippet and prints its start beside true local
# midnight. True midnight is a naive local midnight resolved by the OS,
# which uses the offset in force at midnight, not the offset in force now.
HARNESS = textwrap.dedent("""
    import datetime as real, json, sys, time, types
    time.tzset()
    fake_utc = real.datetime.fromisoformat(sys.argv[1])

    class FakeDateTime(real.datetime):
        @classmethod
        def now(cls, tz=None):
            moment = fake_utc.astimezone(tz) if tz else fake_utc.astimezone().replace(tzinfo=None)
            return cls.fromisoformat(moment.isoformat())

    fake = types.ModuleType("datetime")
    fake.__dict__.update({k: getattr(real, k) for k in dir(real) if not k.startswith("__")})
    fake.datetime = FakeDateTime
    sys.modules["datetime"] = fake

    scope = {}
    exec(sys.stdin.read(), scope)
    local_now = fake_utc.astimezone()
    midnight = real.datetime(local_now.year, local_now.month, local_now.day).astimezone()
    print(json.dumps({"start": scope["start"].isoformat(), "midnight": midnight.isoformat()}))
""")


def window_snippet():
    """The first python block under '## 1. Window' in SKILL.md."""
    text = SKILL.read_text()
    section = text.split("## 1. Window", 1)[1].split("\n## ", 1)[0]
    match = re.search(r"```python\n(.*?)```", section, re.S)
    if not match:
        raise AssertionError("no python block under '## 1. Window' in SKILL.md")
    return match.group(1)


def run(tz, fake_utc):
    result = subprocess.run(
        [sys.executable, "-c", HARNESS, fake_utc],
        input=window_snippet(), capture_output=True, text=True,
        env={"TZ": tz, "PATH": "/usr/bin:/bin"}, check=True,
    )
    return json.loads(result.stdout)


class WindowStartTests(unittest.TestCase):
    """The window starts at local midnight, whatever the offset is now."""

    def assertStartsAtMidnight(self, tz, fake_utc):
        got = run(tz, fake_utc)
        self.assertEqual(got["start"], got["midnight"], f"{tz} at {fake_utc}")

    def test_ordinary_day(self):
        self.assertStartsAtMidnight("America/Chicago", "2026-10-27T20:00:00+00:00")

    def test_day_daylight_saving_ends(self):
        # 2026-11-01: midnight is CDT (-05:00), the afternoon is CST (-06:00).
        self.assertStartsAtMidnight("America/Chicago", "2026-11-01T20:00:00+00:00")

    def test_day_daylight_saving_starts(self):
        # 2026-03-08: midnight is CST (-06:00), the afternoon is CDT (-05:00).
        self.assertStartsAtMidnight("America/Chicago", "2026-03-08T19:00:00+00:00")

    def test_utc(self):
        self.assertStartsAtMidnight("UTC", "2026-10-27T13:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
