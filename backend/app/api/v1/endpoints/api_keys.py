"""
API Key management endpoints with database integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import secrets

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api-keys")


class APIKeyCreate(BaseModel):
    name: str


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str
    created: str
    lastUsed: Optional[str] = None
    status: str


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all API keys for the current user.
    
    Note: In production, API keys should be stored in a separate table
    with proper key management and rotation policies.
    """
    # For now, return the user's current API key
    # TODO: Implement separate APIKey model for multiple keys
    return [
        {
            "id": str(current_user.id),
            "name": "Primary API Key",
            "key": current_user.api_key if current_user.api_key else "ag_live_xxxxxxxxxxxxx",
            "created": current_user.created_at.isoformat() if current_user.created_at else "",
            "lastUsed": current_user.last_login.isoformat() if hasattr(current_user, 'last_login') and current_user.last_login else None,
            "status": "active"
        }
    ]


@router.post("/", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new API key.
    
    Note: Currently regenerates the user's primary API key.
    In production, implement a separate APIKey model for multiple keys.
    """
    # Generate new API key
    new_key = f"ag_live_{secrets.token_hex(24)}"
    
    # Update user's API key
    current_user.api_key = new_key
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": str(current_user.id),
        "name": key_data.name,
        "key": new_key,
        "created": datetime.utcnow().isoformat(),
        "lastUsed": None,
        "status": "active"
    }


@router.post("/{key_id}/revoke")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an API key.
    
    Note: Currently not implemented for user's primary key.
    TODO: Implement with separate APIKey model.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="API key revocation not yet implemented. Use delete or regenerate instead."
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an API key.
    
    Note: Cannot delete the user's primary API key.
    TODO: Implement with separate APIKey model for multiple keys.
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot delete primary API key. Use regenerate to create a new one."
    )
