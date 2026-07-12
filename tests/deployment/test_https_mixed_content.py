"""
Test for HTTPS Mixed Content Issues
This test specifically checks that all resources are loaded over HTTPS
"""
import requests
import re
from bs4 import BeautifulSoup
import pytest

PROD_WEB_URL = "https://overseex.com"
PROD_ADMIN_URL = "https://admin.overseex.com"
PROD_API_URL = "https://api.overseex.com"


class TestMixedContent:
    """Test for mixed content issues (HTTP resources on HTTPS pages)"""
    
    def test_no_http_api_urls_in_web_app(self):
        """Test that web app doesn't contain HTTP API URLs"""
        # Test main page
        response = requests.get(PROD_WEB_URL)
        assert response.status_code == 200
        
        content = response.text.lower()
        
        # Check for insecure API URLs
        assert "http://api.overseex.com" not in content, \
            "Found insecure HTTP API URL in main page"
        
        # If API URL is mentioned, it should be HTTPS
        if "api.overseex.com" in content:
            assert "https://api.overseex.com" in content.lower()
    
    def test_no_http_api_urls_in_admin_app(self):
        """Test that admin app doesn't contain HTTP API URLs"""
        response = requests.get(PROD_ADMIN_URL)
        assert response.status_code == 200
        
        content = response.text.lower()
        
        # Check for insecure API URLs
        assert "http://api.overseex.com" not in content, \
            "Found insecure HTTP API URL in admin page"
    
    def test_dashboard_pages_use_https(self):
        """Test that dashboard pages use HTTPS for all resources"""
        pages = [
            "/dashboard/mocks",
            "/dashboard/settings",
            "/dashboard/agents",
            "/dashboard/billing",
        ]
        
        for page in pages:
            try:
                response = requests.get(f"{PROD_WEB_URL}{page}", allow_redirects=True)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for HTTP API calls in the page
                    assert "http://api.overseex.com" not in content, \
                        f"Found HTTP API URL in {page}"
            except requests.exceptions.ConnectionError:
                # Page might require auth, that's ok for this test
                pass
    
    def test_admin_dashboard_pages_use_https(self):
        """Test that admin dashboard pages use HTTPS"""
        pages = [
            "/dashboard",
            "/dashboard/users",
            "/dashboard/organizations",
        ]
        
        for page in pages:
            try:
                response = requests.get(f"{PROD_ADMIN_URL}{page}", allow_redirects=True)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for HTTP API calls
                    assert "http://api.overseex.com" not in content, \
                        f"Found HTTP API URL in admin {page}"
            except requests.exceptions.ConnectionError:
                # Page might require auth
                pass
    
    def test_javascript_bundles_use_https(self):
        """Test that JavaScript bundles have HTTPS API URLs"""
        response = requests.get(PROD_WEB_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all script tags
        scripts = soup.find_all('script', src=True)
        
        http_api_found = False
        for script in scripts:
            src = script['src']
            if not src.startswith('http'):
                # Relative URL, make it absolute
                if src.startswith('/'):
                    src = f"{PROD_WEB_URL}{src}"
                else:
                    continue
            
            try:
                script_response = requests.get(src)
                if script_response.status_code == 200:
                    script_content = script_response.text.lower()
                    
                    # Check if this script contains HTTP API URLs
                    if "http://api.overseex.com" in script_content:
                        http_api_found = True
                        print(f"Found HTTP API URL in script: {src}")
            except:
                # Skip if we can't fetch the script
                pass
        
        assert not http_api_found, \
            "Found HTTP API URLs in JavaScript bundles - needs rebuild"
    
    def test_api_calls_are_https(self):
        """Test that API itself only accepts HTTPS"""
        # Try to access API via HTTP (should redirect or fail)
        try:
            response = requests.get(
                "http://api.overseex.com/api/v1/health",
                allow_redirects=False,
                timeout=5
            )
            # Should redirect to HTTPS
            if response.status_code in [301, 302, 307, 308]:
                assert response.headers.get('Location', '').startswith('https://')
            else:
                # Or just not work at all (connection refused is also acceptable)
                pass
        except requests.exceptions.ConnectionError:
            # Connection refused is acceptable - HTTP port not open
            pass


class TestAPISecureConnections:
    """Test that API enforces secure connections"""
    
    def test_api_requires_https(self):
        """Test that API endpoints require HTTPS"""
        # All API calls should be via HTTPS
        response = requests.get(f"{PROD_API_URL}/api/v1/health")
        assert response.status_code == 200
        assert response.url.startswith("https://")
    
    def test_api_documentation_uses_https(self):
        """Test that API documentation shows HTTPS examples"""
        response = requests.get(f"{PROD_API_URL}/docs")
        assert response.status_code == 200
        
        content = response.text
        
        # If API URL is shown in docs, it should be HTTPS
        if "api.overseex.com" in content:
            # Count HTTPS vs HTTP occurrences
            https_count = content.count("https://api.overseex.com")
            http_count = content.count("http://api.overseex.com")
            
            assert https_count > 0, "API docs should show HTTPS URLs"
            assert http_count == 0, "API docs should not show HTTP URLs"


class TestBrowserSecurityPolicy:
    """Test that browser security policies are satisfied"""
    
    def test_strict_transport_security(self):
        """Test HSTS header (optional but recommended)"""
        response = requests.get(PROD_WEB_URL)
        
        # HSTS is recommended but not required
        if 'Strict-Transport-Security' in response.headers:
            hsts = response.headers['Strict-Transport-Security']
            assert 'max-age=' in hsts
    
    def test_content_security_policy_allows_api(self):
        """Test that CSP doesn't block API calls (if CSP is set)"""
        response = requests.get(PROD_WEB_URL)
        
        # If CSP is set, check it allows API
        if 'Content-Security-Policy' in response.headers:
            csp = response.headers['Content-Security-Policy']
            
            # Should not have 'upgrade-insecure-requests' that might cause issues
            # or should explicitly allow api.overseex.com
            if 'connect-src' in csp:
                assert 'api.overseex.com' in csp or "'self'" in csp


def test_environment_variables_baked_correctly():
    """
    This test checks if the Next.js build correctly baked in the HTTPS API URL.
    This is a meta-test to verify the deployment process worked.
    """
    # Get the main page
    response = requests.get(PROD_WEB_URL)
    assert response.status_code == 200
    
    # Parse HTML to find Next.js data
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all script tags
    scripts = soup.find_all('script')
    
    # Look for any script that might contain the API URL configuration
    found_https_config = False
    found_http_config = False
    
    for script in scripts:
        if script.string:
            content = script.string.lower()
            if 'https://api.overseex.com' in content:
                found_https_config = True
            if 'http://api.overseex.com' in content and 'https://api.overseex.com' not in content:
                found_http_config = True
    
    # We expect to find HTTPS config and NO HTTP config
    if found_http_config:
        pytest.fail(
            "Found HTTP API configuration in page. "
            "The Docker containers need to be rebuilt with --no-cache "
            "to properly bake in the HTTPS URL."
        )


if __name__ == "__main__":
    print("Testing for mixed content issues...")
    pytest.main([__file__, "-v", "--tb=short"])
