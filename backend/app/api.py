import os
from flask import Flask
from flask_cors import CORS
import logging
from app.routes.plants import plants_bp
from app.routes.uploads import uploads_bp

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "uploads")
)

app.register_blueprint(plants_bp)
app.register_blueprint(uploads_bp)

CORS(app)

if __name__ == "__main__":
    app.run(debug=True)
