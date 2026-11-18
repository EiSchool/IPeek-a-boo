"""ipinfo - the building blocks of IPeek-a-Boo, an IP address information tool
by team We Don't Byte.

Modules
-------
api       Calls the public REST APIs (ipify, ipapi.co, ip-api.com).
analysis  Offline facts about an address using Python's `ipaddress` module.
display   Everything the user sees: banner, menu, colored tables, prompts.
export    Saves results to JSON or CSV files.
maps      Builds "Where am I?" Google Maps / OpenStreetMap links.
history   Remembers the last public IP for the "Your IP changed!" alert.

`app.py` in the project root ties these together into the menu program.
"""

__version__ = "1.1.0"
