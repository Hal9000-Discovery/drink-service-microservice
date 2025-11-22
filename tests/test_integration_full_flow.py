"""
Full integration tests that test complete workflows across multiple endpoints.

These tests verify that the service works correctly end-to-end.
"""

import pytest
import requests
import uuid
from decimal import Decimal
from datetime import date, timedelta


class TestFullWorkflow:
    """Test complete workflows from start to finish"""

    def test_create_drink_add_price_retrieve_flow(self, base_url):
        """Test complete flow: create drink, add price, retrieve both"""
        # Step 1: Create a drink
        unique_name = f"Workflow Test {uuid.uuid4()}"
        drink_payload = {
            "name": unique_name,
            "description": "Workflow test drink"
        }
        
        drink_response = requests.post(f"{base_url}/drinks", json=drink_payload)
        assert drink_response.status_code == 201
        created_drink = drink_response.json()
        drink_id = created_drink["id"]
        
        # Step 2: Add a price for the drink
        price_payload = {
            "drink_id": drink_id,
            "price_amount": 4.99,
            "effective_date": date.today().isoformat()
        }
        
        price_response = requests.post(f"{base_url}/prices", json=price_payload)
        assert price_response.status_code == 201
        created_price = price_response.json()
        price_id = created_price["price_id"]
        
        # Step 3: Retrieve the drink
        get_drink_response = requests.get(f"{base_url}/drinks/{drink_id}")
        assert get_drink_response.status_code == 200
        retrieved_drink = get_drink_response.json()
        assert retrieved_drink["name"] == unique_name
        
        # Step 4: Retrieve the price
        get_price_response = requests.get(f"{base_url}/prices/{price_id}")
        assert get_price_response.status_code == 200
        retrieved_price = get_price_response.json()
        assert retrieved_price["drink_id"] == drink_id
        assert Decimal(retrieved_price["price_amount"]) == Decimal("4.99")

    def test_multiple_prices_for_drink_workflow(self, base_url):
        """Test creating a drink and adding multiple prices over time"""
        # Create drink
        unique_name = f"Multi-Price Test {uuid.uuid4()}"
        drink_payload = {"name": unique_name, "description": "Multi-price test"}
        
        drink_response = requests.post(f"{base_url}/drinks", json=drink_payload)
        assert drink_response.status_code == 201
        drink_id = drink_response.json()["id"]
        
        # Add first price (Q1 2024)
        price1_payload = {
            "drink_id": drink_id,
            "price_amount": 4.99,
            "effective_date": "2024-01-01",
            "end_date": "2024-03-31"
        }
        price1_response = requests.post(f"{base_url}/prices", json=price1_payload)
        assert price1_response.status_code == 201
        
        # Add second price (Q2 2024)
        price2_payload = {
            "drink_id": drink_id,
            "price_amount": 5.99,
            "effective_date": "2024-04-01",
            "end_date": "2024-06-30"
        }
        price2_response = requests.post(f"{base_url}/prices", json=price2_payload)
        assert price2_response.status_code == 201
        
        # Add third price (Q3 2024 onwards)
        price3_payload = {
            "drink_id": drink_id,
            "price_amount": 6.99,
            "effective_date": "2024-07-01"
        }
        price3_response = requests.post(f"{base_url}/prices", json=price3_payload)
        assert price3_response.status_code == 201
        
        # Verify all prices exist
        all_prices_response = requests.get(f"{base_url}/prices")
        assert all_prices_response.status_code == 200
        all_prices = all_prices_response.json()["prices"]
        
        drink_prices = [p for p in all_prices if p["drink_id"] == drink_id]
        assert len(drink_prices) >= 3

    def test_error_handling_workflow(self, base_url):
        """Test error handling across the workflow"""
        # Try to create price for non-existent drink
        invalid_price_payload = {
            "drink_id": 99999,
            "price_amount": 4.99,
            "effective_date": "2024-01-01"
        }
        response = requests.post(f"{base_url}/prices", json=invalid_price_payload)
        assert response.status_code == 404
        
        # Try to get non-existent drink
        response = requests.get(f"{base_url}/drinks/99999")
        assert response.status_code == 404
        
        # Try to get non-existent price
        response = requests.get(f"{base_url}/prices/99999")
        assert response.status_code == 404

    def test_data_consistency_workflow(self, base_url):
        """Test that data remains consistent across operations"""
        # Create drink
        unique_name = f"Consistency Test {uuid.uuid4()}"
        drink_payload = {"name": unique_name, "description": "Consistency test"}
        
        create_response = requests.post(f"{base_url}/drinks", json=drink_payload)
        assert create_response.status_code == 201
        drink_id = create_response.json()["id"]
        
        # Verify drink appears in list
        list_response = requests.get(f"{base_url}/drinks")
        assert list_response.status_code == 200
        drinks = list_response.json()
        assert any(d["id"] == drink_id for d in drinks)
        
        # Verify drink can be retrieved by ID
        get_response = requests.get(f"{base_url}/drinks/{drink_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == unique_name

    def test_concurrent_operations(self, base_url):
        """Test handling of concurrent operations"""
        import concurrent.futures
        
        def create_drink(index):
            unique_name = f"Concurrent Test {index} {uuid.uuid4()}"
            payload = {"name": unique_name, "description": f"Concurrent test {index}"}
            response = requests.post(f"{base_url}/drinks", json=payload)
            return response.status_code in (200, 201)
        
        # Create 5 drinks concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_drink, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should succeed
        assert all(results), "Some concurrent operations failed"

    def test_service_health_during_operations(self, base_url):
        """Test that health endpoint works during operations"""
        # Check health before operations
        health_before = requests.get(f"{base_url}/health")
        assert health_before.status_code == 200
        
        # Perform operations
        unique_name = f"Health Test {uuid.uuid4()}"
        drink_payload = {"name": unique_name, "description": "Health test"}
        requests.post(f"{base_url}/drinks", json=drink_payload)
        
        # Check health after operations
        health_after = requests.get(f"{base_url}/health")
        assert health_after.status_code == 200
        
        # Health should remain consistent
        assert health_before.json()["status"] == health_after.json()["status"]


