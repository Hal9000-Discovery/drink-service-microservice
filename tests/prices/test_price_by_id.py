import requests


def test_get_price_by_id_success(base_url):
    """
    Validate GET /prices/<id> returns correct data.
    """
    price_id = 1  # Adjust if needed based on your seeded DB

    response = requests.get(f"{base_url}/prices/{price_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()

    # Expected schema based on your API output
    expected_keys = [
        "price_id",
        "drink_id",
        "price_amount",
        "effective_date",
        "end_date",
        "created_at",
    ]

    for key in expected_keys:
        assert key in data, f"Missing key: {key}"

    # Validate values
    assert data["price_id"] == price_id
    assert float(data["price_amount"]) > 0


def test_get_price_by_id_not_found(base_url):
    """
    Validate GET /prices/<id> returns 404 for missing price.
    """
    invalid_id = 9999

    response = requests.get(f"{base_url}/prices/{invalid_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    data = response.json()

    # API should provide an error message
    assert "message" in data, "Missing 'message' in 404 response"
    assert "not found" in data["message"].lower()
