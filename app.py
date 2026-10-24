"""IPeek-a-Boo ("I see your IP!") - DEVASC Project Activity 3 (Option 2).
Team We Don't Byte: Tinio, Cabuhat, Carpio, Vidal.

A menu-driven program that shows network technicians this computer's public
IPv4/IPv6 address plus its geolocation, ISP and ASN, checks whether an IP is
"hiding" behind a VPN/proxy (the Peek-a-Boo check), and lets them look up or
analyze any other IP address.

Run:   python app.py
Tests: python -m unittest

Each menu action returns a "result" dict (section -> fields) that the user can
save with option 4. See README.md for the full design and how to extend it.
"""

from ipinfo import analysis, api, display, export


def fetch_details(ip=None):
    """Look up and display location/ISP/ASN for `ip`. Returns the details or None."""
    with display.console.status("Looking up location and provider..."):
        try:
            details = api.get_ip_details(ip)
        except api.LookupFailed as err:
            display.show_error(str(err))
            return None
    display.show_table("Location & provider", details)
    return details


def fetch_privacy(ip):
    """Run the Peek-a-Boo check on `ip`. Returns the flags or None.

    This is a bonus section, so a failure is shown as a note, not an error.
    """
    with display.console.status("Playing peek-a-boo..."):
        try:
            flags = api.get_privacy_check(ip)
        except api.LookupFailed as err:
            display.show_info(f"Peek-a-Boo check skipped: {err}")
            return None
    display.show_table("Peek-a-Boo check", flags)
    display.show_peekaboo_verdict(flags)
    return flags


def my_public_ip():
    """Menu 1: show this computer's public IPv4 / IPv6 and where it is."""
    with display.console.status("Finding your public IP addresses..."):
        try:
            ipv4 = api.get_public_ipv4()
        except api.LookupFailed as err:
            display.show_error(str(err))
            return None
        ipv6 = api.get_public_ipv6()

    addresses = {
        "IPv4": ipv4,
        "IPv6": ipv6 or "Not available (this network has no IPv6)",
    }
    display.show_table("Your public addresses", addresses)
    results = {"Public addresses": addresses}

    details = fetch_details(ipv4)
    if details:
        results["Location & provider"] = details
    flags = fetch_privacy(ipv4)
    if flags:
        results["Peek-a-Boo check"] = flags
    return results


def lookup_ip():
    """Menu 2: analyze any IP the user types in, and geolocate it if it is public."""
    try:
        addr = analysis.parse_ip(display.ask("Enter an IPv4 or IPv6 address"))
    except ValueError as err:
        display.show_error(str(err))
        return None

    facts = analysis.analyze(addr)
    display.show_table("Address facts", facts)
    results = {"Address facts": facts}

    # Private/reserved addresses are not on the internet, so the APIs know nothing about them.
    if not addr.is_global:
        display.show_info("This is not a public address, so it has no geolocation or ISP.")
        return results

    details = fetch_details(str(addr))
    if details:
        results["Location & provider"] = details
    flags = fetch_privacy(str(addr))
    if flags:
        results["Peek-a-Boo check"] = flags
    return results


def analyze_offline():
    """Menu 3: show address facts only - no internet needed."""
    try:
        addr = analysis.parse_ip(display.ask("Enter an IPv4 or IPv6 address"))
    except ValueError as err:
        display.show_error(str(err))
        return None
    facts = analysis.analyze(addr)
    display.show_table("Address facts", facts)
    return {"Address facts": facts}


def save_last(last_result):
    """Menu 4: save the most recent result to exports/."""
    if not last_result:
        display.show_info("Nothing to save yet - run option 1, 2 or 3 first.")
        return
    fmt = display.ask("File format", choices=list(export.FORMATS), default="json")
    path = export.save_results(last_result, fmt)
    display.show_success(f"Saved to {path}")


# Menu number -> function. Add new features here (and to display.MENU).
ACTIONS = {
    "1": my_public_ip,
    "2": lookup_ip,
    "3": analyze_offline,
}


def main():
    display.show_banner()
    last_result = None
    while True:
        display.show_menu()
        choice = display.ask("Choose an option").strip().lower()
        if choice in ("0", "q", "quit", "exit"):
            break
        if choice == "4":
            save_last(last_result)
            continue
        action = ACTIONS.get(choice)
        if action is None:
            display.show_error("Please choose one of the numbers in the menu.")
            continue
        result = action()
        if result:
            last_result = result
    display.console.print("[cyan]Bye! We'll stop peeking now.[/]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye! We'll stop peeking now.")
