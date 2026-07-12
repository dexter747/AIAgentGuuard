"""
Authentication endpoints - simplified
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth")


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    return {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "token_type": "bearer",
        "user": {
            "id": "new-user",
            "email": request.email,
            "full_name": request.full_name
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user"""
    return {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "token_type": "bearer",
        "user": {
            "id": "user-1",
            "email": request.email,
            "full_name": "Demo User"
        }
    }


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email"""
    return {
        "success": True,
        "message": "Password reset email sent"
    }


@router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    """Reset password"""
    return {
        "success": True,
        "message": "Password reset successful"
    }


@router.get("/me")
async def get_current_user():
    """Get current user"""
    return {
        "id": "user-1",
        "email": "demo@example.com",
        "full_name": "Demo User"
    }
