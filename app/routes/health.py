# app/routes/health.py

from flask import Blueprint, jsonify
from datetime import datetime

# Define the Blueprint for health endpoints
health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint — used by Docker, Kubernetes, or monitoring tools
    to verify that the microservice is running and responsive.
    """
    return jsonify({
        "service": "drink-service",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200
