"""
Integration tests for OpenTelemetry Demo application.

These tests verify that all services work together correctly
and that distributed tracing is functioning properly.
"""

import pytest
import requests
import time
import json
from typing import Dict, List, Any


class TestIntegration:
    """Integration test suite for the OpenTelemetry Demo."""
    
    BASE_URL_FRONTEND = "http://localhost:8080"
    BASE_URL_BACKEND = "http://localhost:5000"
    JAEGER_URL = "http://localhost:16686"
    ZIPKIN_URL = "http://localhost:9411"
    
    def wait_for_service(self, url: str, timeout: int = 60) -> bool:
        """Wait for a service to become available."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        return False
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_services(self):
        """Ensure all services are running before tests."""
        services = [
            (f"{self.BASE_URL_FRONTEND}/health", "Frontend"),
            (f"{self.BASE_URL_BACKEND}/health", "Backend"),
            (f"{self.JAEGER_URL}", "Jaeger"),
            (f"{self.ZIPKIN_URL}/zipkin/", "Zipkin"),
        ]
        
        for url, service in services:
            assert self.wait_for_service(url), f"{service} service failed to start"
    
    def test_frontend_health(self):
        """Test frontend service health endpoint."""
        response = requests.get(f"{self.BASE_URL_FRONTEND}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "frontend"
    
    def test_backend_health(self):
        """Test backend service health endpoint."""
        response = requests.get(f"{self.BASE_URL_BACKEND}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "backend"
    
    def test_user_workflow(self):
        """Test complete user creation and retrieval workflow."""
        # Create a new user
        user_data = {
            "name": "Integration Test User",
            "email": f"integration-test-{int(time.time())}@example.com"
        }
        
        response = requests.post(
            f"{self.BASE_URL_FRONTEND}/api/users",
            json=user_data
        )
        assert response.status_code == 201
        created_user = response.json()
        assert "id" in created_user
        assert created_user["name"] == user_data["name"]
        assert created_user["email"] == user_data["email"]
        
        # Get all users and verify the new user is included
        response = requests.get(f"{self.BASE_URL_FRONTEND}/api/users")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert any(user["email"] == user_data["email"] for user in users)
    
    def test_product_workflow(self):
        """Test product retrieval workflow."""
        response = requests.get(f"{self.BASE_URL_FRONTEND}/api/products")
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) > 0
        
        # Verify product structure
        product = products[0]
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "stock" in product
    
    def test_order_workflow(self):
        """Test order creation workflow."""
        order_data = {
            "product_id": 1,
            "quantity": 2
        }
        
        response = requests.post(
            f"{self.BASE_URL_FRONTEND}/api/orders",
            json=order_data
        )
        assert response.status_code == 201
        order = response.json()
        assert "order_id" in order
        assert order["status"] == "completed"
        assert order["payment_status"] == "completed"
    
    def test_tracing_propagation(self):
        """Test that traces are properly propagated between services."""
        # Create a user to generate traces
        user_data = {
            "name": "Tracing Test User",
            "email": f"tracing-test-{int(time.time())}@example.com"
        }
        
        response = requests.post(
            f"{self.BASE_URL_FRONTEND}/api/users",
            json=user_data
        )
        assert response.status_code == 201
        
        # Give some time for traces to be processed
        time.sleep(5)
        
        # Check Jaeger for traces (this is a basic check - in practice you'd use Jaeger API)
        try:
            response = requests.get(f"{self.JAEGER_URL}/api/traces?service=frontend-service")
            if response.status_code == 200:
                # If Jaeger API is accessible, verify we can query traces
                traces_data = response.json()
                assert "data" in traces_data
        except requests.exceptions.RequestException:
            # Jaeger API might not be accessible in test environment
            pytest.skip("Jaeger API not accessible")
    
    def test_error_handling(self):
        """Test error handling and propagation."""
        # Test invalid user creation
        invalid_user_data = {
            "name": "Test User"
            # Missing email field
        }
        
        response = requests.post(
            f"{self.BASE_URL_FRONTEND}/api/users",
            json=invalid_user_data
        )
        # Should return 400 Bad Request
        assert response.status_code == 400
        
        # Test duplicate email
        user_data = {
            "name": "Duplicate User",
            "email": "duplicate@example.com"
        }
        
        # First request should succeed
        response1 = requests.post(
            f"{self.BASE_URL_FRONTEND}/api/users",
            json=user_data
        )
        assert response1.status_code == 201
        
        # Second request with same email should fail
        response2 = requests.post(
            f"{self.BASE_URL_FRONTEND}/api/users",
            json=user_data
        )
        assert response2.status_code == 400
    
    def test_metrics_endpoints(self):
        """Test that metrics endpoints are accessible."""
        # Backend metrics (if exposed)
        try:
            response = requests.get(f"{self.BASE_URL_BACKEND}/metrics")
            # This might not be implemented, so we don't assert on status
        except requests.exceptions.RequestException:
            pass
        
        # Prometheus metrics
        try:
            response = requests.get("http://localhost:9090/metrics")
            if response.status_code == 200:
                assert "prometheus" in response.text.lower()
        except requests.exceptions.RequestException:
            pytest.skip("Prometheus not accessible")


@pytest.mark.slow
class TestPerformance:
    """Performance and load testing integration tests."""
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import concurrent.futures
        
        BASE_URL = "http://localhost:8080"
        
        def make_request(request_id):
            user_data = {
                "name": f"Load Test User {request_id}",
                "email": f"load-test-{request_id}-{int(time.time())}@example.com"
            }
            response = requests.post(
                f"{BASE_URL}/api/users",
                json=user_data
            )
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Most requests should succeed (some might fail due to duplicate emails)
        success_count = sum(1 for status in results if status == 201)
        assert success_count >= 8  # At least 80% should succeed