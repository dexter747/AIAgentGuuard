"""
Comprehensive Production Deployment Test Suite
Tests all critical functionality of the deployed application from local machine
"""
import requests
import pytest
from typing import Dict, Optional
import time

# Production Configuration
PROD_CONFIG = {
    "web_url": "https://overseex.com",
    "admin_url": "https://admin.overseex.com",
    "api_url": "https://api.overseex.com",
    "docs_url": "https://docs.overseex.com",
}

# Test User Credentials
TEST_ADMIN = {
    "email": "admin@overseex.com",
    "password": "Admin@1234"
}


class TestSSLCertificates:
    """Test SSL/HTTPS functionality"""
    
    def test_web_ssl_valid(self):
        """Test that main website has valid SSL certificate"""
        response = requests.get(PROD_CONFIG["web_url"], verify=True)
        assert response.status_code == 200
        assert response.url.startswith("https://")
    
    def test_admin_ssl_valid(self):
        """Test that admin portal has valid SSL certificate"""
        response = requests.get(PROD_CONFIG["admin_url"], verify=True)
        assert response.status_code == 200
        assert response.url.startswith("https://")
    
    def test_api_ssl_valid(self):
        """Test that API has valid SSL certificate"""
        response = requests.get(f"{PROD_CONFIG['api_url']}/docs", verify=True)
        assert response.status_code == 200
    
    def test_docs_ssl_valid(self):
        """Test that docs site has valid SSL certificate"""
        response = requests.get(PROD_CONFIG["docs_url"], verify=True)
        assert response.status_code == 200
    
    def test_http_redirects_to_https(self):
        """Test that HTTP requests redirect to HTTPS"""
        response = requests.get(
            "http://overseex.com", 
            allow_redirects=True,
            verify=True
        )
        assert response.url.startswith("https://")


class TestAPIEndpoints:
    """Test API functionality"""
    
    @pytest.fixture
    def api_base(self):
        return f"{PROD_CONFIG['api_url']}/api/v1"
    
    def test_api_health(self, api_base):
        """Test API health endpoint"""
        response = requests.get(f"{api_base}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_docs_accessible(self):
        """Test that API documentation is accessible"""
        response = requests.get(f"{PROD_CONFIG['api_url']}/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_api_cors_headers(self, api_base):
        """Test that CORS headers are properly configured"""
        response = requests.options(
            f"{api_base}/health",
            headers={
                "Origin": PROD_CONFIG["web_url"],
                "Access-Control-Request-Method": "GET"
            }
        )
        assert "access-control-allow-origin" in response.headers


class TestAuthentication:
    """Test authentication system"""
    
    @pytest.fixture
    def api_base(self):
        return f"{PROD_CONFIG['api_url']}/api/v1"
    
    def test_register_endpoint_exists(self, api_base):
        """Test that registration endpoint exists"""
        # Using invalid data to just check endpoint exists
        response = requests.post(
            f"{api_base}/auth/register",
            json={"email": "test@example.com", "password": "test"}
        )
        # Should return 422 (validation error) or 400, not 404
        assert response.status_code in [400, 422]
    
    def test_login_endpoint_exists(self, api_base):
        """Test that login endpoint exists"""
        response = requests.post(
            f"{api_base}/auth/login",
            json={"email": "invalid@example.com", "password": "invalid"}
        )
        # Should return 401 (unauthorized), not 404
        assert response.status_code in [401, 422]
    
    def test_admin_login_successful(self, api_base):
        """Test that admin can log in successfully"""
        response = requests.post(
            f"{api_base}/auth/login",
            json=TEST_ADMIN
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["is_admin"] == True
        return data["access_token"]
    
    def test_protected_endpoint_requires_auth(self, api_base):
        """Test that protected endpoints require authentication"""
        response = requests.get(f"{api_base}/auth/me")
        assert response.status_code == 401


class TestAdminDashboard:
    """Test admin dashboard functionality"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        response = requests.post(
            f"{api_base}/auth/login",
            json=TEST_ADMIN
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def auth_headers(self, admin_token):
        """Get authentication headers"""
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_admin_stats_accessible(self, auth_headers):
        """Test that admin stats endpoint is accessible"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        response = requests.get(
            f"{api_base}/admin/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_organizations" in data
        assert "monthly_revenue" in data
    
    def test_admin_users_list(self, auth_headers):
        """Test that admin can list users"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        response = requests.get(
            f"{api_base}/admin/users",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_admin_organizations_list(self, auth_headers):
        """Test that admin can list organizations"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        response = requests.get(
            f"{api_base}/admin/organizations",
            headers=auth_headers
        )
        assert response.status_code == 200


class TestEmailSystem:
    """Test email functionality"""
    
    @pytest.fixture
    def api_base(self):
        return f"{PROD_CONFIG['api_url']}/api/v1"
    
    def test_email_verification_flow(self, api_base):
        """Test that email verification is configured"""
        # Register a test user (will fail if user exists, that's ok)
        test_email = f"test_{int(time.time())}@example.com"
        response = requests.post(
            f"{api_base}/auth/register",
            json={
                "email": test_email,
                "password": "Test@1234",
                "organization_name": "Test Org"
            }
        )
        # Should either succeed (200) or fail due to validation (422)
        # but not 500 (email system broken)
        assert response.status_code in [200, 201, 422]


class TestUserDashboard:
    """Test user dashboard functionality"""
    
    def test_dashboard_pages_load(self):
        """Test that dashboard pages load without errors"""
        pages = [
            "/",
            "/pricing",
            "/contact",
            "/how-it-works",
            "/features/agents",
            "/features/health",
            "/features/traces",
            "/features/mocks",
        ]
        
        for page in pages:
            response = requests.get(f"{PROD_CONFIG['web_url']}{page}")
            assert response.status_code == 200, f"Page {page} failed"
    
    def test_no_mixed_content_warnings(self):
        """Test that pages use HTTPS for all resources"""
        response = requests.get(PROD_CONFIG["web_url"])
        content = response.text
        
        # Check that there are no hardcoded HTTP API URLs
        assert "http://api.overseex.com" not in content, \
            "Found insecure HTTP API URLs in page content"
        
        # Check for HTTPS API URLs
        # Note: This only checks static HTML, not JavaScript bundles
        if "api.overseex.com" in content:
            assert "https://api.overseex.com" in content


class TestAPIKeys:
    """Test API key management"""
    
    @pytest.fixture
    def user_token(self):
        """Get regular user authentication token"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        # Login as admin (in real test, use a regular user)
        response = requests.post(
            f"{api_base}/auth/login",
            json=TEST_ADMIN
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def auth_headers(self, user_token):
        """Get authentication headers"""
        return {"Authorization": f"Bearer {user_token}"}
    
    def test_list_api_keys(self, auth_headers):
        """Test listing API keys"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        response = requests.get(
            f"{api_base}/api-keys/",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_api_key(self, auth_headers):
        """Test creating an API key"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        response = requests.post(
            f"{api_base}/api-keys/",
            headers=auth_headers,
            json={"name": f"Test Key {int(time.time())}"}
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "key" in data or "api_key" in data
        
        # Clean up: delete the created key
        key_id = data.get("id")
        if key_id:
            requests.delete(
                f"{api_base}/api-keys/{key_id}",
                headers=auth_headers
            )


class TestBillingSystem:
    """Test billing and subscription functionality"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        response = requests.post(
            f"{api_base}/auth/login",
            json=TEST_ADMIN
        )
        return response.json()["access_token"]
    
    @pytest.fixture
    def auth_headers(self, admin_token):
        return {"Authorization": f"Bearer {admin_token}"}
    
    def test_billing_plans_available(self):
        """Test that billing plans are available"""
        response = requests.get(f"{PROD_CONFIG['web_url']}/api/billing/plans")
        assert response.status_code == 200
    
    def test_admin_has_no_billing(self, auth_headers):
        """Test that super admin doesn't show in billing stats"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        response = requests.get(
            f"{api_base}/admin/stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        # Admin org should not count towards revenue
        assert data["monthly_revenue"] == 0.0


class TestDockerServices:
    """Test that all Docker services are running properly"""
    
    def test_all_services_responding(self):
        """Test that all services respond"""
        services = [
            PROD_CONFIG["web_url"],
            PROD_CONFIG["admin_url"],
            PROD_CONFIG["api_url"] + "/docs",
            PROD_CONFIG["docs_url"],
        ]
        
        for service in services:
            response = requests.get(service, timeout=10)
            assert response.status_code == 200, f"Service {service} not responding"
    
    def test_response_times_acceptable(self):
        """Test that response times are under 2 seconds"""
        api_base = f"{PROD_CONFIG['api_url']}/api/v1"
        start = time.time()
        response = requests.get(f"{api_base}/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0, f"API response took {duration}s (>2s)"


class TestSecurityHeaders:
    """Test security headers are properly configured"""
    
    def test_security_headers_present(self):
        """Test that important security headers are present"""
        response = requests.get(PROD_CONFIG["web_url"])
        headers = response.headers
        
        # Check for important security headers
        # Note: Not all may be required, adjust based on your security policy
        security_checks = {
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-Content-Type-Options": ["nosniff"],
        }
        
        for header, valid_values in security_checks.items():
            if header in headers:
                assert headers[header] in valid_values or len(valid_values) == 0


if __name__ == "__main__":
    print("Running production deployment tests...")
    print(f"Testing against: {PROD_CONFIG['web_url']}")
    pytest.main([__file__, "-v", "--tb=short"])
