from datetime import datetime
from flask import jsonify


def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def get_validated_date(date_str):
    parsed_date = parse_date(date_str)
    if date_str and parsed_date is None:
        return None, jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    return parsed_date, None, None
