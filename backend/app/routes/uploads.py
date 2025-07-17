import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    if image.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(image.filename)
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    image.save(save_path)
    print(f"Saving image to: {save_path}")

    return jsonify({"filename": filename})


@uploads_bp.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
