# config.py
import os

# ------------------------
# Base Configuration
# ------------------------
class Config:
    """Base configuration shared by all environments."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# ------------------------
# Development (Local)
# ------------------------
class DevelopmentConfig(Config):
    """Local development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_data.db'  # Uses local SQLite by default
    
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Git/drink-service/instance/data.db'

# ------------------------
# Production (Docker / Server)
# ------------------------
class ProductionConfig(Config):
    """Production or Docker environment configuration."""
    DEBUG = False  # Never enable debug in production!
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://flask_user:StrongPassword123@host.docker.internal,1433/DrinkServiceDB?'
        'driver=ODBC+Driver+17+for+SQL+Server'
    )


# ------------------------
# Testing Environment
# ------------------------
class TestingConfig(Config):
    """In-memory SQLite for fast test runs."""
    TESTING = True
    DEBUG = True
    # Use a temporary in-memory SQLite database for isolated test runs
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False





# ------------------------
# Environment Detection Logic
# ------------------------
def detect_environment() -> str:
    """
    Detects whether the app is running inside Docker, in development, or under testing.
    """
    # Allow explicit override (useful for CI/CD)
    if os.environ.get("APP_ENV"):
        return os.environ["APP_ENV"].lower()

    # Docker environment detection
    if os.path.exists("/.dockerenv"):
        return "production"

    try:
        with open("/proc/1/cgroup", "r") as f:
            content = f.read()
            if "docker" in content or "containerd" in content:
                return "production"
    except Exception:
        pass

    # Default fallback
    return "development"


# ------------------------
# Config Factory
# ------------------------
def get_config():
    """Returns the appropriate config class based on the current environment."""
    env = os.getenv("FLASK_CONFIG") or detect_environment()
    env = env.lower()

    if env == "testing":
        return TestingConfig
    elif env == "production":
        return ProductionConfig
    else:
        return DevelopmentConfig


# Optional dictionary for direct lookup if you prefer
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
