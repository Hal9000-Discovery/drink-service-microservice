"""
Comprehensive pytest tests for the Drinks API endpoints.

Tests cover:
- GET /drinks (list all)
- GET /drinks/<id> (get by ID)
- POST /drinks (create)
- Edge cases and error handling
"""

import uuid
import pytest
import requests
from decimal import Decimal


class TestGetAllDrinks:
    """Test suite for GET /drinks endpoint"""

    def test_get_all_drinks_success(self, base_url):
        """Test retrieving all drinks returns 200 and a list"""
        response = requests.get(f"{base_url}/drinks")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_drinks_empty_list(self, base_url, client):
        """Test GET /drinks returns empty list when no drinks exist"""
        # This test uses Flask test client for database isolation
        from app import create_app, db
        from app.models import Drink
        
        # Create a test app with in-memory database
        test_app = create_app()
        test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        test_app.config['TESTING'] = True
        
        with test_app.app_context():
            db.create_all()
            test_client = test_app.test_client()
            
            response = test_client.get("/drinks")
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) == 0

    def test_get_all_drinks_response_structure(self, base_url):
        """Test that all drinks have required fields"""
        response = requests.get(f"{base_url}/drinks")
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            drink = data[0]
            required_fields = ["id", "name", "description"]
            for field in required_fields:
                assert field in drink, f"Missing required field: {field}"
            assert isinstance(drink["id"], int)
            assert isinstance(drink["name"], str)
            assert isinstance(drink["description"], (str, type(None)))

    def test_get_all_drinks_content_type(self, base_url):
        """Test response has correct Content-Type header"""
        response = requests.get(f"{base_url}/drinks")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")


class TestGetDrinkById:
    """Test suite for GET /drinks/<id> endpoint"""

    def test_get_drink_by_id_success(self, base_url):
        """Test retrieving a drink by valid ID"""
        # First, get all drinks to find a valid ID
        all_drinks = requests.get(f"{base_url}/drinks").json()
        
        if len(all_drinks) > 0:
            drink_id = all_drinks[0]["id"]
            response = requests.get(f"{base_url}/drinks/{drink_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == drink_id
            assert "name" in data
            assert "description" in data

    def test_get_drink_by_id_not_found(self, base_url):
        """Test retrieving a drink with non-existent ID returns 404"""
        invalid_id = 99999
        response = requests.get(f"{base_url}/drinks/{invalid_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "message" in data
        assert "not found" in data["message"].lower()

    def test_get_drink_by_id_invalid_type(self, base_url):
        """Test retrieving a drink with invalid ID type returns error"""
        response = requests.get(f"{base_url}/drinks/abc")
        
        # Flask route with <int:drink_id> will return 404 for non-integer
        assert response.status_code in (400, 404, 422)

    def test_get_drink_by_id_zero(self, base_url):
        """Test retrieving a drink with ID 0"""
        response = requests.get(f"{base_url}/drinks/0")
        
        # ID 0 is valid integer but likely doesn't exist
        assert response.status_code in (404, 200)

    def test_get_drink_by_id_negative(self, base_url):
        """Test retrieving a drink with negative ID"""
        response = requests.get(f"{base_url}/drinks/-1")
        
        # Negative integers are valid but should return 404
        assert response.status_code == 404

    def test_get_drink_by_id_response_structure(self, base_url):
        """Test response structure for valid drink"""
        all_drinks = requests.get(f"{base_url}/drinks").json()
        
        if len(all_drinks) > 0:
            drink_id = all_drinks[0]["id"]
            response = requests.get(f"{base_url}/drinks/{drink_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify all expected fields
            assert "id" in data
            assert "name" in data
            assert "description" in data
            
            # Verify data types
            assert isinstance(data["id"], int)
            assert isinstance(data["name"], str)
            assert isinstance(data["description"], (str, type(None)))


class TestCreateDrink:
    """Test suite for POST /drinks endpoint"""

    def test_create_drink_success(self, base_url):
        """Test creating a drink with valid data"""
        unique_name = f"Test Drink {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "A test drink created by pytest"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_create_drink_minimal_data(self, base_url):
        """Test creating a drink with only required fields"""
        unique_name = f"Minimal Drink {uuid.uuid4()}"
        payload = {
            "name": unique_name
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == unique_name
        assert data.get("description") == ""  # Default empty string

    def test_create_drink_missing_name(self, base_url):
        """Test creating a drink without required 'name' field"""
        payload = {
            "description": "Missing name field"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        assert response.status_code == 400
        data = response.json()
        assert "message" in data
        assert "name" in data["message"].lower()

    def test_create_drink_empty_name(self, base_url):
        """Test creating a drink with empty name string"""
        payload = {
            "name": "",
            "description": "Empty name test"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        # Should reject empty name
        assert response.status_code in (400, 409)

    def test_create_drink_whitespace_name(self, base_url):
        """Test creating a drink with only whitespace in name"""
        payload = {
            "name": "   ",
            "description": "Whitespace name test"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        # Should reject or trim whitespace
        assert response.status_code in (200, 201, 400, 409)

    def test_create_drink_duplicate_name(self, base_url):
        """Test creating a drink with duplicate name returns 409"""
        unique_name = f"Duplicate Test {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "First drink"
        }
        
        # First creation should succeed
        first_response = requests.post(f"{base_url}/drinks", json=payload)
        assert first_response.status_code in (200, 201)
        
        # Second creation should fail
        second_response = requests.post(f"{base_url}/drinks", json=payload)
        assert second_response.status_code in (400, 409)
        
        if second_response.status_code == 409:
            data = second_response.json()
            assert "message" in data
            assert "already exists" in data["message"].lower()

    def test_create_drink_long_name(self, base_url):
        """Test creating a drink with very long name"""
        # Model has String(100) limit
        long_name = "A" * 300
        payload = {
            "name": long_name,
            "description": "Long name test"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        # Should reject or truncate
        assert response.status_code in (400, 409, 422, 500)

    def test_create_drink_long_description(self, base_url):
        """Test creating a drink with very long description"""
        # Model has String(255) limit
        unique_name = f"Long Desc Test {uuid.uuid4()}"
        long_description = "B" * 500
        payload = {
            "name": unique_name,
            "description": long_description
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        # Should reject or truncate
        assert response.status_code in (201, 400, 422, 500)

    def test_create_drink_no_json(self, base_url):
        """Test creating a drink without JSON body"""
        response = requests.post(
            f"{base_url}/drinks",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == 400

    def test_create_drink_empty_json(self, base_url):
        """Test creating a drink with empty JSON body"""
        response = requests.post(f"{base_url}/drinks", json={})
        
        assert response.status_code == 400

    def test_create_drink_null_name(self, base_url):
        """Test creating a drink with null name"""
        payload = {
            "name": None,
            "description": "Null name test"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        assert response.status_code == 400

    def test_create_drink_special_characters(self, base_url):
        """Test creating a drink with special characters in name"""
        unique_name = f"Special!@#$%^&*() {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "Special chars test"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        # Should accept or reject based on validation
        assert response.status_code in (201, 400)

    def test_create_drink_unicode_characters(self, base_url):
        """Test creating a drink with unicode characters"""
        unique_name = f"Unicode 测试 🍺 {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "Unicode test"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        # Should handle unicode properly
        assert response.status_code in (201, 400)

    def test_create_drink_numeric_name(self, base_url):
        """Test creating a drink with numeric name (as string)"""
        unique_name = f"12345 {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "Numeric name test"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        # Should accept numeric strings
        assert response.status_code == 201

    def test_create_drink_response_structure(self, base_url):
        """Test response structure after creating a drink"""
        unique_name = f"Structure Test {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "Structure test"
        }
        
        response = requests.post(f"{base_url}/drinks", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "name" in data
        assert "description" in data
        
        # Verify data matches request
        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]

    def test_create_drink_verify_persistence(self, base_url):
        """Test that created drink persists and can be retrieved"""
        unique_name = f"Persistence Test {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "Persistence test"
        }
        
        # Create drink
        create_response = requests.post(f"{base_url}/drinks", json=payload)
        assert create_response.status_code == 201
        created_drink = create_response.json()
        drink_id = created_drink["id"]
        
        # Retrieve drink
        get_response = requests.get(f"{base_url}/drinks/{drink_id}")
        assert get_response.status_code == 200
        retrieved_drink = get_response.json()
        
        # Verify data matches
        assert retrieved_drink["id"] == drink_id
        assert retrieved_drink["name"] == unique_name
        assert retrieved_drink["description"] == payload["description"]


class TestDrinksIntegration:
    """Integration tests for drinks endpoints"""

    def test_create_and_list_drink(self, base_url):
        """Test creating a drink and verifying it appears in list"""
        unique_name = f"Integration Test {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "Integration test"
        }
        
        # Create drink
        create_response = requests.post(f"{base_url}/drinks", json=payload)
        assert create_response.status_code == 201
        
        # Get all drinks
        list_response = requests.get(f"{base_url}/drinks")
        assert list_response.status_code == 200
        drinks = list_response.json()
        
        # Verify drink is in list
        drink_names = [d["name"] for d in drinks]
        assert unique_name in drink_names

    def test_create_get_update_flow(self, base_url):
        """Test complete CRUD flow (create, read)"""
        unique_name = f"CRUD Test {uuid.uuid4()}"
        payload = {
            "name": unique_name,
            "description": "CRUD test"
        }
        
        # Create
        create_response = requests.post(f"{base_url}/drinks", json=payload)
        assert create_response.status_code == 201
        created = create_response.json()
        drink_id = created["id"]
        
        # Read
        get_response = requests.get(f"{base_url}/drinks/{drink_id}")
        assert get_response.status_code == 200
        retrieved = get_response.json()
        assert retrieved["name"] == unique_name


