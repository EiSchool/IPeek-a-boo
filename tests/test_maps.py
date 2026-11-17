"""Tests for ipinfo.maps - the "Where am I?" map links."""

import unittest

from ipinfo import maps


class MapLinkTests(unittest.TestCase):
    def test_links_built_from_coordinates(self):
        links = maps.map_links({"latitude": 14.5995, "longitude": 120.9842})
        self.assertEqual(links["Google Maps"],
                         "https://www.google.com/maps/search/?api=1&query=14.5995,120.9842")
        self.assertIn("mlat=14.5995&mlon=120.9842", links["OpenStreetMap"])

    def test_rounds_and_accepts_numeric_strings(self):
        links = maps.map_links({"latitude": "37.42301", "longitude": -122.083352})
        self.assertIn("query=37.4230,-122.0834", links["Google Maps"])

    def test_missing_or_bad_coordinates_give_none(self):
        for details in ({}, {"latitude": None, "longitude": 1},
                        {"latitude": "abc", "longitude": 1},
                        {"latitude": 91, "longitude": 0},
                        {"latitude": 0, "longitude": -181}):
            self.assertIsNone(maps.map_links(details), details)

    def test_zero_is_a_real_coordinate(self):
        self.assertIsNotNone(maps.map_links({"latitude": 0, "longitude": 0}))


if __name__ == "__main__":
    unittest.main()
