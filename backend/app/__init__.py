import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.routes.plants import plants_bp
from app.routes.uploads import uploads_bp

logging.basicConfig(level=logging.DEBUG)

def create_app():
    env = os.getenv("ENV", "development")

    dotenv_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", f".env{'.test' if env == 'test' else ''}")
    )
    load_dotenv(dotenv_path=dotenv_path, override=True)

    app = Flask(__name__)

    app.config["ENVIRONMENT"] = env

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["DB_NAME"] = os.getenv("DB_NAME")
    app.config["API_KEY"] = os.getenv("API_KEY")  
    app.config["TESTING"] = env == "test"

    print("🧪 ENV =", app.config["ENVIRONMENT"])
    print("🌱 DB_NAME =", app.config["DB_NAME"])
    print("🔑 API_KEY =", app.config["API_KEY"])

    app.register_blueprint(plants_bp)
    app.register_blueprint(uploads_bp)

    CORS(app)
    return app
