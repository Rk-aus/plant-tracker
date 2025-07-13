from flask import Blueprint, request, jsonify, make_response, url_for
from app.utils.auth import require_api_key
from app.utils.validation import (
    get_validated_date,
    validate_required_image,
    validate_required_fields,
)
from app.utils.image_helpers import save_image_and_get_location

plants_bp = Blueprint("plants", __name__)
db = None


def init_db():
    global db
    if db is None:
        from app.plant_db_class import PlantDB

        db = PlantDB()


@plants_bp.route("/plants", methods=["POST"])
@require_api_key
def add_plant():
    init_db()
    if not request.content_type.startswith("multipart/form-data"):
        return jsonify({"error": "Content-Type must be multipart/form-data"}), 415

    data = request.form

    image = request.files.get("image")
    error_response, status_code = validate_required_image(image)
    if error_response:
        return error_response, status_code

    manual_location = data.get("location")
    image_path, location = save_image_and_get_location(image, manual_location)

    required_fields = [
        "plant_name_en",
        "plant_name_ja",
        "plant_class_en",
        "plant_class_ja",
    ]

    data, error_response, status_code = validate_required_fields(data, required_fields)
    if error_response:
        return error_response, status_code

    plant_name_en = data.get("plant_name_en").strip()
    plant_name_ja = data.get("plant_name_ja").strip()
    plant_class_en = data.get("plant_class_en").strip()
    plant_class_ja = data.get("plant_class_ja").strip()
    botanical_name = data.get("botanical_name", "").strip()
    plant_date_str = data.get("plant_date")

    plant_date, error_response, status_code = get_validated_date(plant_date_str)
    if error_response:
        return error_response, status_code

    try:
        db.insert_plant(
            plant_name_en,
            plant_class_en,
            plant_name_ja,
            plant_class_ja,
            image_path,
            botanical_name,
            location,
            plant_date,
        )
        db.conn.commit()
        return jsonify({"message": "Plant added"}), 201
    except Exception as e:
        db.conn.rollback()
        if "duplicate key value" in str(e):
            return jsonify({"error": "Duplicate plant name"}), 409
        return jsonify({"error": str(e)}), 400


@plants_bp.route("/plants/<int:plant_id>", methods=["PUT"])
@require_api_key
def update_plant(plant_id):
    init_db()

    if not request.content_type.startswith("multipart/form-data"):
        return jsonify({"error": "Content-Type must be multipart/form-data"}), 415

    data = request.form

    image = request.files.get("image")
    error_response, status_code = validate_required_image(image)
    if error_response:
        return error_response, status_code

    manual_location = data.get("location")
    image_path, location = save_image_and_get_location(image, manual_location)

    plant_name_en = data.get("plant_name_en").strip()
    plant_name_ja = data.get("plant_name_ja").strip()
    plant_class_en = data.get("plant_class_en").strip()
    plant_class_ja = data.get("plant_class_ja").strip()
    botanical_name = data.get("botanical_name", "").strip()

    plant_date_str = data.get("plant_date")
    plant_date, error_response, status_code = get_validated_date(plant_date_str)
    if error_response:
        return error_response, status_code

    try:
        db.update_plant(
            plant_id,
            plant_name_en,
            plant_class_en,
            plant_name_ja,
            plant_class_ja,
            image_path,
            botanical_name,
            location,
            plant_date,
        )
        db.conn.commit()
        response = make_response(jsonify({"message": f"Plant {plant_id} updated"}), 200)
        response.headers["Location"] = url_for("plants.get_plant", plant_id=plant_id)
        return response
    except Exception as e:
        db.conn.rollback()
        print("❌ Error updating plant:", e)
        return jsonify({"error": str(e)}), 400


@plants_bp.route("/plants/<int:plant_id>", methods=["DELETE"])
@require_api_key
def delete_plant(plant_id):
    init_db()
    try:
        db.delete_plant(plant_id)
        db.conn.commit()
        return ("", 204)
    except Exception as e:
        db.conn.rollback()
        print("❌ Error deleting plant:", e)
        return jsonify({"error": str(e)}), 400


@plants_bp.route("/plants", methods=["GET"])
def get_all_plants():
    init_db()
    plants = db.get_all_plants()
    print("🌱 Received GET:", plants)
    result = [
        {
            "plant_id": row[0],
            "plant_name_en": row[1],
            "plant_class_en": row[2],
            "plant_name_ja": row[3],
            "plant_class_ja": row[4],
            "image_path": row[5],
            "botanical_name": row[6],
            "location": row[7],
            "plant_date": row[8],
        }
        for row in plants
    ]
    return jsonify(result)


@plants_bp.route("/plants/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    init_db()
    plant = db.get_plant_details(plant_id)
    print("🌱 Received GET:", plant)
    if plant:
        return jsonify(
            {
                "plant_id": plant[0],
                "plant_name_en": plant[1],
                "plant_class_en": plant[2],
                "plant_name_ja": plant[3],
                "plant_class_ja": plant[4],
                "image_path": plant[5],
                "botanical_name": plant[6],
                "location": plant[7],
                "plant_date": plant[8],
            }
        )
    else:
        return jsonify({"error": "Plant not found"}), 404


@plants_bp.route("/plants/sort_by_date", methods=["GET"])
def get_plants_sorted_by_date():
    init_db()
    sorted_rows = db.list_plants_by_date()
    print("🌱 Received GET:", sorted_rows)
    formatted = [
        {
            "plant_id": row[0],
            "plant_name_en": row[1],
            "plant_class_en": row[2],
            "plant_name_ja": row[3],
            "plant_class_ja": row[4],
            "image_path": row[5],
            "botanical_name": row[6],
            "location": row[7],
            "plant_date": row[8],
        }
        for row in sorted_rows
    ]
    return jsonify(formatted)
