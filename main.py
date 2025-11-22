"""
main.py — Entry point for the Drink Service microservice.

Responsibilities:
- Create the Flask app instance using the factory pattern.
- Initialize the database for the selected environment.
- Start the HTTP server on an environment-specific port.
    - Development → 5001
    - Testing → 5002
    - Production → 8000
- Provide a /debug/config endpoint for verification.

This file should NOT contain routes (those belong to blueprints).
"""

import os
from app import create_app, db
from app.models import Drink, Price   # Ensures models are registered with SQLAlchemy


# --------------------------------------------------------
# 1. Create Flask app through the factory pattern
# --------------------------------------------------------
# This loads:
# - config based on environment (dev/test/prod)
# - database setup
# - blueprints for routes
app = create_app()


# --------------------------------------------------------
# 2. Initialize database tables (only if they do not exist)
# --------------------------------------------------------
# This allows SQLite or SQL Server to create schemas automatically.
with app.app_context():
    db.create_all()


# --------------------------------------------------------
# 3. Debug route to confirm configuration at runtime
# --------------------------------------------------------
@app.route("/debug/config", methods=["GET"])
def show_config():
    """
    Returns runtime configuration values so you can confirm:
    - Which environment is active
    - Which database the app is using
    - Which port it should run on
    """
    from flask import jsonify

    return jsonify({
        "FLASK_CONFIG": os.getenv("FLASK_CONFIG"),
        "APP_ENV": app.config.get("APP_ENV", "unknown"),
        "SQLALCHEMY_DATABASE_URI": app.config.get("SQLALCHEMY_DATABASE_URI"),
        "DEBUG": app.config.get("DEBUG"),
    })


# --------------------------------------------------------
# 4. Determine correct port based on environment
# --------------------------------------------------------
def resolve_port():
    """
    Chooses the correct default port based on environment.

    Order of precedence:
    1. PORT environment variable (manual override)
    2. Environment-specific defaults:
        - development: 5001
        - testing:      5002
        - production:   8000
    """

    # If the user explicitly sets PORT, always use it
    if "PORT" in os.environ:
        return int(os.environ["PORT"])

    flask_env = os.getenv("FLASK_CONFIG", "").lower()

    if flask_env == "testing":
        return 5002
    if flask_env == "production":
        return 8000

    # Default fallback: development
    return 5001


# --------------------------------------------------------
# 5. Application entry point
# --------------------------------------------------------
if __name__ == "__main__":
    port = resolve_port()

    app.run(
        host="0.0.0.0",              # Required for Docker
        port=port,
        debug=app.config.get("DEBUG", False)
    )
