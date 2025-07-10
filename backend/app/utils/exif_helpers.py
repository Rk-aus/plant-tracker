import piexif
from PIL import Image
from geopy.geocoders import Nominatim


def get_coordinates(exif_data):
    gps_info = exif_data.get("GPS", {})
    if not gps_info:
        return None

    def convert_to_degrees(value):
        d, m, s = value
        return d[0] / d[1] + m[0] / m[1] / 60 + s[0] / s[1] / 3600

    try:
        lat = convert_to_degrees(gps_info[2])
        if gps_info[1] == b'S':
            lat = -lat

        lon = convert_to_degrees(gps_info[4])
        if gps_info[3] == b'W':
            lon = -lon

        return lat, lon
    except Exception:
        return None


def get_location_from_image(image_path):
    try:
        image = Image.open(image_path)
        exif_dict = piexif.load(image.info.get("exif", b""))
        coords = get_coordinates(exif_dict)
        if not coords:
            return None

        geolocator = Nominatim(user_agent="plant_tracker")
        location = geolocator.reverse(coords, language="en")
        return location.address if location else None
    except Exception as e:
        print("📍 EXIF location error:", e)
        return None
