# app/routes/drinks.py

from flask import Blueprint, jsonify, request
from app.models import db, Drink

# Define the Blueprint for drinks endpoints
drinks_bp = Blueprint("drinks", __name__)

@drinks_bp.route("/drinks", methods=["GET"])
def get_drinks():
    """
    Retrieves all drinks from the database.
    """
    drinks = Drink.query.all()
    results = [
        {"id": d.id, "name": d.name, "description": d.description}
        for d in drinks
    ]
    return jsonify(results), 200


@drinks_bp.route("/drinks/<int:drink_id>", methods=["GET"])
def get_drink_by_id(drink_id):
    """
    Retrieves a single drink by ID.
    """
    drink = Drink.query.get(drink_id)
    if not drink:
        return jsonify({"message": f"Drink with ID {drink_id} not found"}), 404
    return jsonify({
        "id": drink.id,
        "name": drink.name,
        "description": drink.description
    }), 200


@drinks_bp.route("/drinks", methods=["POST"])
def add_drink():
    from flask import jsonify, request
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"message": "Missing required field 'name'"}), 400

    name = data["name"]
    description = data.get("description", "")

    # Check for duplicate BEFORE inserting
    existing = Drink.query.filter_by(name=name).first()
    if existing:
        return jsonify({
            "message": f"Drink with name '{name}' already exists.",
            "drink_id": existing.id
        }), 409  # Conflict

    try:
        drink = Drink(name=name, description=description)
        db.session.add(drink)
        db.session.commit()

        return jsonify({
            "id": drink.id,
            "name": drink.name,
            "description": drink.description
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Unexpected database error", "error": str(e)}), 500

