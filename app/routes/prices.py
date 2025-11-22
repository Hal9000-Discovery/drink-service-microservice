# app/routes/prices.py

from flask import Blueprint, jsonify, request
from app.models import db, Price, Drink
from decimal import Decimal
from datetime import datetime

prices_bp = Blueprint("prices", __name__)


@prices_bp.route("/prices", methods=["GET"])
def get_prices():
    """
    Retrieves all prices.
    """
    prices = Price.query.all()
    results = [
        {
            "price_id": p.price_id,
            "drink_id": p.drink_id,
            "price_amount": str(p.price_amount),
            "effective_date": p.effective_date.isoformat(),
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "created_at": p.created_at.isoformat()
        }
        for p in prices
    ]
    return jsonify({"prices": results}), 200


@prices_bp.route("/prices/<int:price_id>", methods=["GET"])
def get_price(price_id):
    """
    Retrieves a specific price by its ID.
    """
    price = Price.query.get(price_id)
    if not price:
        return jsonify({"message": f"Price with ID {price_id} not found"}), 404

    return jsonify({
        "price_id": price.price_id,
        "drink_id": price.drink_id,
        "price_amount": str(price.price_amount),
        "effective_date": price.effective_date.isoformat(),
        "end_date": price.end_date.isoformat() if price.end_date else None,
        "created_at": price.created_at.isoformat()
    }), 200


@prices_bp.route("/prices", methods=["POST"])
def add_price():
    """
    Adds a new price record for an existing drink.
    """
    data = request.get_json()
    if not data:
        return jsonify({"message": "Request must contain JSON"}), 400

    required_fields = ["drink_id", "price_amount", "effective_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field '{field}'"}), 400

    try:
        drink_id = data["drink_id"]
        price_amount = Decimal(str(data["price_amount"]))
        effective_date = datetime.strptime(data["effective_date"], "%Y-%m-%d").date()
        end_date = (
            datetime.strptime(data["end_date"], "%Y-%m-%d").date()
            if "end_date" in data and data["end_date"]
            else None
        )
    except Exception as e:
        return jsonify({"message": f"Invalid data format: {e}"}), 400

    # Validate foreign key
    drink = Drink.query.get(drink_id)
    if not drink:
        return jsonify({"message": f"Drink with ID {drink_id} not found"}), 404

    price = Price(
        drink_id=drink_id,
        price_amount=price_amount,
        effective_date=effective_date,
        end_date=end_date
    )

    db.session.add(price)
    db.session.commit()

    return jsonify({
        "price_id": price.price_id,
        "drink_id": price.drink_id,
        "price_amount": str(price.price_amount),
        "effective_date": price.effective_date.isoformat(),
        "end_date": price.end_date.isoformat() if price.end_date else None,
        "created_at": price.created_at.isoformat()
    }), 201
