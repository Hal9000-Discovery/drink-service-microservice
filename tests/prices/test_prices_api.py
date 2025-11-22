import requests


def test_prices_endpoint(base_url):
    """
    Validate that GET /prices returns a list of price records
    with the expected structure.
    """
    response = requests.get(f"{base_url}/prices")
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    data = response.json()

    # Your API returns: { "prices": [ ... ] }
    assert isinstance(data, dict), "Expected a JSON object"
    assert "prices" in data, "Missing 'prices' key in response"

    prices = data["prices"]
    assert isinstance(prices, list), "'prices' should be a list"
    assert len(prices) > 0, "Expected at least one price record"

    sample = prices[0]

    expected_keys = [
        "price_id",
        "drink_id",
        "price_amount",
        "effective_date",
        "end_date",
        "created_at",
    ]

    for key in expected_keys:
        assert key in sample, f"Missing key '{key}'"

    assert float(sample["price_amount"]) > 0, "Price amount should be positive"
