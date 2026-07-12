"""
Additional security measures for user management.
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict
import asyncio

# Track registration attempts by IP
registration_attempts: Dict[str, list] = defaultdict(list)
login_attempts: Dict[str, list] = defaultdict(list)

# Configuration
MAX_REGISTRATIONS_PER_IP_PER_HOUR = 3
MAX_LOGIN_ATTEMPTS_PER_EMAIL = 5
LOGIN_LOCKOUT_MINUTES = 15


def is_ip_rate_limited(ip_address: str) -> bool:
    """
    Check if an IP has exceeded registration rate limits.
    Prevents automated abuse from same IP.
    """
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    
    # Clean old attempts
    registration_attempts[ip_address] = [
        timestamp for timestamp in registration_attempts[ip_address]
        if timestamp > one_hour_ago
    ]
    
    # Check limit
    if len(registration_attempts[ip_address]) >= MAX_REGISTRATIONS_PER_IP_PER_HOUR:
        return True
    
    # Record this attempt
    registration_attempts[ip_address].append(now)
    return False


def is_login_rate_limited(email: str) -> tuple[bool, int]:
    """
    Check if login attempts for an email have been exceeded.
    Returns (is_limited, remaining_lockout_minutes)
    """
    now = datetime.utcnow()
    lockout_period = now - timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
    
    # Clean old attempts (older than lockout period)
    login_attempts[email] = [
        timestamp for timestamp in login_attempts[email]
        if timestamp > lockout_period
    ]
    
    # Check if locked out
    if len(login_attempts[email]) >= MAX_LOGIN_ATTEMPTS_PER_EMAIL:
        oldest_attempt = min(login_attempts[email])
        unlock_time = oldest_attempt + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
        remaining_minutes = int((unlock_time - now).total_seconds() / 60)
        return True, max(0, remaining_minutes)
    
    # Record this attempt
    login_attempts[email].append(now)
    return False, 0


def record_successful_login(email: str):
    """Clear failed login attempts after successful login"""
    if email in login_attempts:
        del login_attempts[email]


# Periodic cleanup task (run this in background)
async def cleanup_rate_limit_data():
    """Clean up old rate limit data every hour"""
    while True:
        await asyncio.sleep(3600)  # 1 hour
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Clean registration attempts
        for ip in list(registration_attempts.keys()):
            registration_attempts[ip] = [
                t for t in registration_attempts[ip] if t > one_hour_ago
            ]
            if not registration_attempts[ip]:
                del registration_attempts[ip]
        
        # Clean login attempts
        lockout_period = now - timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
        for email in list(login_attempts.keys()):
            login_attempts[email] = [
                t for t in login_attempts[email] if t > lockout_period
            ]
            if not login_attempts[email]:
                del login_attempts[email]
