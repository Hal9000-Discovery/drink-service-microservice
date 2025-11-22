"""
Comprehensive pytest tests for the Health Check endpoints.

Tests cover:
- GET /health
- Response structure and content
- Performance characteristics
"""

import pytest
import requests
from datetime import datetime


class TestHealthEndpoint:
    """Test suite for GET /health endpoint"""

    def test_health_endpoint_success(self, base_url):
        """Test health endpoint returns 200"""
        response = requests.get(f"{base_url}/health")
        
        assert response.status_code == 200

    def test_health_endpoint_response_structure(self, base_url):
        """Test health endpoint response structure"""
        response = requests.get(f"{base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "service" in data
        assert "status" in data
        assert "timestamp" in data
        
        # Verify values
        assert data["service"] == "drink-service"
        assert data["status"] == "healthy"

    def test_health_endpoint_timestamp_format(self, base_url):
        """Test health endpoint timestamp is valid ISO format"""
        response = requests.get(f"{base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify timestamp is valid ISO format
        timestamp = data["timestamp"]
        assert timestamp.endswith("Z")  # UTC indicator
        # Try to parse it
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp}")

    def test_health_endpoint_content_type(self, base_url):
        """Test health endpoint has correct Content-Type"""
        response = requests.get(f"{base_url}/health")
        
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_health_endpoint_method_not_allowed(self, base_url):
        """Test health endpoint rejects non-GET methods"""
        # POST should not be allowed
        response = requests.post(f"{base_url}/health")
        assert response.status_code in (405, 404)  # Method not allowed or not found
        
        # PUT should not be allowed
        response = requests.put(f"{base_url}/health")
        assert response.status_code in (405, 404)
        
        # DELETE should not be allowed
        response = requests.delete(f"{base_url}/health")
        assert response.status_code in (405, 404)

    def test_health_endpoint_performance(self, base_url):
        """Test health endpoint responds quickly"""
        import time
        
        start = time.time()
        response = requests.get(f"{base_url}/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        # Health check should be very fast (< 100ms)
        assert duration < 0.1, f"Health check took {duration}s, expected < 0.1s"

    def test_health_endpoint_multiple_requests(self, base_url):
        """Test health endpoint handles multiple concurrent requests"""
        import concurrent.futures
        
        def check_health():
            response = requests.get(f"{base_url}/health")
            return response.status_code == 200
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_health) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(results), "Some health checks failed"

    def test_health_endpoint_no_authentication_required(self, base_url):
        """Test health endpoint is accessible without authentication"""
        response = requests.get(f"{base_url}/health")
        
        assert response.status_code == 200
        # Should not require auth headers

    def test_health_endpoint_caching_headers(self, base_url):
        """Test health endpoint cache headers (if any)"""
        response = requests.get(f"{base_url}/health")
        
        assert response.status_code == 200
        # Health checks typically should not be cached
        # But we just verify it doesn't break


