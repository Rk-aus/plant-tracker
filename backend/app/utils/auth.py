import os
from flask import request, jsonify
from functools import wraps

def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if api_key != os.getenv("API_KEY"):
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper
