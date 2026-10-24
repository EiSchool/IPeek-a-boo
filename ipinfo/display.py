"""Everything the user sees: banner, menu, colored tables, prompts and messages.

Uses the `rich` library for colors and tables. Keeping all output here means
the look of the app can change without touching the API or analysis code.
"""

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

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
    ("1", "Show my public IP information"),
    ("2", "Look up any IP address"),
    ("3", "Analyze an IP address (offline)"),
    ("4", "Save last result to a file"),
    ("0", "Exit"),
]


def show_banner():
    console.print(Panel.fit(
        "[bold cyan]IPeek-a-Boo[/]  [italic]I see your IP![/]\n"
        "[dim]Public IPv4 / IPv6 - Geolocation - ISP - ASN[/]\n"
        "[dim]by team We Don't Byte[/]",
        border_style="cyan",
    ))


def show_menu():
    console.print()
    for key, text in MENU:
        console.print(f"  [bold yellow]{key}[/]  {text}")
    console.print()


def show_table(title, fields):
    """Print a two-column table of field -> value. Missing values show as n/a."""
    table = Table(title=title, title_style="bold magenta", show_header=True,
                  header_style="bold cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value", style="green", overflow="fold")  # wrap long values
    for key, value in fields.items():
        label = LABELS.get(key, key)
        if isinstance(value, bool):
            shown = "[bold yellow]Yes[/]" if value else "No"
        elif value in (None, ""):
            shown = "[dim]n/a[/]"
        else:
            shown = escape(str(value))
        table.add_row(label, shown)
    console.print(table)


def show_peekaboo_verdict(flags):
    """Print a fun one-line verdict for the flags from api.get_privacy_check()."""
    if flags["VPN / proxy / Tor"]:
        console.print("[bold yellow]Peek-a-boo... we still see you![/] "
                      "ip-api.com lists this IP as a VPN, proxy or Tor exit.")
    if flags["Hosting / data center"]:
        console.print("[yellow]This IP lives in a data center (cloud/hosting), "
                      "not a home or office.[/]")
    if flags["Mobile network"]:
        console.print("[yellow]This IP comes from a mobile/cellular network.[/]")
    if not any(flags.values()):
        console.print("[green]Nothing hiding here - looks like a regular "
                      "home/office connection.[/]")


def ask(question, choices=None, default=None):
    """Ask the user for input. With `choices`, keeps asking until one is picked."""
    return Prompt.ask(f"[bold]{question}[/]", choices=choices, default=default)


def show_error(message):
    console.print(f"[bold red]Error:[/] {escape(message)}")


def show_info(message):
    console.print(f"[yellow]{escape(message)}[/]")


def show_success(message):
    console.print(f"[bold green]{escape(message)}[/]")
