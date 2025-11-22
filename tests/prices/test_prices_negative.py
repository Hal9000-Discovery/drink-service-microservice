import requests


def test_get_price_invalid_id(base_url):
    """
    GET /prices/<id> with a non-numeric value should return a client error.
    Flask routes using <int:id> do not match non-integer values, resulting in 404.
    Some validation layers may return 400 or 422 instead.
    """
    response = requests.get(f"{base_url}/prices/abc")

    # Acceptable outcomes depending on implementation
    assert response.status_code in (400, 404, 422)


def test_get_price_not_found(base_url):
    """
    Requesting a price ID that does not exist should return 404 Not Found.
    The ID format is correct, but the record is missing.
    """
    invalid_id = 999999
    response = requests.get(f"{base_url}/prices/{invalid_id}")

    assert response.status_code == 404


def test_create_price_missing_fields(base_url):
    """
    POST /prices without required fields should result in 400 Bad Request.
    Required fields are typically: drink_id, price_amount, effective_date.
    """
    payload = {
        # Missing 'drink_id', 'price_amount', 'effective_date'
        "end_date": None
    }
    response = requests.post(f"{base_url}/prices", json=payload)

    assert response.status_code == 400


def test_create_price_invalid_drink_id(base_url):
    """
    POST /prices with invalid drink_id type (string instead of int)
    should be rejected by validation or route handling.
    """
    payload = {
        "drink_id": "invalid",
        "price_amount": 4.99,
        "effective_date": "2024-01-01",
        "end_date": None
    }
    response = requests.post(f"{base_url}/prices", json=payload)

    assert response.status_code in (400, 422)


def test_create_price_negative_amount(base_url):
    """
    POST /prices with a negative price value should be rejected.
    Prices should always be positive.
    """
    payload = {
        "drink_id": 1,
        "price_amount": -10.00,
        "effective_date": "2024-01-01",
        "end_date": None
    }
    response = requests.post(f"{base_url}/prices", json=payload)

    assert response.status_code == 400


def test_create_price_invalid_date_format(base_url):
    """
    POST /prices with an invalid date format should result in 400 or 422.
    For example, using an impossible date or a non-ISO format.
    """
    payload = {
        "drink_id": 1,
        "price_amount": 2.99,
        "effective_date": "2024-99-99",  # Invalid date
        "end_date": None
    }
    response = requests.post(f"{base_url}/prices", json=payload)

    assert response.status_code in (400, 422)


def test_create_price_end_date_before_effective(base_url):
    """
    POST /prices where end_date occurs BEFORE effective_date should not be allowed.
    This enforces logical business rules.
    """
    payload = {
        "drink_id": 1,
        "price_amount": 2.99,
        "effective_date": "2024-12-01",
        "end_date": "2024-01-01"  # Earlier than effective date — invalid
    }
    response = requests.post(f"{base_url}/prices", json=payload)

    assert response.status_code == 400


def test_create_duplicate_price_for_same_effective_date(base_url):
    """
    Creating two prices for the same drink on the same effective_date should fail.
    This prevents overlapping price rules for the same drink.
    """

    payload = {
        "drink_id": 1,
        "price_amount": 3.99,
        "effective_date": "2024-05-01",
        "end_date": None
    }

    # First should succeed
    first = requests.post(f"{base_url}/prices", json=payload)
    assert first.status_code in (200, 201)

    # Second should fail due to duplicate rule
    second = requests.post(f"{base_url}/prices", json=payload)
    assert second.status_code in (400, 409)
