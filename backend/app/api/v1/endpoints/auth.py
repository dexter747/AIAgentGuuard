"""
Authentication endpoints with database integration
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import delete, text
from pydantic import BaseModel, EmailStr
from typing import Optional
import os

from app.core.database import get_db
from app.models.user import User, Organization, UserRole
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token
)
from app.utils.email_validator import validate_email_for_signup, is_disposable_email
from app.utils.security import (
    is_ip_rate_limited,
    is_login_rate_limited,
    record_successful_login
)
import secrets

router = APIRouter(prefix="/auth")


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str


class RegisterResponse(BaseModel):
    success: bool
    message: str
    email: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=RegisterResponse)
async def register(
    request_data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user and organization"""
    
    # Check IP rate limiting
    client_ip = request.client.host if request.client else "unknown"
    if is_ip_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Validate email (blocks disposable addresses)
    validate_email_for_signup(request_data.email, allow_disposable=False)
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create organization
    org = Organization(name=request_data.organization_name)
    db.add(org)
    db.flush()
    
    # Generate API key and verification token
    api_key = f"ag_live_{secrets.token_hex(24)}"
    verification_token = secrets.token_urlsafe(32)
    
    # Create user
    user = User(
        org_id=org.id,
        email=request_data.email,
        password_hash=get_password_hash(request_data.password),
        full_name=request_data.full_name,
        role=UserRole.ADMIN,
        api_key=api_key,
        email_verified=False,
        email_verification_token=verification_token
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email
    email_sent = False
    try:
        from app.services.email_service import EmailService
        email_service = EmailService()
        email_sent = email_service.send_confirmation_email(
            to_email=user.email,
            user_name=user.full_name or user.email.split('@')[0],
            confirmation_token=verification_token
        )
        if email_sent:
            import logging
            logging.info(f"Verification email sent to {user.email}")
            # In development mode, also log the verification link
            import os
            if os.getenv("ENVIRONMENT", "development") == "development":
                verification_url = f"{os.getenv('APP_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"
                logging.info(f"\n🔗 DEVELOPMENT MODE - Verification Link:\n{verification_url}\n")
        else:
            import logging
            logging.warning(f"Failed to send verification email to {user.email}")
    except Exception as e:
        # Log error but don't fail registration
        import logging
        logging.error(f"Exception while sending verification email: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
    
    return {
        "success": True,
        "message": "Registration successful! Please check your email to verify your account." if email_sent else "Registration successful! Check console for verification link (dev mode).",
        "email": user.email
    }


@router.post("/login", response_model=TokenResponse)
async def login(request_data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    
    # Check login rate limiting
    is_limited, remaining_minutes = is_login_rate_limited(request_data.email)
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Please try again in {remaining_minutes} minutes."
        )
    
    # Find user
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user or not verify_password(request_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if email is verified (skip for admin users)
    if not user.email_verified and not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before signing in. Check your inbox for the verification link."
        )
    
    # Clear failed attempts on successful login
    record_successful_login(request_data.email)
    
    # Get organization
    org = db.query(Organization).filter(Organization.id == user.org_id).first()
    
    # Generate tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "org_id": str(user.org_id)
    }
    access_token = create_access_token(token_data)
    refresh_token_str = create_refresh_token(token_data)
    
    # Get plan from user_metadata
    user_meta = user.user_metadata or {}
    plan_id = user_meta.get("plan_id", "free_monthly")
    # Extract plan name (e.g., "starter_monthly" -> "Starter")
    plan_name = plan_id.replace("_monthly", "").replace("_annual", "").title()
    if plan_name == "Free":
        plan_name = "Free"

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "org_id": str(user.org_id),
            "org_name": org.name if org else None,
            "role": user.role.value,
            "api_key": user.api_key,
            "is_admin": user.is_admin,
            "plan": plan_name,
            "plan_id": plan_id
        }
    }


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email"""
    user = db.query(User).filter(User.email == request.email).first()
    
    # Don't reveal if user exists or not
    return {
        "success": True,
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with token"""
    
    # Verify token
    payload = verify_token(request.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return {
        "success": True,
        "message": "Password reset successful"
    }


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify user's email address with token"""
    
    # Find user with this verification token
    user = db.query(User).filter(
        User.email_verification_token == request.token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Check if already verified
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Mark email as verified
    user.email_verified = True
    user.email_verification_token = None  # Clear the token
    db.commit()
    
    # Send welcome email
    try:
        from app.services.email_service import EmailService
        email_service = EmailService()
        org = db.query(Organization).filter(Organization.id == user.org_id).first()
        email_service.send_welcome_email(
            to_email=user.email,
            user_name=user.full_name or user.email.split('@')[0],
            organization_name=org.name if org else None
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to send welcome email: {str(e)}")
    
    return {
        "success": True,
        "message": "Email verified successfully! You can now sign in."
    }


@router.post("/resend-verification")
async def resend_verification_email(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """Resend verification email to user"""
    
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    
    # Don't reveal if user exists or not for security
    if not user:
        return {
            "success": True,
            "message": "If the email exists and is unverified, a verification link has been sent."
        }
    
    # Check if already verified
    if user.email_verified:
        return {
            "success": False,
            "message": "Email is already verified. Please sign in."
        }
    
    # Generate new verification token if needed
    if not user.email_verification_token:
        user.email_verification_token = secrets.token_urlsafe(32)
        db.commit()
    
    # Send verification email
    email_sent = False
    try:
        from app.services.email_service import EmailService
        email_service = EmailService()
        email_sent = email_service.send_confirmation_email(
            to_email=user.email,
            user_name=user.full_name or user.email.split('@')[0],
            confirmation_token=user.email_verification_token
        )
        # In development mode, log the verification link
        import os
        if os.getenv("ENVIRONMENT", "development") == "development":
            verification_url = f"{os.getenv('APP_URL', 'http://localhost:3000')}/verify-email?token={user.email_verification_token}"
            import logging
            logging.info(f"\n🔗 RESEND - Verification Link:\n{verification_url}\n")
    except Exception as e:
        import logging
        logging.error(f"Failed to resend verification email: {str(e)}")
    
    return {
        "success": True,
        "message": "If the email exists and is unverified, a verification link has been sent." if email_sent else "Check console for verification link (dev mode)."
    }


@router.get("/me")
async def get_current_user_info(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """Get current authenticated user info from JWT token"""
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    org = db.query(Organization).filter(Organization.id == user.org_id).first()
    
    # Get plan from user_metadata
    user_meta = user.user_metadata or {}
    plan_id = user_meta.get("plan_id", "free_monthly")
    plan_name = plan_id.replace("_monthly", "").replace("_annual", "").title()
    if plan_name == "Free":
        plan_name = "Free"

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "org_id": str(user.org_id),
        "org_name": org.name if org else None,
        "role": user.role.value,
        "api_key": user.api_key,
        "plan": plan_name,
        "plan_id": plan_id
    }


# REMOVED: Dangerous cleanup endpoint
# This endpoint was removed for security reasons.
# If you need to cleanup the database, use direct database access with proper authentication.
# Never expose database truncation via an HTTP endpoint in production.
