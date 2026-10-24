"""Tests for ipinfo.analysis (offline - no internet needed)."""

import unittest

from ipinfo import analysis


class ParseIpTests(unittest.TestCase):
    def test_valid_ipv4_and_ipv6(self):
        self.assertEqual(analysis.parse_ip("8.8.8.8").version, 4)
        self.assertEqual(analysis.parse_ip("  2001:4860:4860::8888 ").version, 6)

    def test_invalid_input_gives_friendly_error(self):
        for bad in ("hello", "256.1.1.1", "1.2.3", ""):
            with self.assertRaises(ValueError):
                analysis.parse_ip(bad)


class AddressTypeTests(unittest.TestCase):
    def check(self, ip, expected):
        self.assertEqual(analysis.address_type(analysis.parse_ip(ip)), expected, ip)

    def test_ipv4_types(self):
        self.check("8.8.8.8", "Public")
        self.check("192.168.1.10", "Private")
        self.check("10.0.0.1", "Private")
        self.check("127.0.0.1", "Loopback")
        self.check("169.254.10.20", "Link-local")
        self.check("224.0.0.1", "Multicast")
        self.check("0.0.0.0", "Unspecified")
        self.check("100.64.0.1", "Special use (e.g. carrier-grade NAT)")

    def test_ipv6_types(self):
        self.check("2001:4860:4860::8888", "Public")
        self.check("::1", "Loopback")
        self.check("fe80::1", "Link-local")
        self.check("fc00::1", "Private")


class Ipv4ClassTests(unittest.TestCase):
    def test_classes(self):
        cases = {"10.1.1.1": "A", "172.16.0.1": "B", "192.168.0.1": "C",
                 "224.0.0.1": "D (multicast)", "240.0.0.1": "E (experimental)"}
        for ip, expected in cases.items():
            self.assertEqual(analysis.ipv4_class(analysis.parse_ip(ip)), expected, ip)


class AnalyzeTests(unittest.TestCase):
    def test_ipv4_facts(self):
        info = analysis.analyze(analysis.parse_ip("192.168.1.1"))
        self.assertEqual(info["Version"], "IPv4")
        self.assertEqual(info["Binary"], "11000000.10101000.00000001.00000001")
        self.assertEqual(info["Integer"], 3232235777)
        self.assertEqual(info["Reverse DNS name"], "1.1.168.192.in-addr.arpa")

    def test_ipv6_facts(self):
        info = analysis.analyze(analysis.parse_ip("2001:db8::1"))
        self.assertEqual(info["Version"], "IPv6")
        self.assertEqual(info["Compressed"], "2001:db8::1")
        self.assertEqual(info["Exploded"], "2001:0db8:0000:0000:0000:0000:0000:0001")


if __name__ == "__main__":
    unittest.main()
