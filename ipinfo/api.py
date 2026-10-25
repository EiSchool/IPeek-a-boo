"""Calls to the public IP-information REST APIs.

APIs used (all free, none needs an API key):
  * ipify      https://www.ipify.org  -> this computer's public IPv4 / IPv6
  * ipapi.co   https://ipapi.co       -> geolocation, ISP, ASN   (primary)
  * ip-api.com https://ip-api.com     -> geolocation, ISP, ASN   (fallback)
                                      -> VPN/proxy, hosting, mobile flags (Peek-a-Boo check)

Every public function returns plain Python data (str / dict / None) or raises
LookupFailed, so the rest of the program never handles `requests` errors.

To add another geolocation API: write a `_from_<name>()` function that turns
its JSON into the standard dict below, then add it to GEO_PROVIDERS.
"""

import requests

TIMEOUT = 5  # seconds to wait for any API before giving up
HEADERS = {"User-Agent": "ipeekaboo-devasc-project/1.0"}  # ipapi.co rejects blank agents

IPV4_URL = "https://api.ipify.org?format=json"
IPV6_URL = "https://api6.ipify.org?format=json"  # only answers over IPv6


class LookupFailed(Exception):
    """Raised when an API cannot give us an answer (offline, rate limit, bad IP...)."""


def _get_json(url):
    """GET a URL and return the decoded JSON body, or raise LookupFailed."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except requests.exceptions.Timeout as err:
        raise LookupFailed(f"Timed out after {TIMEOUT}s waiting for {url}") from err
    except requests.exceptions.RequestException as err:
        raise LookupFailed(f"Could not reach {url} (check your internet connection)") from err

    if resp.status_code == 429:
        raise LookupFailed("Rate limit reached - wait a minute and try again")
    if resp.status_code != 200:
        raise LookupFailed(f"{url} returned HTTP {resp.status_code}")

    try:
        return resp.json()
    except ValueError as err:
        raise LookupFailed(f"{url} did not return valid JSON") from err


# --------------------------------------------------------------------------
# Public IP address (ipify)
# --------------------------------------------------------------------------

def get_public_ipv4():
    """Return this computer's public IPv4 address as a string."""
    return _get_json(IPV4_URL)["ip"]


def get_public_ipv6():
    """Return this computer's public IPv6 address, or None if the network has no IPv6.

    api6.ipify.org can only be reached over IPv6, so any connection error
    here simply means "no IPv6" rather than a real failure.
    """
    try:
        return _get_json(IPV6_URL)["ip"]
    except LookupFailed:
        return None


# --------------------------------------------------------------------------
# Geolocation / ISP / ASN
#
# Each provider's JSON is converted to this standard dict so the display and
# export code only ever deals with one shape:
#   ip, city, region, country, country_code, postal, latitude, longitude,
#   timezone, isp, asn, source
# --------------------------------------------------------------------------

def _ipapi_co_url(ip):
    # https://ipapi.co/json/ = caller's own IP, https://ipapi.co/8.8.8.8/json/ = that IP
    return f"https://ipapi.co/{ip}/json/" if ip else "https://ipapi.co/json/"


def _from_ipapi_co(data):
    """Convert an ipapi.co response to the standard dict."""
    if data.get("error"):
        raise LookupFailed(f"ipapi.co: {data.get('reason', 'unknown error')}")
    return {
        "ip": data.get("ip"),
        "city": data.get("city"),
        "region": data.get("region"),
        "country": data.get("country_name"),
        "country_code": data.get("country_code"),
        "postal": data.get("postal"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
        "timezone": data.get("timezone"),
        "isp": data.get("org"),
        "asn": data.get("asn"),
        "source": "ipapi.co",
    }


def _ip_api_com_url(ip):
    # The free tier of ip-api.com is HTTP only (HTTPS needs a paid key).
    return f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"


def _from_ip_api_com(data):
    """Convert an ip-api.com response to the standard dict."""
    if data.get("status") != "success":
        raise LookupFailed(f"ip-api.com: {data.get('message', 'unknown error')}")
    # "as" looks like "AS15169 Google LLC" - keep just the AS number.
    asn = (data.get("as") or "").split(" ")[0] or None
    return {
        "ip": data.get("query"),
        "city": data.get("city"),
        "region": data.get("regionName"),
        "country": data.get("country"),
        "country_code": data.get("countryCode"),
        "postal": data.get("zip"),
        "latitude": data.get("lat"),
        "longitude": data.get("lon"),
        "timezone": data.get("timezone"),
        "isp": data.get("isp"),
        "asn": asn,
        "source": "ip-api.com",
    }


# Tried in order; the first provider that answers wins.
GEO_PROVIDERS = [
    (_ipapi_co_url, _from_ipapi_co),
    (_ip_api_com_url, _from_ip_api_com),
]


def get_ip_details(ip=None):
    """Return location/ISP/ASN details for `ip` (or this computer if ip is None).

    Falls back to the next provider if one is down or rate limited.
    Raises LookupFailed only if every provider fails.
    """
    errors = []
    for build_url, parse in GEO_PROVIDERS:
        try:
            return parse(_get_json(build_url(ip)))
        except LookupFailed as err:
            errors.append(str(err))
    raise LookupFailed(" | ".join(errors))


# --------------------------------------------------------------------------
# Peek-a-Boo check: is this IP "hiding"?
# --------------------------------------------------------------------------

PRIVACY_URL = "http://ip-api.com/json/{ip}?fields=status,message,mobile,proxy,hosting"


def get_privacy_check(ip):
    """Return True/False flags saying whether `ip` is a VPN/proxy, data center or mobile network.

    Uses ip-api.com's free `proxy`, `hosting` and `mobile` fields.
    """
    data = _get_json(PRIVACY_URL.format(ip=ip))
    if data.get("status") != "success":
        raise LookupFailed(f"ip-api.com: {data.get('message', 'unknown error')}")
    return {
        "VPN / proxy / Tor": bool(data.get("proxy")),
        "Hosting / data center": bool(data.get("hosting")),
        "Mobile network": bool(data.get("mobile")),
    }
