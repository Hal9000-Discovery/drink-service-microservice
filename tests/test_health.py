import pytest
from playwright.sync_api import sync_playwright

def test_health_endpoint():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        response = page.request.get("http://localhost:5001/health")
        assert response.ok
        data = response.json()
        assert data["status"] == "healthy"

        browser.close()
 