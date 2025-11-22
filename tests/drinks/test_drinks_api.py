# tests/test_drinks.py

import uuid
import requests


# ---------------------------------------------------------
# Test GET /drinks
# ---------------------------------------------------------
def test_get_all_drinks(base_url):
    """
    Validate that GET /drinks returns HTTP 200 and a list.
    """
    response = requests.get(f"{base_url}/drinks")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)  # expect list of drinks


# ---------------------------------------------------------
# Test GET /drinks/{id}
# ---------------------------------------------------------
def test_get_drink_by_id(base_url):
    """
    Validate retrieving a single drink by ID.
    Assumes ID 1 exists. If not, update to any correct ID.
    """
    drink_id = 1
    response = requests.get(f"{base_url}/drinks/{drink_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == drink_id
    assert "name" in data             # ensure fields exist
    assert "description" in data


# ---------------------------------------------------------
# Test POST /drinks
# ---------------------------------------------------------
def test_create_drink(base_url):
    """
    Validate creating a drink returns 201 and correct data.
    """

    # Create a unique drink name each time to avoid 409 Conflict
    unique_name = f"Test Drink {uuid.uuid4()}"

    payload = {
        "name": unique_name,
        "description": "Created by pytest automation"
    }

    response = requests.post(f"{base_url}/drinks", json=payload)

    assert response.status_code == 201  # Created

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
