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
    if env == "test":
        load_dotenv(
            dotenv_path=os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", ".env.test")
            ),
            override=True,
        )
    else:
        load_dotenv(
            dotenv_path=os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", ".env")
            ),
            override=True,
        )

    print("🧪 ENV =", os.getenv("ENV"))
    print("🌱 DB_NAME =", os.getenv("DB_NAME"))

    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads")
    )

    app.register_blueprint(plants_bp)
    app.register_blueprint(uploads_bp)

    CORS(app)
    return app
