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


def parse_network(text):
    """Turn user input into an IPv4Network / IPv6Network object.

    Accepts CIDR ("192.168.1.10/24"), a dotted mask ("192.168.1.10 255.255.255.0"
    or "192.168.1.10/255.255.255.0") or a bare address (treated as one host).
    Host bits are allowed: 192.168.1.10/24 means "the /24 that .10 lives in".
    Raises ValueError with a friendly message if the text is not valid.
    """
    cleaned = "/".join(text.split())  # "10.0.0.1 255.0.0.0" -> "10.0.0.1/255.0.0.0"
    try:
        return ipaddress.ip_network(cleaned, strict=False)
    except ValueError:
        raise ValueError(
            f"'{text.strip()}' is not a valid network - try 192.168.1.0/24, "
            "10.0.0.1 255.0.0.0 or 2001:db8::/64"
        ) from None


def subnet_info(net):
    """Return a dict of subnet facts (mask, range, host count...) for a network.

    Host counts are calculated, never listed, so even a huge /8 or IPv6 /64 is instant.
    IPv4 /31 (point-to-point links, RFC 3021) and /32 (a single host) have no
    separate network/broadcast address, so every address in them is usable.
    """
    info = {
        "Network": str(net),
        "Version": f"IPv{net.version}",
        "Prefix length": f"/{net.prefixlen}",
        "Type": address_type(net.network_address),
        "Network address": str(net.network_address),
    }
    total = net.num_addresses

    if net.version == 4:
        info["Subnet mask"] = str(net.netmask)
        info["Wildcard mask"] = str(net.hostmask)
        if net.prefixlen <= 30:
            info["Broadcast address"] = str(net.broadcast_address)
            first, last, usable = net.network_address + 1, net.broadcast_address - 1, total - 2
        else:  # /31 and /32
            info["Broadcast address"] = "None (/31 and /32 have no broadcast)"
            first, last, usable = net.network_address, net.broadcast_address, total
        info["First usable host"] = str(first)
        info["Last usable host"] = str(last)
        info["Usable hosts"] = f"{usable:,}"
    else:
        # IPv6 has no broadcast; every address in the prefix can be assigned.
        info["First address"] = str(net.network_address)
        info["Last address"] = str(net.broadcast_address)

    info["Total addresses"] = f"{total:,}"
    return info
