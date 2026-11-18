"""'Your IP changed!' alert: remember the last public IP and compare on the next run.

The last IPv4/IPv6 seen is kept in a small JSON file in the user's home folder
(not in the repository), so it survives between runs. A missing or damaged file
is simply treated as "first run" - this feature must never crash the app.
"""

import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".ipeekaboo_last_ip.json")


def load_last(path=None):
    """Return the last saved record {"IPv4", "IPv6", "Checked at"} or None."""
    path = path or HISTORY_FILE
    try:
        with open(path, encoding="utf-8") as f:
            record = json.load(f)
    except (OSError, ValueError):
        return None
    return record if isinstance(record, dict) else None


def check_and_record(ipv4, ipv6, path=None, now=None):
    """Compare the current IPs with the last saved ones, then save the current ones.

    Returns a dict ready to show in a table:
        "Status"      "First peek" | "Unchanged" | "CHANGED"
        "Changed"     which addresses changed, e.g. "IPv4" (only when CHANGED)
        "Previous …"  the old addresses and when they were seen (when known)
    """
    path = path or HISTORY_FILE
    now = now or datetime.now()
    previous = load_last(path)
    current = {"IPv4": ipv4, "IPv6": ipv6, "Checked at": now.strftime("%Y-%m-%d %H:%M:%S")}

    if previous is None:
        result = {"Status": "First peek"}
    else:
        changed = [key for key in ("IPv4", "IPv6") if previous.get(key) != current[key]]
        result = {"Status": "CHANGED" if changed else "Unchanged"}
        if changed:
            result["Changed"] = ", ".join(changed)
        result["Previous IPv4"] = previous.get("IPv4")
        result["Previous IPv6"] = previous.get("IPv6")
        result["Previous check"] = previous.get("Checked at")

    try:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
    except OSError:
        result["Note"] = "Could not save this IP for next time"
    return result
