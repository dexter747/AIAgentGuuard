"""
Authentication dependencies
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.user import User, Organization
from app.core.rate_limiter import rate_limiter, get_rate_limit_for_plan
from app.core.jwt import verify_token


async def get_current_user(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify JWT token or API key and return current user
    
    Supports:
    1. JWT Token: Authorization: Bearer <jwt_token>
    2. API Key: X-API-Key: ag_live_xxx
    3. API Key: Authorization: Bearer ag_live_xxx
    """
    token = None
    api_key = None
    
    # Check X-API-Key header
    if x_api_key:
        api_key = x_api_key
    
    # Check Authorization header
    if authorization and authorization.startswith("Bearer "):
        token_or_key = authorization.replace("Bearer ", "")
        
        # Determine if it looks like a JWT (has 3 parts separated by dots)
        is_jwt_format = token_or_key.count('.') == 2
        
        if is_jwt_format:
            # Try to decode as JWT
            payload = verify_token(token_or_key)
            if payload:
                # It's a valid JWT token
                user_id = payload.get("sub")
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid token: missing subject")
                
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise HTTPException(status_code=401, detail="User not found")
                
                if not user.is_active:
                    raise HTTPException(status_code=401, detail="User account is inactive")
                
                return user
            else:
                # JWT validation failed
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid or expired JWT token. Please log in again."
                )
        else:
            # Not JWT format, treat as API key
            api_key = token_or_key
    
    # If we have an API key, look up user
    if api_key:
        user = db.query(User).filter(User.api_key == api_key).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Check rate limit for API key usage
        org = db.query(Organization).filter(Organization.id == user.org_id).first()
        limit = get_rate_limit_for_plan(org.plan.value)
        
        is_allowed, rate_info = rate_limiter.check_rate_limit(api_key, limit=limit)
        
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": rate_info["reset_at"]
                }
            )
        
        return user
    
    raise HTTPException(
        status_code=401,
        detail="Missing authentication. Provide JWT token or API key"
    )
