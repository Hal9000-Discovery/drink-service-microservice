# The heart of your micrioservice application
# The heart of your microservice application
# It creates the Flask app, loads configuration, initializes SQl Alchemy, and registers API routes.

# Creates Flask app + initializes db

# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import get_config

# Initialize the database (will be bound to app later)
db = SQLAlchemy()


def create_app():
    """
    Application factory — creates and configures the Flask app instance.
    This ensures the app can be easily reused for tests, Docker, or local dev.
    """
    app = Flask(__name__)

    # -----------------------------
    # 1. Load configuration dynamically
    # -----------------------------
    config_class = get_config()
    app.config.from_object(config_class)

    # -----------------------------
    # 2. Initialize database
    # -----------------------------
    db.init_app(app)

    # -----------------------------
    # 3. Register blueprints (routes)
    # -----------------------------
    from app.routes.health import health_bp
    from app.routes.drinks import drinks_bp
    from app.routes.prices import prices_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(drinks_bp)
    app.register_blueprint(prices_bp)

    # -----------------------------
    # 4. Root route (optional)
    # -----------------------------
    @app.route("/")
    def home():
        return {
            "service": "drink-service",
            "message": "Welcome to the Drink Service API!",
            "status": "running"
        }, 200

    return app
