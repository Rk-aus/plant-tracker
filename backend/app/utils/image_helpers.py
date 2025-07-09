import os
from werkzeug.utils import secure_filename
from flask import current_app

def save_uploaded_image(image):
    if image and image.filename:
        filename = secure_filename(image.filename)
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image.save(save_path)
        return filename
    return None
