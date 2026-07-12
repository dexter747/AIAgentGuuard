"""
Users API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.core.auth import get_current_user

router = APIRouter()


# Pydantic Models
class UserProfile(BaseModel):
    """User profile data"""
    id: str
    email: str
    name: str
    organization_id: Optional[str] = None
    role: str
    created_at: str
    updated_at: str
    avatar_url: Optional[str] = None
    settings: Optional[dict] = None


class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[dict] = None


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user = Depends(get_current_user)):
    """
    Get current user's profile
    
    Returns:
        UserProfile: Current user's profile information
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.email.split('@')[0].title(),  # Use email prefix as name
        "organization_id": str(current_user.org_id) if current_user.org_id else None,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        "created_at": current_user.created_at.isoformat() if current_user.created_at else datetime.utcnow().isoformat(),
        "updated_at": current_user.created_at.isoformat() if current_user.created_at else datetime.utcnow().isoformat(),
        "avatar_url": None,
        "settings": {
            "notifications": True,
            "theme": "dark",
            "language": "en"
        }
    }


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    request: UpdateProfileRequest,
    current_user = Depends(get_current_user)
):
    """
    Update current user's profile
    
    Args:
        request: Profile update data
        
    Returns:
        UserProfile: Updated user profile
    """
    # TODO: Update name and avatar in database (need to add fields to User model)
    updated_data = {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": request.name if request.name else current_user.email.split('@')[0].title(),
        "organization_id": str(current_user.org_id) if current_user.org_id else None,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        "created_at": current_user.created_at.isoformat() if current_user.created_at else datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "avatar_url": request.avatar_url,
        "settings": request.settings if request.settings else {
            "notifications": True,
            "theme": "dark",
            "language": "en"
        }
    }
    
    return updated_data


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user = Depends(get_current_user)):
    """
    Delete current user's account
    
    This will permanently delete the user account and all associated data.
    """
    # TODO: Implement account deletion
    # 1. Delete user's agents
    # 2. Delete user's traces
    # 3. Delete user's API keys
    # 4. Delete user from organization
    # 5. Delete user account
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Account deletion not yet implemented"
    )
