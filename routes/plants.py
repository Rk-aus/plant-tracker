from flask import Blueprint, request, jsonify
from plant_db_class import PlantDB
from datetime import datetime

plants_bp = Blueprint("plants", __name__)
db = PlantDB()

# Helper function to parse date

def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None

@plants_bp.route("/plants", methods=["POST"])
def add_plant():
    data = request.json
    print("🌱 Received POST:", data)

    plant_name_en = data.get("plant_name_en")
    plant_name_ja = data.get("plant_name_ja")
    class_en = data.get("plant_class_en")
    class_ja = data.get("plant_class_ja")
    plant_date = parse_date(data.get("plant_date"))

    if data.get("plant_date") and plant_date is None:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    try:
        db.insert_plant(plant_name_en, plant_name_ja, class_en, class_ja, plant_date)
        db.conn.commit()
        return jsonify({"message": "Plant added"}), 201
    except Exception as e:
        db.conn.rollback()
        print("❌ Error adding plant:", e)
        return jsonify({"error": str(e)}), 400

@plants_bp.route("/plants/<int:plant_id>", methods=["DELETE"])
def delete_plant(plant_id):
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
    data = request.json
    try:
        db.update_plant(
            plant_id,
            data.get("plant_name_en"),
            data.get("plant_class_en"),
            parse_date(data.get("plant_date")),
            data.get("plant_name_ja"),
            data.get("plant_class_ja")
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
            "plant_class_ja": row[5]
        }
        for row in plants
    ]
    return jsonify(result)

@plants_bp.route("/plants/<int:plant_id>", methods=["GET"])
def get_plant(plant_id):
    plant = db.get_plant_details(plant_id)
    print("🌱 Received GET:", plant)
    if plant:
        return jsonify({
            "plant_id": plant[0],
            "plant_name_en": plant[1],
            "plant_class_en": plant[2],
            "plant_date": plant[3],
            "plant_name_ja": plant[4],
            "plant_class_ja": plant[5]
        })
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

