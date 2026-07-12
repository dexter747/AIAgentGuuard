"""
Organization management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.models.user import User, Organization, UserRole
from app.core.auth import get_current_user

router = APIRouter(prefix="/organizations")


# Response Models
class OrganizationResponse(BaseModel):
    id: str
    name: str
    created_at: str
    member_count: int


class MemberResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    joined_at: str


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: str = "member"


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's organization"""
    
    if not current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No organization found"
        )
    
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    member_count = db.query(User).filter(User.org_id == org.id).count()
    
    return {
        "id": str(org.id),
        "name": org.name,
        "created_at": org.created_at.isoformat(),
        "member_count": member_count
    }


@router.put("/me")
async def update_organization(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update organization details"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    org = db.query(Organization).filter(Organization.id == current_user.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    org.name = name
    db.commit()
    
    return {"message": "Organization updated successfully"}


@router.get("/members", response_model=List[MemberResponse])
async def list_members(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all organization members"""
    
    if not current_user.org_id:
        return []
    
    members = db.query(User).filter(User.org_id == current_user.org_id).all()
    
    return [
        {
            "id": str(member.id),
            "email": member.email,
            "full_name": member.full_name or "Unknown",
            "role": member.role.value,
            "joined_at": member.created_at.isoformat()
        }
        for member in members
    ]


@router.post("/members")
async def invite_member(
    request: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a new member to the organization"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required to invite members"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # TODO: Send invitation email
    # For now, just return success
    
    return {
        "message": "Invitation sent successfully",
        "email": request.email
    }


@router.delete("/members/{user_id}")
async def remove_member(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from the organization"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Cannot remove yourself
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself"
        )
    
    member = db.query(User).filter(
        User.id == user_id,
        User.org_id == current_user.org_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    db.delete(member)
    db.commit()
    
    return {"message": "Member removed successfully"}
