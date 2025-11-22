# tests/conftest.py

import os
import sys
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright

# ------------------------------------------------------------
# Ensure project root is added to PYTHONPATH so that:
#   from app import create_app, db
# works correctly when pytest runs inside /tests
# ------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import create_app, db  # noqa: E402


# ============================================================
# ENVIRONMENT CONFIGURATION (MATCHES main.py)
# ------------------------------------------------------------
# Your app uses FLASK_CONFIG values:
#   - development → 5001
#   - testing     → 5002
#   - production  → 5003
#
# PyTest will read FLASK_CONFIG and map to the correct port.
# ============================================================

ENV_TO_PORT = {
    "development": 5001,
    "testing": 5002,
    "production": 5003
}


@pytest.fixture(scope="session")
def flask_env():
    """
    Read the FLASK_CONFIG environment variable used by your service.
    If missing, default to 'development'.
    """
    return os.getenv("FLASK_CONFIG", "development").lower()


@pytest.fixture(scope="session")
def base_url(flask_env):
    """
    Build the base URL based on FLASK_CONFIG.

    Examples:
        FLASK_CONFIG=testing     → http://localhost:5002
        FLASK_CONFIG=production  → http://localhost:5003
    """
    port = ENV_TO_PORT.get(flask_env, 5001)  # fallback to development
    return f"http://localhost:{port}"


# ============================================================
# FLASK + DATABASE FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def app(flask_env):
    """
    Create and configure the Flask app for internal testing.
    Rarely used for external API tests (Requests/Playwright).
    """
    os.environ["FLASK_CONFIG"] = flask_env

    flask_app = create_app()

    with flask_app.app_context():
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    """
    Flask internal test client.
    Only used for direct Flask route testing, not HTTP API testing.
    """
    return app.test_client()


# ============================================================
# PLAYWRIGHT API CONTEXT (Optional)
# ============================================================

@pytest.fixture(scope="session")
def api_context(base_url):
    """
    Create a Playwright API request context for API testing.

    Example:
        response = api_context.get("/drinks")
    """
    with sync_playwright() as p:
        context = p.request.new_context(base_url=base_url)
        yield context
        context.dispose()
