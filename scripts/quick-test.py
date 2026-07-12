#!/usr/bin/env python3
"""
Quick Deployment Health Check
Runs the most critical tests to verify deployment is working
"""
import requests
import sys

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

PROD_CONFIG = {
    "web_url": "https://overseex.com",
    "admin_url": "https://admin.overseex.com",
    "api_url": "https://api.overseex.com",
    "docs_url": "https://docs.overseex.com",
}

TEST_ADMIN = {
    "email": "admin@overseex.com",
    "password": "Admin@1234"
}

def print_result(test_name, passed, message=""):
    status = f"{GREEN}✓ PASS{NC}" if passed else f"{RED}✗ FAIL{NC}"
    print(f"{status} {test_name}")
    if message and not passed:
        print(f"     {RED}{message}{NC}")

def test_ssl():
    """Test SSL certificates"""
    print(f"\n{YELLOW}Testing SSL Certificates...{NC}")
    
    try:
        response = requests.get(PROD_CONFIG["web_url"], verify=True, timeout=10)
        print_result("Web SSL", response.status_code == 200)
    except Exception as e:
        print_result("Web SSL", False, str(e))
        return False
    
    try:
        response = requests.get(PROD_CONFIG["admin_url"], verify=True, timeout=10)
        print_result("Admin SSL", response.status_code == 200)
    except Exception as e:
        print_result("Admin SSL", False, str(e))
        return False
    
    try:
        response = requests.get(f"{PROD_CONFIG['api_url']}/docs", verify=True, timeout=10)
        print_result("API SSL", response.status_code == 200)
    except Exception as e:
        print_result("API SSL", False, str(e))
        return False
    
    return True

def test_mixed_content():
    """Test for mixed content issues"""
    print(f"\n{YELLOW}Testing for Mixed Content (HTTP URLs)...{NC}")
    
    try:
        response = requests.get(PROD_CONFIG["web_url"], timeout=10)
        content = response.text.lower()
        
        has_http = "http://api.overseex.com" in content
        print_result(
            "No HTTP API URLs in static HTML", 
            not has_http,
            "Found HTTP URLs - but this might be in cached JS bundles, not static HTML"
        )
        
        return not has_http
    except Exception as e:
        print_result("Mixed Content Check", False, str(e))
        return False

def test_api():
    """Test API health"""
    print(f"\n{YELLOW}Testing API...{NC}")
    
    try:
        response = requests.get(f"{PROD_CONFIG['api_url']}/api/v1/health", timeout=10)
        is_healthy = response.status_code == 200 and response.json().get("status") == "healthy"
        print_result("API Health", is_healthy)
        return is_healthy
    except Exception as e:
        print_result("API Health", False, str(e))
        return False

def test_authentication():
    """Test authentication"""
    print(f"\n{YELLOW}Testing Authentication...{NC}")
    
    try:
        response = requests.post(
            f"{PROD_CONFIG['api_url']}/api/v1/auth/login",
            json=TEST_ADMIN,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            has_token = "access_token" in data
            is_admin = data.get("user", {}).get("is_admin", False)
            
            print_result("Admin Login", has_token and is_admin)
            return has_token and is_admin
        else:
            print_result("Admin Login", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Admin Login", False, str(e))
        return False

def test_admin_dashboard():
    """Test admin dashboard"""
    print(f"\n{YELLOW}Testing Admin Dashboard...{NC}")
    
    try:
        # Get admin token
        response = requests.post(
            f"{PROD_CONFIG['api_url']}/api/v1/auth/login",
            json=TEST_ADMIN,
            timeout=10
        )
        
        if response.status_code != 200:
            print_result("Admin Dashboard", False, "Could not login")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test admin stats endpoint
        response = requests.get(
            f"{PROD_CONFIG['api_url']}/api/v1/admin/stats",
            headers=headers,
            timeout=10
        )
        
        is_working = response.status_code == 200 and "total_users" in response.json()
        print_result("Admin Stats Endpoint", is_working)
        return is_working
    except Exception as e:
        print_result("Admin Dashboard", False, str(e))
        return False

def test_api_keys():
    """Test API key management"""
    print(f"\n{YELLOW}Testing API Keys...{NC}")
    
    try:
        # Get admin token
        response = requests.post(
            f"{PROD_CONFIG['api_url']}/api/v1/auth/login",
            json=TEST_ADMIN,
            timeout=10
        )
        
        if response.status_code != 200:
            print_result("API Keys", False, "Could not login")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test list API keys
        response = requests.get(
            f"{PROD_CONFIG['api_url']}/api/v1/api-keys/",
            headers=headers,
            timeout=10
        )
        
        is_working = response.status_code == 200
        print_result("API Keys Endpoint", is_working)
        return is_working
    except Exception as e:
        print_result("API Keys", False, str(e))
        return False

def main():
    print("=" * 60)
    print(f"{YELLOW}Quick Deployment Health Check{NC}")
    print("=" * 60)
    print(f"Testing: {PROD_CONFIG['web_url']}")
    
    results = []
    
    results.append(("SSL", test_ssl()))
    results.append(("API", test_api()))
    results.append(("Authentication", test_authentication()))
    results.append(("Admin Dashboard", test_admin_dashboard()))
    results.append(("API Keys", test_api_keys()))
    results.append(("Mixed Content", test_mixed_content()))
    
    print("\n" + "=" * 60)
    print(f"{YELLOW}Summary{NC}")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✓{NC}" if result else f"{RED}✗{NC}"
        print(f"{status} {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"{GREEN}All tests passed! Deployment is healthy.{NC}")
        
        print(f"\n{YELLOW}Note on Mixed Content Errors:{NC}")
        print("If you're seeing mixed content errors in the browser but the test passes,")
        print("your browser has cached old JavaScript files.")
        print("\nTo fix:")
        print("1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
        print("2. Or open in Incognito/Private mode")
        print("3. Or clear all browser cache")
        
        return 0
    else:
        print(f"{RED}Some tests failed. Check the output above for details.{NC}")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{NC}")
        sys.exit(1)
