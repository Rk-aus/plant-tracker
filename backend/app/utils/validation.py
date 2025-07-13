from datetime import datetime
from flask import jsonify


def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



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
