"""'Where am I?' map links built from the latitude/longitude an API returned.

Nothing here touches the network: the links are only built, and the user opens
them in a browser. IP geolocation is approximate (usually the ISP's city), so
the pin shows the area, not the exact building.
"""

GOOGLE_MAPS = "https://www.google.com/maps/search/?api=1&query={lat},{lon}"
OPENSTREETMAP = "https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}"


def _coordinate(value, limit):
    """Return `value` as a float within +/- limit, or None if it is missing or invalid."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not -limit <= number <= limit:
        return None
    return number


def map_links(details):
    """Return {"Google Maps": url, "OpenStreetMap": url} for a details dict, or None.

    `details` is the standard dict from api.get_ip_details(); only its
    "latitude" and "longitude" are used. Returns None when there are no usable
    coordinates (missing, not a number, or out of range).
    """
    lat = _coordinate(details.get("latitude"), 90)
    lon = _coordinate(details.get("longitude"), 180)
    if lat is None or lon is None:
        return None
    # 4 decimal places is about 11 m - far more precise than IP geolocation anyway.
    lat, lon = f"{lat:.4f}", f"{lon:.4f}"
    return {
        "Google Maps": GOOGLE_MAPS.format(lat=lat, lon=lon),
        "OpenStreetMap": OPENSTREETMAP.format(lat=lat, lon=lon),
    }
