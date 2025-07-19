import piexif
from PIL import Image
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def get_coordinates(exif_data):
    gps_info = exif_data.get("GPS", {})
    if not gps_info:
        return None

    def convert_to_degrees(value):
        d, m, s = value
        return d[0] / d[1] + m[0] / m[1] / 60 + s[0] / s[1] / 3600

    try:
        lat = convert_to_degrees(gps_info[2])
        if gps_info[1] == b"S":
            lat = -lat

        lon = convert_to_degrees(gps_info[4])
        if gps_info[3] == b"W":
            lon = -lon

        return lat, lon
    except Exception:
        return None


def get_location_from_image(image_path):
    try:
        image = Image.open(image_path)
        exif_bytes = image.info.get("exif", b"")
        exif_data = piexif.load(exif_bytes)
        coords = get_coordinates(exif_data)
        if not coords:
            return None

        geolocator = Nominatim(user_agent="plant_tracker")
        location = geolocator.reverse(coords, language="en", exactly_one=True)
        if not location:
            return None

        address = location.raw.get("address", {})

        print("➡️ city:", address.get("city"))
        print("➡️ town:", address.get("town"))
        print("➡️ village:", address.get("village"))
        print("➡️ municipality:", address.get("municipality"))

        print("➡️ state:", address.get("state"))
        print("➡️ region:", address.get("region"))
        print("➡️ province:", address.get("province"))
        print("➡️ state_district:", address.get("state_district"))
        print("➡️ county:", address.get("county"))

        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
        )
        state = (
            address.get("state")
            or address.get("region")
            or address.get("province")
            or address.get("state_district")
            or address.get("county")
        )
        country = address.get("country")

        full = location.address
        print("📍 Full location address:", full)
        if "Tokyo" in full and (not state or "Tokyo" not in state):
            state = "Tokyo"
        if "Vancouver" in full and (not city or "Vancouver" not in city):
            city = "Vancouver"
        if state:
            state = (
                state.replace(" Prefecture", "")
                .replace(" Metropolis", "")
                .replace(" City", "")
            )

        parts = [part for part in [city, state, country] if part]
        return ", ".join(parts)

    except GeocoderTimedOut:
        print("📍 Geocoder timed out")
        return None
    except Exception as e:
        print("📍 EXIF location error:", e)
        return None
