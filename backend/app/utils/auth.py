from functools import wraps
from flask import request, jsonify, current_app


def require_api_key(func=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get("x-api-key")
            if api_key != current_app.config.get("API_KEY"):
                return jsonify({"error": "Invalid or missing API key"}), 401
            return f(*args, **kwargs)

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator
