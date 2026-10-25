"""Tests for ipinfo.export - writes into a temporary folder."""

import csv
import json
import tempfile
import unittest

from ipinfo import export

SAMPLE = {
    "Public addresses": {"IPv4": "203.0.113.5", "IPv6": None},
    "Location & provider": {"city": "Manila", "asn": "AS9299"},
}


class ExportTests(unittest.TestCase):
    def test_json_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            path = export.save_results(SAMPLE, "json", folder)
            with open(path, encoding="utf-8") as f:
                self.assertEqual(json.load(f), SAMPLE)

    def test_csv_has_one_row_per_field(self):
        with tempfile.TemporaryDirectory() as folder:
            path = export.save_results(SAMPLE, "csv", folder)
            with open(path, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            self.assertEqual(rows[0], ["section", "field", "value"])
            self.assertEqual(len(rows), 1 + 4)

    def test_unknown_format_rejected(self):
        with self.assertRaises(ValueError):
            export.save_results(SAMPLE, "xml")


if __name__ == "__main__":
    unittest.main()
