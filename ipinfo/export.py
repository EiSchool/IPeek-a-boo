"""Save lookup results to JSON or CSV files.

A "result" is a dict of sections, each section a dict of field -> value, e.g.
    {"Public addresses": {"IPv4": "203.0.113.5", "IPv6": None},
     "Location & provider": {"city": "Manila", ...}}
"""

import csv
import json
import os
from datetime import datetime

EXPORT_DIR = "exports"
FORMATS = ("json", "csv")


def save_results(results, fmt="json", folder=EXPORT_DIR):
    """Write `results` to a timestamped file in `folder` and return its path."""
    if fmt not in FORMATS:
        raise ValueError(f"Unknown format '{fmt}', expected one of {FORMATS}")

    os.makedirs(folder, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(folder, f"ipeekaboo_{stamp}.{fmt}")

    if fmt == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
    else:
        # CSV is flat, so each row is one field: section, field, value.
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["section", "field", "value"])
            for section, fields in results.items():
                for field, value in fields.items():
                    writer.writerow([section, field, value])
    return path
