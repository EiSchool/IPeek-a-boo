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


class ParseNetworkTests(unittest.TestCase):
    def test_accepted_formats(self):
        for text in ("192.168.1.0/24", "192.168.1.77/24", "192.168.1.0 255.255.255.0",
                     " 192.168.1.0/255.255.255.0 "):
            self.assertEqual(str(analysis.parse_network(text)), "192.168.1.0/24", text)

    def test_bare_address_is_single_host(self):
        self.assertEqual(analysis.parse_network("8.8.8.8").prefixlen, 32)

    def test_invalid_input_gives_friendly_error(self):
        for bad in ("hello", "192.168.1.0/33", "10.0.0.0 255.0.255.0", ""):
            with self.assertRaises(ValueError):
                analysis.parse_network(bad)


class SubnetInfoTests(unittest.TestCase):
    def info(self, text):
        return analysis.subnet_info(analysis.parse_network(text))

    def test_class_c_sized_subnet(self):
        info = self.info("192.168.1.130/24")
        self.assertEqual(info["Network address"], "192.168.1.0")
        self.assertEqual(info["Subnet mask"], "255.255.255.0")
        self.assertEqual(info["Wildcard mask"], "0.0.0.255")
        self.assertEqual(info["Broadcast address"], "192.168.1.255")
        self.assertEqual(info["First usable host"], "192.168.1.1")
        self.assertEqual(info["Last usable host"], "192.168.1.254")
        self.assertEqual(info["Usable hosts"], "254")
        self.assertEqual(info["Total addresses"], "256")
        self.assertEqual(info["Type"], "Private")

    def test_small_subnet_from_dotted_mask(self):
        info = self.info("10.10.10.70 255.255.255.224")
        self.assertEqual(info["Network"], "10.10.10.64/27")
        self.assertEqual(info["Broadcast address"], "10.10.10.95")
        self.assertEqual(info["Usable hosts"], "30")

    def test_point_to_point_and_single_host(self):
        p2p = self.info("203.0.113.0/31")
        self.assertEqual(p2p["Usable hosts"], "2")
        self.assertEqual(p2p["First usable host"], "203.0.113.0")
        self.assertEqual(p2p["Last usable host"], "203.0.113.1")
        host = self.info("8.8.8.8/32")
        self.assertEqual(host["Usable hosts"], "1")
        self.assertEqual(host["Type"], "Public")

    def test_huge_networks_are_instant(self):
        self.assertEqual(self.info("10.0.0.0/8")["Usable hosts"], "16,777,214")
        info = self.info("2001:db8::/64")
        self.assertEqual(info["Total addresses"], "18,446,744,073,709,551,616")
        self.assertEqual(info["Last address"], "2001:db8::ffff:ffff:ffff:ffff")
        self.assertNotIn("Broadcast address", info)


if __name__ == "__main__":
    unittest.main()
