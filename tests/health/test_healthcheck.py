from playwright.sync_api import sync_playwright


def test_health_endpoint(base_url):
    """
    Verify the /health endpoint returns a healthy status.
    """
    with sync_playwright() as p:
        context = p.request.new_context(base_url=base_url)
        
        response = context.get("/health")
        assert response.ok, f"Expected 200 OK, got {response.status}"
        
        data = response.json()
        assert data.get("status") == "healthy"
        
        context.dispose()
