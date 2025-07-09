from flask import Blueprint, request, jsonify
from app.plant_db_class import PlantDB
from app.utils.auth import require_api_key
from app.utils.image_helpers import save_uploaded_image
from app.utils.validation import get_validated_date

plants_bp = Blueprint("plants", __name__)
db = PlantDB()

@plants_bp.route("/plants", methods=["POST"])
def add_plant():
    require_api_key()
    if not request.content_type.startswith("multipart/form-data"):
        return jsonify({"error": "Content-Type must be multipart/form-data"}), 415

    data = request.form
    image = request.files.get("image")
    image_path = save_uploaded_image(image)

    plant_name_en = data.get("plant_name_en")
    plant_name_ja = data.get("plant_name_ja")
    plant_class_en = data.get("plant_class_en")
    plant_class_ja = data.get("plant_class_ja")
    botanical_name = data.get("botanical_name")
    location = data.get("location")
    plant_date_str = data.get("plant_date")
    plant_date, error_response, status_code = get_validated_date(plant_date_str)
    if error_response:
        return error_response, status_code

    if data.get("plant_date") and plant_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    try:
        db.insert_plant(
            plant_name_en,
            plant_class_en,
            plant_date,
            plant_name_ja,
            plant_class_ja,
            image_path,
            botanical_name,
            location,
        )
        db.conn.commit()
        return jsonify({"message": "Plant added"}), 201
    except Exception as e:
        db.conn.rollback()
        print("❌ Error adding plant:", e)
        return jsonify({"error": str(e)}), 400


@plants_bp.route("/plants/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
    require_api_key()
    try:
        db.delete_plant(plant_id)
        db.conn.commit()
        return jsonify({"message": f"Plant {plant_id} deleted"})
    except Exception as e:
        db.conn.rollback()
        print("❌ Error deleting plant:", e)
        return jsonify({"error": str(e)}), 400


@plants_bp.route("/plants/<int:plant_id>", methods=["PUT"])
def update_plant(plant_id):
    require_api_key()

    if not request.content_type.startswith("multipart/form-data"):
        return jsonify({"error": "Content-Type must be multipart/form-data"}), 415

    data = request.form
    image = request.files.get("image")
    image_path = save_uploaded_image(image)

    plant_name_en = data.get("plant_name_en")
    plant_name_ja = data.get("plant_name_ja")
    plant_class_en = data.get("plant_class_en")
    plant_class_ja = data.get("plant_class_ja")
    botanical_name = data.get("botanical_name")
    location = data.get("location")
    plant_date_str = data.get("plant_date")
    plant_date, error_response, status_code = get_validated_date(plant_date_str)
    if error_response:
        return error_response, status_code

    if data.get("plant_date") and plant_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    try:
        db.update_plant(
            plant_id,
            plant_name_en,
            plant_class_en,
            plant_date,
            plant_name_ja,
            plant_class_ja,
            image_path,
            botanical_name,
            location
        )
        db.conn.commit()
        return jsonify({"message": f"Plant {plant_id} updated"})
    except Exception as e:
        db.conn.rollback()
        print("❌ Error updating plant:", e)
        return jsonify({"error": str(e)}), 400


@plants_bp.route("/plants", methods=["GET"])
def get_all_plants():
    plants = db.get_all_plants()
    print("🌱 Received GET:", plants)
    result = [
        {
            "plant_id": row[0],
            "plant_name_en": row[1],
            "plant_class_en": row[2],
            "plant_date": row[3],
            "plant_name_ja": row[4],
            "plant_class_ja": row[5],
        }
        for row in plants
    ]
    return jsonify(result)


@plants_bp.route("/plants/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    plant = db.get_plant_details(plant_id)
    print("🌱 Received GET:", plant)
    if plant:
        return jsonify(
            {
                "plant_id": plant[0],
                "plant_name_en": plant[1],
                "plant_class_en": plant[2],
                "plant_date": plant[3],
                "plant_name_ja": plant[4],
                "plant_class_ja": plant[5],
            }
        )
    else:
        return jsonify({"error": "Plant not found"}), 404


@plants_bp.route("/plants/sort_by_date", methods=["GET"])
def get_plants_sorted_by_date():
    sorted_rows = db.list_plants_by_date()
    print("🌱 Received GET:", sorted_rows)
    formatted = [
        {
            "plant_id": row[0],
            "plant_name_en": row[1],
            "plant_class_en": row[2],
            "plant_date": row[3],
            "plant_name_ja": row[4],
            "plant_class_ja": row[5],
        }
        for row in sorted_rows
    ]
    return jsonify(formatted)
