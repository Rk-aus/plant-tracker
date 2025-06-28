from flask import Flask
from routes.plants import plants_bp
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.register_blueprint(plants_bp)
CORS(app)  # Apply CORS to just this Blueprint

if __name__ == "__main__":
    app.run(debug=True)
