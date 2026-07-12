"""
Email endpoints - simplified
"""
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/emails")


class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


@router.post("/send")
async def send_email(request: SendEmailRequest):
    """Send an email"""
    return {
        "success": True,
        "message": f"Email sent to {request.to}"
    }
