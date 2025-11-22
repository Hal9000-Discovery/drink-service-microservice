import requests


def test_get_drink_invalid_id(base_url):
    """
    Validate that requesting a drink using a non-numeric ID (e.g., 'abc')
    results in a client error. The route expects an integer, so the API
    should reject or fail to match the route.
    """
    response = requests.get(f"{base_url}/drinks/abc")

    # Acceptable outcomes:
    # 400 → backend validates and rejects bad input
    # 404 → Flask cannot match route because <int:id> fails integer conversion
    # 422 → validation library rejects the type before route handler runs
    assert response.status_code in (400, 404, 422)


def test_get_drink_not_found(base_url):
    """
    Validate that requesting a drink with a valid integer ID but one that
    does not exist in the database should return 404 Not Found.
    """
    invalid_id = 99999
    response = requests.get(f"{base_url}/drinks/{invalid_id}")

    # Expect 404 because the ID is valid type but does not exist.
    assert response.status_code == 404


def test_create_drink_missing_name(base_url):
    """
    POST /drinks without the required 'name' field should trigger input validation
    and return 400 Bad Request.
    """
    payload = {
        "category": "Test Category"
    }
    response = requests.post(f"{base_url}/drinks", json=payload)

    # Missing 'name', so API should reject
    assert response.status_code == 400


def test_create_drink_missing_category(base_url):
    """
    POST /drinks without the required 'category' field should return a 400 error.
    """
    payload = {
        "name": "Bad Drink"
    }
    response = requests.post(f"{base_url}/drinks", json=payload)

    # Missing 'category', so API should not create drink
    assert response.status_code in (400, 409, 422)


def test_create_drink_empty_name(base_url):
    """
    Validate that creating a drink with an empty string as name should be rejected.
    This prevents inserting invalid or meaningless data into the database.
    """
    payload = {
        "name": "",
        "category": "Test"
    }
    response = requests.post(f"{base_url}/drinks", json=payload)

    # Empty name is invalid → expect 400 Bad Request
    assert response.status_code in (400,409)


def test_create_drink_too_long_name(base_url):
    """
    Validate that the API enforces maximum field length limits by rejecting
    excessively long names (e.g., 300 characters).
    """
    payload = {
        "name": "A" * 300,  # Very long name
        "category": "Hot"
    }
    response = requests.post(f"{base_url}/drinks", json=payload)

    # Name too long → expect 400 Bad Request
    assert response.status_code in (400, 409, 422)
    


def test_create_duplicate_drink(base_url):
    """
    Validate that the API does not allow duplicate drink names when uniqueness
    constraints are expected. Sends the same drink twice and the second should
    fail with a 409 Conflict or 400 Bad Request depending on implementation.
    """

    payload = {"name": "DuplicateTestDrink", "category": "Cold"}

    # First request should succeed
    first = requests.post(f"{base_url}/drinks", json=payload)
    assert first.status_code in (200, 201)

    # Second request with the same payload should fail
    second = requests.post(f"{base_url}/drinks", json=payload)

    # Expected:
    # 409 → explicit conflict handling
    # 400 → failed validation or DB constraint error
    assert second.status_code in (400, 409)
