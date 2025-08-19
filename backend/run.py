import os
from app.api import app
from app.db.connections import init_connection_pool
from app.services.plant_service import PlantService

init_connection_pool(minconn=1, maxconn=10)

plant_service = PlantService()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
