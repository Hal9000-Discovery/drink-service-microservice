# app/models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db



# --------------------------
# Drink Model
# --------------------------
class Drink(db.Model):
    """
    Represents a drink item in the database.
    Each drink can have multiple price records (one-to-many relationship).
    """
    __tablename__ = "drink"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

    # Relationship to Price model (not a column in DB — just logical link)
    prices = db.relationship("Price", backref="drink", lazy=True)

    def __repr__(self):
        return f"<Drink {self.name}>"


# --------------------------
# Price Model
# --------------------------
class Price(db.Model):
    """
    Represents the price of a specific drink.
    A drink can have multiple prices over time (effective and end dates).
    """
    __tablename__ = "price"

    price_id = db.Column(db.Integer, primary_key=True)
    drink_id = db.Column(db.Integer, db.ForeignKey("drink.id"), nullable=False)

    price_amount = db.Column(db.Numeric(10, 2), nullable=False)
    effective_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Price {self.price_amount} for Drink {self.drink_id}>"
