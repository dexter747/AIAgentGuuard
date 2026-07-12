# Production Deployment Test Suite

This directory contains comprehensive tests for validating the production deployment of the AgentGuard platform.

## Prerequisites

```bash
pip install pytest requests beautifulsoup4 lxml
```

## Test Files

### 1. `test_production.py`
Comprehensive tests covering all major functionality:
- ✅ SSL Certificate validation for all domains
- ✅ HTTP to HTTPS redirects
- ✅ API endpoints and health checks
- ✅ Authentication system (login, registration)
- ✅ Admin dashboard functionality
- ✅ Email system configuration
- ✅ User dashboard pages
- ✅ API key management
- ✅ Billing system
- ✅ Docker services health
- ✅ Security headers

### 2. `test_https_mixed_content.py`
Specific tests for HTTPS/mixed content issues:
- ✅ No HTTP API URLs in web app
- ✅ No HTTP API URLs in admin app
- ✅ Dashboard pages use HTTPS
- ✅ JavaScript bundles use HTTPS
- ✅ API requires HTTPS
- ✅ Browser security policies satisfied
- ✅ Environment variables baked correctly

## Running Tests

### Run All Tests
```bash
# From project root
cd /Users/developer/Desktop/AgentGaurd
pytest tests/deployment/ -v
```

### Run Specific Test File
```bash
# Test production functionality
pytest tests/deployment/test_production.py -v

# Test HTTPS/mixed content
pytest tests/deployment/test_https_mixed_content.py -v
```

### Run Specific Test Class
```bash
# Test only SSL certificates
pytest tests/deployment/test_production.py::TestSSLCertificates -v

# Test only mixed content
pytest tests/deployment/test_https_mixed_content.py::TestMixedContent -v
```

### Run Specific Test
```bash
# Test admin login
pytest tests/deployment/test_production.py::TestAuthentication::test_admin_login_successful -v

# Test JavaScript bundles
pytest tests/deployment/test_https_mixed_content.py::TestMixedContent::test_javascript_bundles_use_https -v
```

## Test Configuration

Edit the configuration in each test file:

```python
# Production URLs
PROD_CONFIG = {
    "web_url": "https://overseex.com",
    "admin_url": "https://admin.overseex.com",
    "api_url": "https://api.overseex.com",
    "docs_url": "https://docs.overseex.com",
}

# Test credentials
TEST_ADMIN = {
    "email": "admin@overseex.com",
    "password": "Admin@1234"
}
```

## Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/test-production.yml
name: Test Production Deployment

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pytest requests beautifulsoup4 lxml
      - name: Run deployment tests
        run: |
          pytest tests/deployment/ -v --tb=short
```

## Common Issues and Solutions

### Mixed Content Errors

**Symptom:** Browser console shows:
```
Mixed Content: The page at 'https://overseex.com/...' was loaded over HTTPS,
but requested an insecure resource 'http://api.overseex.com/...'
```

**Diagnosis:**
```bash
# Run the mixed content test
pytest tests/deployment/test_https_mixed_content.py::TestMixedContent::test_javascript_bundles_use_https -v
```

**Solution:**
If the test fails, the Next.js containers need to be rebuilt:
```bash
# On VPS
cd /root/AIAgentGuuard
docker-compose -f docker-compose.prod.yml build --no-cache web admin
docker-compose -f docker-compose.prod.yml up -d web admin
```

**Verification:**
1. Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
2. Re-run the test
3. Check browser console - errors should be gone

### SSL Certificate Issues

**Test:**
```bash
pytest tests/deployment/test_production.py::TestSSLCertificates -v
```

**Fix:**
```bash
# On VPS
certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
```

### Authentication Failures

**Test:**
```bash
pytest tests/deployment/test_production.py::TestAuthentication -v
```

**Common causes:**
- Admin user not created
- Wrong credentials
- Database migration not applied

**Fix:**
```bash
# On VPS
docker exec agentguard-backend python create_overseex_admin.py
```

### API Not Responding

**Test:**
```bash
pytest tests/deployment/test_production.py::TestAPIEndpoints::test_api_health -v
```

**Fix:**
```bash
# Check backend logs
docker logs agentguard-backend --tail 100

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

## Test Results Interpretation

### All Tests Pass ✅
Your deployment is healthy and properly configured.

### SSL Tests Fail ❌
- Check certificate expiration: `certbot certificates`
- Renew certificates: `certbot renew`
- Verify nginx configuration

### Mixed Content Tests Fail ❌
- Containers have old JavaScript bundles with HTTP URLs
- Need to rebuild with `--no-cache` flag
- Verify `NEXT_PUBLIC_API_URL` build arg in docker-compose.prod.yml

### Authentication Tests Fail ❌
- Check database connection
- Verify admin user exists
- Check backend logs for errors

### API Tests Fail ❌
- Check backend service status
- Verify database migrations applied
- Check environment variables

## Adding New Tests

Example test structure:

```python
class TestNewFeature:
    """Test description"""
    
    @pytest.fixture
    def setup_data(self):
        """Fixture for test setup"""
        return {"key": "value"}
    
    def test_feature_works(self, setup_data):
        """Test that feature works correctly"""
        response = requests.get(f"{PROD_CONFIG['api_url']}/api/v1/feature")
        assert response.status_code == 200
        assert "expected_key" in response.json()
```

## Monitoring

Run tests periodically to catch issues:

```bash
# Add to crontab for hourly checks
0 * * * * cd /path/to/project && pytest tests/deployment/ -v --tb=line >> /var/log/deployment-tests.log 2>&1
```

## Support

If tests fail and you can't resolve:
1. Check VPS logs: `docker-compose -f docker-compose.prod.yml logs --tail=100`
2. Check individual service logs: `docker logs agentguard-backend --tail=100`
3. Verify all services running: `docker ps`
4. Check disk space: `df -h`
5. Check memory: `free -h`
