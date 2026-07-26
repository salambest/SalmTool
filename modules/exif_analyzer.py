"""
EXIF Analyzer module.

Extracts metadata (camera model, capture date, GPS coordinates, and the
full raw EXIF tag set) from an image, and provides a helper to strip all
metadata by re-saving a clean copy of the image.
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def _convert_to_degrees(value):
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)


def _get_gps_coords(gps_info):
    if not gps_info:
        return None
    try:
        lat = _convert_to_degrees(gps_info["GPSLatitude"])
        if gps_info.get("GPSLatitudeRef") == "S":
            lat = -lat
        lon = _convert_to_degrees(gps_info["GPSLongitude"])
        if gps_info.get("GPSLongitudeRef") == "W":
            lon = -lon
        return {"latitude": lat, "longitude": lon}
    except Exception:
        return None


def extract_exif(image_path):
    result = {"camera_model": None, "date_taken": None, "gps": None, "raw": {}}
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return result

        tags = {}
        gps_info = {}
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == "GPSInfo":
                for gps_id, gps_val in value.items():
                    gps_info[GPSTAGS.get(gps_id, gps_id)] = gps_val
            else:
                tags[tag_name] = value

        result["raw"] = {str(k): str(v) for k, v in tags.items()}
        result["camera_model"] = tags.get("Model")
        result["date_taken"] = tags.get("DateTimeOriginal") or tags.get("DateTime")
        result["gps"] = _get_gps_coords(gps_info)
    except Exception as e:
        result["error"] = str(e)
    return result


def strip_metadata(image_path, output_path):
    """Re-saves the image without any EXIF metadata by copying only raw
    pixel data into a brand new image object."""
    try:
        img = Image.open(image_path)
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)
        clean_img.save(output_path)
        return True
    except Exception:
        return False
