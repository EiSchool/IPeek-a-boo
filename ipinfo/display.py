"""Everything the user sees: banner, menu, colored tables, prompts and messages.

Uses the `rich` library for colors and tables. Keeping all output here means
the look of the app can change without touching the API or analysis code.

Theme: Halloween. To re-skin the whole app, change only the five colors below.
"""

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# --- Halloween palette -------------------------------------------------------
PUMPKIN = "#ff7518"   # borders, titles, menu numbers
WITCH = "#b07cff"     # headers, info messages, spinners' text
SLIME = "#7fff00"     # values and success messages
BONE = "#f5f0e1"      # field names
BLOOD = "#ff2e2e"     # errors and "Yes" flags

PUMPKIN_ART = r"""      ,(
   .-'-'-.
  / /\ /\ \
 |    ^    |
  \ \/\/\/ /
   '-...-'"""

# Friendly names for the keys returned by api.get_ip_details().
LABELS = {
    "ip": "IP address",
    "city": "City",
    "region": "Region / State",
    "country": "Country",
    "country_code": "Country code",
    "postal": "Postal code",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "timezone": "Time zone",
    "isp": "ISP / Organization",
    "asn": "ASN",
    "source": "Data source",
}

MENU = [
    ("1", "Show my public IP information", "unmask yourself"),
    ("2", "Look up any IP address", "hunt a stranger"),
    ("3", "Analyze an IP address (offline)", "read its bones"),
    ("4", "Save last result to a file", "bury it in exports/"),
    ("0", "Exit", "flee into the night"),
]


def show_banner():
    console.print(Panel.fit(
        f"[{PUMPKIN}]{PUMPKIN_ART}[/]\n\n"
        f"[bold {PUMPKIN}]IPeek-a-Boo[/]  [italic {WITCH}]I see your IP![/]\n"
        f"[{BONE}]Public IPv4 / IPv6 - Geolocation - ISP - ASN[/]\n"
        f"[dim]by team We Don't Byte  -  Halloween edition[/]",
        border_style=PUMPKIN,
    ))


def show_menu():
    console.print()
    for key, text, hint in MENU:
        console.print(f"  [bold {PUMPKIN}]{key}[/]  [{BONE}]{text}[/]  [dim italic]({hint})[/]")
    console.print()


def status(message):
    """Spinner shown while waiting for an API, e.g. `with display.status("..."):`."""
    return console.status(f"[{WITCH}]{message}[/]", spinner_style=PUMPKIN)


def show_table(title, fields):
    """Print a two-column table of field -> value. Missing values show as n/a."""
    table = Table(title=title, title_style=f"bold {PUMPKIN}", border_style=PUMPKIN,
                  show_header=True, header_style=f"bold {WITCH}")
    table.add_column("Field", style=f"bold {BONE}")
    table.add_column("Value", style=SLIME, overflow="fold")  # wrap long values
    for key, value in fields.items():
        label = LABELS.get(key, key)
        if isinstance(value, bool):
            shown = f"[bold {BLOOD}]Yes[/]" if value else "No"
        elif value in (None, ""):
            shown = "[dim]n/a[/]"
        else:
            shown = escape(str(value))
        table.add_row(label, shown)
    console.print(table)


def show_peekaboo_verdict(flags):
    """Print a spooky one-line verdict for the flags from api.get_privacy_check()."""
    if flags["VPN / proxy / Tor"]:
        console.print(f"[bold {BLOOD}]BOO! Nice mask... but we still see you.[/] "
                      f"[{BONE}]ip-api.com lists this IP as a VPN, proxy or Tor exit.[/]")
    if flags["Hosting / data center"]:
        console.print(f"[{WITCH}]This IP haunts a data center (cloud/hosting), "
                      "not a home or office.[/]")
    if flags["Mobile network"]:
        console.print(f"[{WITCH}]This IP roams the night on a mobile/cellular network.[/]")
    if not any(flags.values()):
        console.print(f"[{SLIME}]No ghosts here - looks like a regular "
                      "home/office connection.[/]")


def ask(question, choices=None, default=None):
    """Ask the user for input. With `choices`, keeps asking until one is picked."""
    return Prompt.ask(f"[bold {PUMPKIN}]{question}[/]", choices=choices, default=default)


def show_error(message):
    console.print(f"[bold {BLOOD}]Eek![/] [{BONE}]{escape(message)}[/]")


def show_info(message):
    console.print(f"[{WITCH}]{escape(message)}[/]")


def show_success(message):
    console.print(f"[bold {SLIME}]{escape(message)}[/]")


def show_goodbye():
    console.print(f"[bold {PUMPKIN}]Bye! The ghosts will stop peeking now.[/]")
