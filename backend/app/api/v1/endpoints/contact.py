"""
Contact form endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.contact import ContactQuery
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/contact")


# Request/Response Models
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str


class ContactResponse(BaseModel):
    success: bool
    message: str


class ContactQueryResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    subject: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=ContactResponse)
async def create_contact_query(
    contact: ContactRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new contact query (no authentication required)
    """
    try:
        # Create contact query
        contact_query = ContactQuery(
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            subject=contact.subject,
            message=contact.message,
            is_read=False
        )
        
        db.add(contact_query)
        db.commit()
        db.refresh(contact_query)
        
        return ContactResponse(
            success=True,
            message="Your message has been sent successfully. We'll get back to you soon!"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/queries", response_model=List[ContactQueryResponse])
async def get_contact_queries(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all contact queries (admin only)
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view contact queries"
        )
    
    query = db.query(ContactQuery)
    
    if unread_only:
        query = query.filter(ContactQuery.is_read == False)
    
    queries = query.order_by(ContactQuery.created_at.desc()).offset(skip).limit(limit).all()
    
    return queries


@router.patch("/queries/{query_id}/read")
async def mark_query_as_read(
    query_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a contact query as read (admin only)
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update contact queries"
        )
    
    contact_query = db.query(ContactQuery).filter(ContactQuery.id == query_id).first()
    
    if not contact_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact query not found"
        )
    
    contact_query.is_read = True
    db.commit()
    
    return {"success": True, "message": "Query marked as read"}


@router.delete("/queries/{query_id}")
async def delete_contact_query(
    query_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a contact query (admin only)
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete contact queries"
        )
    
    contact_query = db.query(ContactQuery).filter(ContactQuery.id == query_id).first()
    
    if not contact_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact query not found"
        )
    
    db.delete(contact_query)
    db.commit()
    
    return {"success": True, "message": "Query deleted successfully"}
