"""Tests for ipinfo.api using saved sample responses (no real network calls)."""

import unittest
from unittest import mock

from ipinfo import api

# Trimmed real-shaped responses from each API.
IPAPI_CO_SAMPLE = {
    "ip": "8.8.8.8", "city": "Mountain View", "region": "California",
    "country_name": "United States", "country_code": "US", "postal": "94043",
    "latitude": 37.42301, "longitude": -122.083352, "timezone": "America/Los_Angeles",
    "asn": "AS15169", "org": "GOOGLE",
}
IP_API_COM_SAMPLE = {
    "status": "success", "query": "8.8.8.8", "city": "Ashburn", "regionName": "Virginia",
    "country": "United States", "countryCode": "US", "zip": "20149",
    "lat": 39.03, "lon": -77.5, "timezone": "America/New_York",
    "isp": "Google LLC", "as": "AS15169 Google LLC",
}


class NormalizeTests(unittest.TestCase):
    def test_ipapi_co(self):
        d = api._from_ipapi_co(IPAPI_CO_SAMPLE)
        self.assertEqual(d["country_code"], "US")
        self.assertEqual(d["asn"], "AS15169")
        self.assertEqual(d["isp"], "GOOGLE")
        self.assertEqual(d["source"], "ipapi.co")

    def test_ip_api_com(self):
        d = api._from_ip_api_com(IP_API_COM_SAMPLE)
        self.assertEqual(d["asn"], "AS15169")  # company name stripped off
        self.assertEqual(d["region"], "Virginia")
        self.assertEqual(d["source"], "ip-api.com")

    def test_both_providers_produce_same_keys(self):
        self.assertEqual(api._from_ipapi_co(IPAPI_CO_SAMPLE).keys(),
                         api._from_ip_api_com(IP_API_COM_SAMPLE).keys())

    def test_error_responses_raise(self):
        with self.assertRaises(api.LookupFailed):
            api._from_ipapi_co({"error": True, "reason": "Reserved IP Address"})
        with self.assertRaises(api.LookupFailed):
            api._from_ip_api_com({"status": "fail", "message": "private range"})


class FallbackTests(unittest.TestCase):
    def test_uses_second_provider_when_first_fails(self):
        def fake_get_json(url):
            if "ipapi.co" in url:
                raise api.LookupFailed("Rate limit reached")
            return IP_API_COM_SAMPLE

        with mock.patch.object(api, "_get_json", side_effect=fake_get_json):
            self.assertEqual(api.get_ip_details("8.8.8.8")["source"], "ip-api.com")

    def test_raises_when_all_providers_fail(self):
        with mock.patch.object(api, "_get_json", side_effect=api.LookupFailed("offline")):
            with self.assertRaises(api.LookupFailed):
                api.get_ip_details("8.8.8.8")

    def test_no_ipv6_returns_none(self):
        with mock.patch.object(api, "_get_json", side_effect=api.LookupFailed("no route")):
            self.assertIsNone(api.get_public_ipv6())


class PrivacyCheckTests(unittest.TestCase):
    def test_flags_are_booleans(self):
        sample = {"status": "success", "proxy": True, "hosting": False, "mobile": False}
        with mock.patch.object(api, "_get_json", return_value=sample):
            flags = api.get_privacy_check("8.8.8.8")
        self.assertEqual(flags, {"VPN / proxy / Tor": True,
                                 "Hosting / data center": False,
                                 "Mobile network": False})

    def test_failed_status_raises(self):
        sample = {"status": "fail", "message": "private range"}
        with mock.patch.object(api, "_get_json", return_value=sample):
            with self.assertRaises(api.LookupFailed):
                api.get_privacy_check("192.168.1.1")


if __name__ == "__main__":
    unittest.main()
