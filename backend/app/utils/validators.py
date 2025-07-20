from datetime import date, datetime
from flask import jsonify
from app.exceptions import UniquePlantConstraintError, UniqueBotanicalNameError, UniqueImagePathError

def validate_positive_int(value, name):
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer.")

def validate_non_empty_str(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    
def validate_date_or_none(value, name="date"):
    if value is not None and not isinstance(value, date):
        raise ValueError(f"{name} must be a datetime.date object or None.")

def handle_unique_violation(e):
    error_msg = str(e)

    if "unique_botanical_name" in error_msg:
        raise UniqueBotanicalNameError("Botanical name already exists.") from e
    elif "unique_image_path" in error_msg:
        raise UniqueImagePathError("Image path already exists.") from e
    else:
        raise UniquePlantConstraintError("Unique constraint violation.") from e


def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_validated_date(date_str):
    parsed_date = parse_date(date_str)
    if date_str and parsed_date is None:
        return None, jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    return parsed_date, None, None

def validate_required_image(image):
    if not image or not image.filename.strip() or not allowed_file(image.filename):
        return jsonify({"error": "Image file is required."}), 400
    return None, None

def validate_required_fields(data, required_fields):
    missing = []
    for field in required_fields:
        value = data.get(field, "").strip()
        if not value:
            missing.append(field)

    if missing:
        return (
            None,
            jsonify({"error": f"Missing required fields: {', '.join(missing)}"}),
            400,
        )

    return data, None, None
