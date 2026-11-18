"""Tests for ipinfo.history - the "Your IP changed!" alert. Uses a temporary folder."""

import os
import tempfile
import unittest
from datetime import datetime

from ipinfo import history

FIRST = datetime(2026, 10, 31, 20, 0, 0)
LATER = datetime(2026, 11, 1, 9, 30, 0)


class IpChangeTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "last_ip.json")

    def tearDown(self):
        self.folder.cleanup()

    def test_first_run(self):
        result = history.check_and_record("203.0.113.5", None, self.path, FIRST)
        self.assertEqual(result, {"Status": "First peek"})
        self.assertEqual(history.load_last(self.path)["Checked at"], "2026-10-31 20:00:00")

    def test_same_ip_is_unchanged(self):
        history.check_and_record("203.0.113.5", None, self.path, FIRST)
        result = history.check_and_record("203.0.113.5", None, self.path, LATER)
        self.assertEqual(result["Status"], "Unchanged")
        self.assertEqual(result["Previous check"], "2026-10-31 20:00:00")

    def test_changed_ipv4_is_reported(self):
        history.check_and_record("203.0.113.5", "2001:db8::1", self.path, FIRST)
        result = history.check_and_record("198.51.100.7", "2001:db8::1", self.path, LATER)
        self.assertEqual(result["Status"], "CHANGED")
        self.assertEqual(result["Changed"], "IPv4")
        self.assertEqual(result["Previous IPv4"], "203.0.113.5")
        # The new address is now the one remembered for next time.
        self.assertEqual(history.load_last(self.path)["IPv4"], "198.51.100.7")

    def test_losing_ipv6_counts_as_a_change(self):
        history.check_and_record("203.0.113.5", "2001:db8::1", self.path, FIRST)
        result = history.check_and_record("203.0.113.5", None, self.path, LATER)
        self.assertEqual(result["Changed"], "IPv6")

    def test_damaged_file_is_treated_as_first_run(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{not json")
        result = history.check_and_record("203.0.113.5", None, self.path, FIRST)
        self.assertEqual(result["Status"], "First peek")

    def test_unwritable_location_does_not_crash(self):
        # A path *inside a file* can never be created.
        blocker = os.path.join(self.folder.name, "blocker")
        open(blocker, "w").close()
        result = history.check_and_record("203.0.113.5", None,
                                          os.path.join(blocker, "x.json"), FIRST)
        self.assertEqual(result["Status"], "First peek")
        self.assertIn("Note", result)


if __name__ == "__main__":
    unittest.main()
