from flask import request, jsonify, current_app
from functools import wraps

def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        req_key = request.headers.get("x-api-key")
        expected_key = current_app.config.get("API_KEY")
        if not expected_key:
            return jsonify({"error": "Server misconfigured: API key not set"}), 500
        if not req_key:
            return jsonify({"error": "Missing API key"}), 401
        if req_key != expected_key:
            return jsonify({"error": "Invalid API key"}), 403
        return func(*args, **kwargs)
    return wrapper
