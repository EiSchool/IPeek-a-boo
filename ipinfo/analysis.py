"""Offline facts about an IP address, using Python's built-in `ipaddress` module.

Nothing here touches the network, so this works even without internet and
is the easiest part of the program to unit test (see tests/test_analysis.py).
"""

import ipaddress


def parse_ip(text):
    """Turn user input into an IPv4Address / IPv6Address object.

    Raises ValueError with a friendly message if the text is not a valid IP.
    """
    try:
        return ipaddress.ip_address(text.strip())
    except ValueError:
        raise ValueError(f"'{text.strip()}' is not a valid IPv4 or IPv6 address") from None


def ipv4_class(addr):
    """Return the classful network class (A-E) of an IPv4 address.

    Classes are obsolete for routing (CIDR replaced them) but technicians
    still use them as a quick description of an address.
    """
    first_octet = addr.packed[0]
    if first_octet < 128:
        return "A"
    if first_octet < 192:
        return "B"
    if first_octet < 224:
        return "C"
    if first_octet < 240:
        return "D (multicast)"
    return "E (experimental)"


def address_type(addr):
    """Describe what kind of address this is.

    Order matters: e.g. 127.0.0.1 is also "private" in Python's eyes, so the
    more specific checks come first.
    """
    if addr.is_loopback:
        return "Loopback"
    if addr.is_link_local:
        return "Link-local"
    if addr.is_multicast:
        return "Multicast"
    if addr.is_unspecified:
        return "Unspecified"
    if addr.is_private:
        return "Private"
    if addr.is_reserved:
        return "Reserved"
    if addr.is_global:
        return "Public"
    return "Special use (e.g. carrier-grade NAT)"


def analyze(addr):
    """Return a dict of facts about the address, ready to show in a table."""
    info = {
        "Address": str(addr),
        "Version": f"IPv{addr.version}",
        "Type": address_type(addr),
        "Reverse DNS name": addr.reverse_pointer,
    }
    if addr.version == 4:
        info["Class"] = ipv4_class(addr)
        info["Binary"] = ".".join(f"{octet:08b}" for octet in addr.packed)
        info["Integer"] = int(addr)
    else:
        info["Compressed"] = addr.compressed
        info["Exploded"] = addr.exploded
        if addr.ipv4_mapped:
            info["IPv4-mapped"] = str(addr.ipv4_mapped)
    return info
