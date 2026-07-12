"""
Email validation utilities including disposable email detection.
"""
import re
from typing import Set
import httpx
from fastapi import HTTPException

# Common disposable email domains
DISPOSABLE_DOMAINS: Set[str] = {
    "tempmail.com", "temp-mail.org", "guerrillamail.com", "10minutemail.com",
    "mailinator.com", "throwaway.email", "fakeinbox.com", "maildrop.cc",
    "yopmail.com", "getnada.com", "temp-mail.io", "dispostable.com",
    "trashmail.com", "emailondeck.com", "sharklasers.com", "guerrillamail.info",
    "grr.la", "spam4.me", "mailnesia.com", "tempinbox.com", "10minutemail.net",
    "mintemail.com", "mytemp.email", "mohmal.com", "inboxbear.com",
}

# Regex patterns for suspicious domains
SUSPICIOUS_PATTERNS = [
    r"^temp.*mail",
    r"^fake.*mail",
    r"^trash.*mail",
    r"^disposable",
    r"^\d+min.*mail",
    r"^throw.*away",
]


def is_disposable_email(email: str) -> bool:
    """
    Check if an email address is from a disposable email provider.
    
    Args:
        email: Email address to check
        
    Returns:
        True if email is disposable, False otherwise
    """
    # Extract domain from email
    try:
        domain = email.lower().split('@')[1]
    except IndexError:
        return True  # Invalid email format
    
    # Check against known disposable domains
    if domain in DISPOSABLE_DOMAINS:
        return True
    
    # Check against suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if re.match(pattern, domain):
            return True
    
    return False


async def check_email_deliverability(email: str) -> bool:
    """
    Check if email domain has valid MX records (can receive emails).
    This helps detect fake domains.
    
    Args:
        email: Email address to check
        
    Returns:
        True if domain can receive emails, False otherwise
    """
    try:
        import dns.resolver
        domain = email.split('@')[1]
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0
    except Exception:
        # If we can't verify, allow it (don't want false positives)
        return True


def validate_email_for_signup(email: str, allow_disposable: bool = False) -> None:
    """
    Validate email for signup, checking for disposable addresses.
    
    Args:
        email: Email address to validate
        allow_disposable: Whether to allow disposable emails (for testing)
        
    Raises:
        HTTPException: If email is invalid or disposable
    """
    # Basic format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )
    
    # Check for disposable email
    if not allow_disposable and is_disposable_email(email):
        raise HTTPException(
            status_code=400,
            detail="Disposable email addresses are not allowed. Please use a permanent email address."
        )


# Optional: Use an API service for more comprehensive checking
async def check_email_with_api(email: str, api_key: str | None = None) -> dict:
    """
    Use a third-party API to validate email (optional enhancement).
    
    Services like:
    - EmailListVerify
    - ZeroBounce
    - Hunter.io
    - AbstractAPI
    
    Returns:
        dict with validation results
    """
    if not api_key:
        return {"valid": True, "message": "API validation disabled"}
    
    # Example using AbstractAPI (free tier: 100/month)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://emailvalidation.abstractapi.com/v1/",
                params={"api_key": api_key, "email": email},
                timeout=5.0
            )
            data = response.json()
            
            return {
                "valid": data.get("is_valid_format", {}).get("value", False),
                "disposable": data.get("is_disposable_email", {}).get("value", False),
                "deliverable": data.get("deliverability") == "DELIVERABLE",
                "quality_score": data.get("quality_score", 0),
            }
        except Exception as e:
            # Don't block signup if API fails
            return {"valid": True, "message": f"API check failed: {str(e)}"}
