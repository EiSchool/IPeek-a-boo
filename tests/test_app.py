"""Integration tests for app.py: the menu actions with the APIs faked, and one
end-to-end run of the real program driven through stdin (offline options only).
"""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from rich.console import Console

import app
from ipinfo import api, display, history

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DETAILS = {
    "ip": "203.0.113.5", "city": "Manila", "region": "Metro Manila",
    "country": "Philippines", "country_code": "PH", "postal": "1000",
    "latitude": 14.5995, "longitude": 120.9842, "timezone": "Asia/Manila",
    "isp": "Example ISP", "asn": "AS64500", "source": "ipapi.co",
}
FLAGS = {"VPN / proxy / Tor": False, "Hosting / data center": False, "Mobile network": False}


class MenuActionTests(unittest.TestCase):
    """Each menu action, with the network and the screen replaced by fakes."""

    def setUp(self):
        self.screen = io.StringIO()
        self.folder = tempfile.TemporaryDirectory()
        patches = [
            mock.patch.object(display, "console", Console(file=self.screen, width=120)),
            mock.patch.object(history, "HISTORY_FILE",
                              os.path.join(self.folder.name, "last_ip.json")),
            mock.patch.object(api, "get_public_ipv4", return_value="203.0.113.5"),
            mock.patch.object(api, "get_public_ipv6", return_value=None),
            mock.patch.object(api, "get_ip_details", return_value=DETAILS),
            mock.patch.object(api, "get_privacy_check", return_value=FLAGS),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.addCleanup(self.folder.cleanup)

    def test_my_public_ip_has_every_section(self):
        result = app.my_public_ip()
        self.assertEqual(list(result), ["Public addresses", "IP change check",
                                        "Location & provider", "Where am I?",
                                        "Peek-a-Boo check"])
        self.assertEqual(result["IP change check"]["Status"], "First peek")
        self.assertIn("14.5995,120.9842", result["Where am I?"]["Google Maps"])

    def test_second_run_with_new_ip_raises_the_alert(self):
        app.my_public_ip()
        with mock.patch.object(api, "get_public_ipv4", return_value="198.51.100.7"):
            result = app.my_public_ip()
        self.assertEqual(result["IP change check"]["Status"], "CHANGED")
        self.assertIn("BOO! Your IP changed", self.screen.getvalue())

    def test_lookup_private_ip_skips_geolocation(self):
        with mock.patch.object(display, "ask", return_value="192.168.1.1"):
            result = app.lookup_ip()
        self.assertEqual(list(result), ["Address facts"])
        api.get_ip_details.assert_not_called()

    def test_lookup_public_ip_adds_map(self):
        with mock.patch.object(display, "ask", return_value="8.8.8.8"):
            result = app.lookup_ip()
        self.assertIn("Where am I?", result)

    def test_geolocation_failure_is_friendly(self):
        with mock.patch.object(display, "ask", return_value="8.8.8.8"), \
             mock.patch.object(api, "get_ip_details", side_effect=api.LookupFailed("offline")):
            result = app.lookup_ip()
        self.assertNotIn("Location & provider", result)
        self.assertIn("Eek!", self.screen.getvalue())

    def test_subnet_calculator(self):
        with mock.patch.object(display, "ask", return_value="10.0.0.1 255.255.255.0"):
            result = app.subnet_calculator()
        self.assertEqual(result["Subnet calculator"]["Broadcast address"], "10.0.0.255")

    def test_subnet_calculator_rejects_bad_input(self):
        with mock.patch.object(display, "ask", return_value="not a subnet"):
            self.assertIsNone(app.subnet_calculator())

    def test_every_menu_number_works(self):
        menu_keys = {key for key, _, _ in display.MENU}
        self.assertEqual(menu_keys, set(app.ACTIONS) | {"0", "4"})


class EndToEndTests(unittest.TestCase):
    """Runs `python app.py` for real, typing menu choices into it like a user would."""

    def test_offline_session(self):
        keystrokes = "\n".join([
            "3", "8.8.8.8",            # analyze an address
            "5", "192.168.1.0/24",     # subnet calculator
            "9",                       # invalid menu choice
            "0",                       # exit
        ]) + "\n"
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        run = subprocess.run([sys.executable, "app.py"], cwd=ROOT, input=keystrokes,
                             capture_output=True, text=True, encoding="utf-8",
                             env=env, timeout=60)
        self.assertEqual(run.returncode, 0, run.stderr)
        out = run.stdout
        self.assertIn("IPeek-a-Boo", out)               # banner
        self.assertIn("Public", out)                    # 8.8.8.8 analysis
        self.assertIn("192.168.1.255", out)             # broadcast from the calculator
        self.assertIn("Please choose one of the numbers", out)
        self.assertIn("Bye!", out)


if __name__ == "__main__":
    unittest.main()
