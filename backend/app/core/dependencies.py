"""
Dependency functions for FastAPI
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models import User, APIKey
from app.services.rate_limiter import RateLimiter


async def get_current_org(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> UUID:
    """
    Verify API key and return organization ID
    Also enforces rate limiting
    """
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key"
        )
    
    # Find API key
    api_key = db.query(APIKey).filter(APIKey.key == x_api_key).first()
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Check if key is valid
    if not api_key.is_valid:
        raise HTTPException(
            status_code=401,
            detail="API key is inactive or expired"
        )
    
    # Check rate limits
    is_allowed, details = RateLimiter.check_rate_limit(
        str(api_key.id),
        api_key.rate_limit_per_minute,
        api_key.rate_limit_per_hour,
        api_key.rate_limit_per_day
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=details.get("error"),
            headers={"Retry-After": "60"}
        )
    
    # Update last used timestamp
    api_key.last_used_at = datetime.utcnow()
    db.commit()
    
    return api_key.org_id
