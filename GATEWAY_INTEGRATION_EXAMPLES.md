# Gateway Integration - Implementation Examples

This document provides code examples for implementing the most critical gateway integration improvements.

## 1. API Versioning with Blueprints

### Updated `app/__init__.py`
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import get_config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    config_class = get_config()
    app.config.from_object(config_class)
    db.init_app(app)

    # Register versioned blueprints
    from app.routes.health import health_bp
    from app.routes.drinks import drinks_bp
    from app.routes.prices import prices_bp

    # Health check (no version needed)
    app.register_blueprint(health_bp)
    
    # Versioned API routes
    app.register_blueprint(drinks_bp, url_prefix='/api/v1')
    app.register_blueprint(prices_bp, url_prefix='/api/v1')

    return app
```

### Updated Routes (example: `app/routes/drinks.py`)
```python
from flask import Blueprint, jsonify, request
from app.models import db, Drink

drinks_bp = Blueprint("drinks", __name__)

# Routes are now at /api/v1/drinks
@drinks_bp.route("/drinks", methods=["GET"])
def get_drinks():
    # ... existing code
    pass
```

---

## 2. Request ID Middleware

### Create `app/middleware/request_id.py`
```python
import uuid
from flask import request, g

def init_request_id(app):
    """Initialize request ID middleware"""
    
    @app.before_request
    def add_request_id():
        # Get request ID from header (gateway may provide) or generate new one
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        g.request_id = request_id
    
    @app.after_request
    def add_request_id_header(response):
        # Add request ID to response headers
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        return response
```

### Update `app/__init__.py`
```python
def create_app():
    # ... existing code ...
    
    # Add request ID middleware
    from app.middleware.request_id import init_request_id
    init_request_id(app)
    
    return app
```

---

## 3. Standardized Error Handling

### Create `app/errors/__init__.py`
```python
from flask import jsonify, g
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    """Base API error class"""
    status_code = 500
    error_code = "INTERNAL_ERROR"
    
    def __init__(self, message, status_code=None, error_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code

class ValidationError(APIError):
    status_code = 400
    error_code = "VALIDATION_ERROR"

class NotFoundError(APIError):
    status_code = 404
    error_code = "NOT_FOUND"

class ConflictError(APIError):
    status_code = 409
    error_code = "CONFLICT"

def register_error_handlers(app):
    """Register error handlers for consistent error responses"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {
            "error": {
                "code": error.error_code,
                "message": error.message,
                "request_id": getattr(g, 'request_id', None)
            }
        }
        return jsonify(response), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = {
            "error": {
                "code": error.code,
                "message": error.description,
                "request_id": getattr(g, 'request_id', None)
            }
        }
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        # Log the full error for debugging
        app.logger.exception("Unhandled exception")
        
        response = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "request_id": getattr(g, 'request_id', None)
            }
        }
        return jsonify(response), 500
```

### Update `app/__init__.py`
```python
def create_app():
    # ... existing code ...
    
    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    return app
```

### Updated Route Example
```python
from app.errors import NotFoundError, ValidationError, ConflictError

@drinks_bp.route("/drinks/<int:drink_id>", methods=["GET"])
def get_drink_by_id(drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        raise NotFoundError(f"Drink with ID {drink_id} not found")
    
    return jsonify({
        "data": {
            "id": drink.id,
            "name": drink.name,
            "description": drink.description
        }
    }), 200
```

---

## 4. Enhanced Health Checks

### Updated `app/routes/health.py`
```python
from flask import Blueprint, jsonify
from datetime import datetime
from app import db
from sqlalchemy import text

health_bp = Blueprint("health", __name__)

@health_bp.route("/health/live", methods=["GET"])
def liveness_check():
    """Liveness probe - is the service running?"""
    return jsonify({
        "status": "alive",
        "service": "drink-service",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

@health_bp.route("/health/ready", methods=["GET"])
def readiness_check():
    """Readiness probe - can the service handle requests?"""
    try:
        # Check database connection
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        
        return jsonify({
            "status": "ready",
            "service": "drink-service",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "not_ready",
            "service": "drink-service",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 503

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Backward compatibility - redirects to liveness"""
    return liveness_check()

@health_bp.route("/api/v1/info", methods=["GET"])
def service_info():
    """Service metadata for gateway"""
    return jsonify({
        "service": "drink-service",
        "version": "1.0.0",
        "api_version": "v1",
        "status": "running"
    }), 200
```

---

## 5. Request Validation with Marshmallow

### Install: `pip install marshmallow`

### Create `app/schemas/drinks.py`
```python
from marshmallow import Schema, fields, validate, ValidationError

class DrinkSchema(Schema):
    """Schema for drink creation/update"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "Name is required"}
    )
    description = fields.Str(
        validate=validate.Length(max=255),
        allow_none=True,
        missing=""
    )
    category = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True
    )

class DrinkResponseSchema(Schema):
    """Schema for drink response"""
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    category = fields.Str(allow_none=True)

# Create instances
drink_schema = DrinkSchema()
drink_response_schema = DrinkResponseSchema()
drinks_response_schema = DrinkResponseSchema(many=True)
```

### Updated Route with Validation
```python
from app.schemas.drinks import drink_schema, drink_response_schema
from app.errors import ValidationError

@drinks_bp.route("/drinks", methods=["POST"])
def add_drink():
    data = request.get_json()
    
    if not data:
        raise ValidationError("Request body must contain JSON")
    
    # Validate input
    try:
        validated_data = drink_schema.load(data)
    except ValidationError as err:
        raise ValidationError(f"Validation failed: {err.messages}")
    
    # Check for duplicates
    existing = Drink.query.filter_by(name=validated_data['name']).first()
    if existing:
        raise ConflictError(f"Drink with name '{validated_data['name']}' already exists")
    
    # Create drink
    drink = Drink(
        name=validated_data['name'],
        description=validated_data.get('description', ''),
        category=validated_data.get('category')
    )
    
    db.session.add(drink)
    db.session.commit()
    
    # Return validated response
    return jsonify({
        "data": drink_response_schema.dump(drink)
    }), 201
```

---

## 6. Structured Logging

### Create `app/logging_config.py`
```python
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(app):
    """Configure structured JSON logging"""
    
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Configure root logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    app.logger.setLevel(getattr(logging, log_level))
    app.logger.addHandler(handler)
    
    # Suppress noisy loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
```

### Logging Middleware
```python
# In app/middleware/logging.py
from flask import request, g
import time

def init_logging_middleware(app):
    @app.before_request
    def log_request_start():
        g.start_time = time.time()
        app.logger.info("Request started", extra={
            "method": request.method,
            "path": request.path,
            "request_id": getattr(g, 'request_id', None)
        })
    
    @app.after_request
    def log_request_end(response):
        duration = time.time() - g.start_time
        app.logger.info("Request completed", extra={
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "request_id": getattr(g, 'request_id', None)
        })
        return response
```

---

## 7. CORS Configuration

### Install: `pip install flask-cors`

### Update `app/__init__.py`
```python
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    # ... existing config ...
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"]
        }
    })
    
    return app
```

---

## 8. Updated Requirements

### Add to `requirements.txt`
```
marshmallow==3.20.1
flask-cors==4.0.0
python-json-logger==2.0.7
gunicorn==21.2.0
```

---

## 9. Gateway Configuration Example

### For Kong Gateway
```yaml
services:
  - name: drink-service
    url: http://drink-service:8000
    routes:
      - name: drink-service-route
        paths:
          - /api/v1/drinks
          - /api/v1/prices
        strip_path: false
    plugins:
      - name: request-id
        config:
          header_name: X-Request-ID
      - name: cors
        config:
          origins:
            - https://your-frontend.com
```

### For AWS API Gateway
- Create REST API
- Set base path: `/api/v1`
- Configure CORS
- Map routes to service endpoints
- Enable request ID passthrough

---

## Testing Gateway Integration

### Test Request ID Propagation
```python
def test_request_id_propagation(base_url):
    """Test that request ID is returned in response"""
    request_id = "test-12345"
    response = requests.get(
        f"{base_url}/api/v1/drinks",
        headers={"X-Request-ID": request_id}
    )
    assert response.headers["X-Request-ID"] == request_id
```

### Test Health Checks
```python
def test_readiness_check(base_url):
    """Test readiness probe"""
    response = requests.get(f"{base_url}/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["database"] == "connected"
```


