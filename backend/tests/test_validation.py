"""
Unit tests for input validation utilities.
"""
import pytest
from app.utils.validation import (
    sanitize_html,
    sanitize_rich_text,
    validate_agent_name,
    validate_email,
    validate_url,
    sanitize_json_metadata,
    validate_webhook_url,
    validate_pagination_params
)


class TestSanitization:
    """Test HTML and input sanitization."""
    
    def test_sanitize_html_removes_tags(self):
        """Test that HTML tags are removed."""
        dirty = "<script>alert('xss')</script>Hello"
        clean = sanitize_html(dirty)
        
        assert "<script>" not in clean
        assert "alert" not in clean or "&lt;script&gt;" in clean
    
    def test_sanitize_html_escapes_chars(self):
        """Test that special characters are escaped."""
        dirty = "<b>Bold</b> & <i>Italic</i>"
        clean = sanitize_html(dirty)
        
        # Should not contain raw HTML
        assert "<b>" not in clean
        assert "<i>" not in clean
    
    def test_sanitize_rich_text_allows_safe_tags(self):
        """Test that safe tags are preserved in rich text."""
        text = "<p>Paragraph</p><strong>Bold</strong><script>bad</script>"
        clean = sanitize_rich_text(text)
        
        # Should keep safe tags
        assert "<p>" in clean or "Paragraph" in clean
        # Should remove dangerous tags
        assert "<script>" not in clean
    
    def test_sanitize_json_metadata_recursive(self):
        """Test recursive JSON sanitization."""
        dirty = {
            "name": "<script>xss</script>",
            "nested": {
                "value": "<b>test</b>"
            },
            "list": ["<i>item1</i>", "<i>item2</i>"],
            "safe": 123
        }
        
        clean = sanitize_json_metadata(dirty)
        
        # Scripts should be removed
        assert "<script>" not in str(clean)
        # Numbers should be preserved
        assert clean["safe"] == 123
        # Structure should be preserved
        assert "nested" in clean
        assert isinstance(clean["list"], list)


class TestValidation:
    """Test validation functions."""
    
    def test_validate_agent_name_valid(self):
        """Test valid agent names."""
        valid_names = [
            "My Agent",
            "Agent-123",
            "Test_Agent_1"
        ]
        
        for name in valid_names:
            result = validate_agent_name(name)
            assert result == name.strip()
    
    def test_validate_agent_name_invalid(self):
        """Test invalid agent names."""
        with pytest.raises(ValueError):
            validate_agent_name("")  # Empty
        
        with pytest.raises(ValueError):
            validate_agent_name("a" * 101)  # Too long
        
        with pytest.raises(ValueError):
            validate_agent_name("Agent<script>")  # Invalid chars
    
    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.user@example.co.uk",
            "user+tag@example.com"
        ]
        
        for email in valid_emails:
            result = validate_email(email)
            assert "@" in result
            assert result == email.lower().strip()
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user@.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError):
                validate_email(email)
    
    def test_validate_url_valid(self):
        """Test valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.com/path",
            "https://subdomain.example.com:8080"
        ]
        
        for url in valid_urls:
            result = validate_url(url)
            assert result == url
    
    def test_validate_url_dangerous_schemes(self):
        """Test that dangerous URL schemes are blocked."""
        dangerous_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "vbscript:msgbox('xss')"
        ]
        
        for url in dangerous_urls:
            with pytest.raises(ValueError):
                validate_url(url)
    
    def test_validate_url_xss_patterns(self):
        """Test that XSS patterns in URLs are blocked."""
        xss_urls = [
            "https://example.com/<script>alert(1)</script>",
            "https://example.com?onerror=alert(1)"
        ]
        
        for url in xss_urls:
            with pytest.raises(ValueError):
                validate_url(url)
    
    def test_validate_pagination_params(self):
        """Test pagination parameter validation."""
        # Valid params
        limit, offset = validate_pagination_params(50, 100)
        assert limit == 50
        assert offset == 100
        
        # Limit too high
        limit, offset = validate_pagination_params(1000, 0)
        assert limit == 100  # Should be capped
        
        # Negative values
        limit, offset = validate_pagination_params(-10, -5)
        assert limit >= 1
        assert offset >= 0
        
        # Offset too high
        with pytest.raises(ValueError):
            validate_pagination_params(50, 20000)
    
    def test_validate_webhook_url_https_required(self):
        """Test that webhook URLs must be HTTPS."""
        with pytest.raises(ValueError):
            validate_webhook_url("http://example.com/webhook")
        
        # HTTPS should work
        result = validate_webhook_url("https://example.com/webhook")
        assert result.startswith("https://")
    
    def test_validate_webhook_url_blocks_private_ips(self):
        """Test that webhook URLs to private IPs are blocked (SSRF prevention)."""
        private_urls = [
            "https://127.0.0.1/webhook",  # Localhost
            "https://10.0.0.1/webhook",   # Private
            "https://192.168.1.1/webhook" # Private
        ]
        
        for url in private_urls:
            with pytest.raises(ValueError, match="private"):
                validate_webhook_url(url)


class TestMetadataValidation:
    """Test trace metadata validation."""
    
    def test_validate_trace_metadata_size_limit(self):
        """Test that metadata size is limited."""
        from app.utils.validation import validate_trace_metadata
        
        # Create large metadata
        large_metadata = {"data": "x" * 200000}  # 200KB
        
        with pytest.raises(ValueError, match="too large"):
            validate_trace_metadata(large_metadata)
    
    def test_validate_trace_metadata_sanitizes(self):
        """Test that metadata is sanitized."""
        from app.utils.validation import validate_trace_metadata
        
        dirty_metadata = {
            "user_input": "<script>alert('xss')</script>",
            "safe_value": 123
        }
        
        clean = validate_trace_metadata(dirty_metadata)
        
        assert "<script>" not in str(clean)
        assert clean["safe_value"] == 123
