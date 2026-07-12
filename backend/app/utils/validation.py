"""
Input validation and sanitization utilities for security.
Prevents XSS, SQL injection, and other injection attacks.
"""
import re
import html
from typing import Any, Dict, Optional, List
import bleach
from pydantic import validator


# Allowed HTML tags for rich text fields (very restrictive)
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'code', 'pre']
ALLOWED_ATTRIBUTES = {}


def sanitize_html(text: str) -> str:
    """
    Remove all HTML tags and potentially dangerous content.
    Use for user-generated content that shouldn't contain HTML.
    """
    if not text:
        return text
    
    # Remove all HTML tags
    clean_text = bleach.clean(text, tags=[], strip=True)
    
    # HTML encode remaining special characters
    clean_text = html.escape(clean_text)
    
    return clean_text


def sanitize_rich_text(text: str) -> str:
    """
    Allow only safe HTML tags in rich text content.
    Use for fields like descriptions that may contain formatting.
    """
    if not text:
        return text
    
    # Clean with allowed tags only
    clean_text = bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return clean_text


def validate_agent_name(name: str) -> str:
    """
    Validate and sanitize agent names.
    Only allows alphanumeric, spaces, hyphens, underscores.
    """
    if not name or len(name) < 1 or len(name) > 100:
        raise ValueError("Agent name must be between 1 and 100 characters")
    
    # Remove any HTML
    name = sanitize_html(name)
    
    # Only allow safe characters
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        raise ValueError("Agent name can only contain letters, numbers, spaces, hyphens, and underscores")
    
    return name.strip()


def validate_email(email: str) -> str:
    """Validate email format."""
    if not email:
        raise ValueError("Email is required")
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email.lower().strip()


def validate_url(url: str, schemes: List[str] = ['http', 'https']) -> str:
    """
    Validate URL format and scheme.
    Prevents javascript:, data:, and other dangerous schemes.
    """
    if not url:
        raise ValueError("URL is required")
    
    # Check for allowed schemes only
    if not any(url.lower().startswith(f"{scheme}://") for scheme in schemes):
        raise ValueError(f"URL must use one of: {', '.join(schemes)}")
    
    # Prevent common XSS patterns
    dangerous_patterns = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'<script',
        r'onerror=',
        r'onload='
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            raise ValueError("URL contains potentially dangerous content")
    
    return url


def sanitize_json_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitize JSON metadata to prevent XSS in stored data.
    Recursively cleans all string values.
    """
    if metadata is None:
        return None
    
    if isinstance(metadata, dict):
        return {
            key: sanitize_json_metadata(value)
            for key, value in metadata.items()
        }
    elif isinstance(metadata, list):
        return [sanitize_json_metadata(item) for item in metadata]
    elif isinstance(metadata, str):
        # Sanitize string values
        return sanitize_html(metadata)
    else:
        # Return numbers, booleans, None as-is
        return metadata


def validate_trace_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize trace metadata.
    Ensures no malicious content in stored trace data.
    """
    if not metadata:
        return {}
    
    # Limit size to prevent DoS
    if len(str(metadata)) > 100000:  # 100KB limit
        raise ValueError("Metadata too large (max 100KB)")
    
    # Sanitize all string values
    sanitized = sanitize_json_metadata(metadata)
    
    return sanitized


def validate_pagination_params(limit: int = 50, offset: int = 0) -> tuple:
    """
    Validate pagination parameters to prevent abuse.
    Returns safe (limit, offset) tuple.
    """
    # Limit to reasonable range
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    
    # Prevent huge offsets (use cursor pagination instead)
    if offset > 10000:
        raise ValueError("Offset too large. Use cursor-based pagination for large datasets.")
    
    return (limit, offset)


def validate_webhook_url(url: str) -> str:
    """
    Validate webhook URL with additional security checks.
    Prevents SSRF by blocking private IPs.
    """
    import socket
    from urllib.parse import urlparse
    
    # Basic URL validation
    url = validate_url(url, schemes=['https'])  # HTTPS only for webhooks
    
    # Parse URL
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    if not hostname:
        raise ValueError("Invalid webhook URL")
    
    # Resolve hostname to IP
    try:
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        raise ValueError("Could not resolve webhook hostname")
    
    # Block private/local IPs to prevent SSRF
    private_ranges = [
        r'^127\.',           # Localhost
        r'^10\.',            # Private A
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Private B
        r'^192\.168\.',      # Private C
        r'^169\.254\.',      # Link-local
        r'^::1$',            # IPv6 localhost
        r'^fc00:',           # IPv6 private
        r'^fe80:',           # IPv6 link-local
    ]
    
    for pattern in private_ranges:
        if re.match(pattern, ip):
            raise ValueError("Webhook URL cannot point to private/internal networks")
    
    return url


# Pydantic validators for use in models

class SafeString(str):
    """String type that auto-sanitizes HTML."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        return sanitize_html(v)


class SafeRichText(str):
    """String type that allows limited HTML formatting."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        return sanitize_rich_text(v)
