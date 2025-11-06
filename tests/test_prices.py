import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def service_url():
    """Base URL for the microservice under test."""
    return "http://localhost:5001"


def test_prices_endpoint(service_url):
    """
    Validates that the /prices endpoint returns expected structure and data types.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        response = page.request.get(f"{service_url}/prices")
        assert response.ok, f"Request failed with status {response.status}"

        prices_data = response.json()
        assert "prices" in prices_data, "Missing 'prices' key in response"

        prices = prices_data["prices"]
        assert isinstance(prices, list)
        assert len(prices) > 0, "Expected at least one price record"

        sample = prices[0]
        for key in ["price_id", "drink_id", "price_amount", "effective_date", "end_date", "created_at"]:
            assert key in sample, f"Missing key '{key}'"

        assert float(sample["price_amount"]) > 0, "Price amount should be positive"

        browser.close()
