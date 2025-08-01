import os
from werkzeug.utils import secure_filename
from flask import current_app
from .exif_helpers import get_location_from_image


def save_uploaded_image(image):
    if image and image.filename:
        filename = secure_filename(image.filename)
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(save_path)
        return filename
    return None


def save_image_and_get_location(image, manual_location=None):
    image_path = save_uploaded_image(image)

    if manual_location:
        return image_path, manual_location

    if image_path:
        full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], image_path)
        extracted_location = get_location_from_image(full_path)
        return image_path, extracted_location

    return None, None
