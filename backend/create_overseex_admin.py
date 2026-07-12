"""
Create admin@overseex.com user
Run with: python create_overseex_admin.py
"""
import sys
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, Organization, SubscriptionPlan
from app.core.security import get_password_hash
import uuid
from datetime import datetime

def create_overseex_admin():
    """Create admin@overseex.com user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@overseex.com").first()
        if existing_admin:
            print("✅ Admin user admin@overseex.com already exists")
            print(f"   User ID: {existing_admin.id}")
            print(f"   Organization: {existing_admin.org_id}")
            return
        
        # Create admin organization (no billing plan for super admin)
        admin_org = Organization(
            id=uuid.uuid4(),
            name="OverseeX Admin",
            plan=None,  # Super admin has no billing plan
            stripe_customer_id=None,  # No Stripe for super admin
            created_at=datetime.utcnow()
        )
        db.add(admin_org)
        db.flush()
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            org_id=admin_org.id,
            email="admin@overseex.com",
            password_hash=get_password_hash("Admin@1234"),
            full_name="OverseeX Admin",
            is_active=True,
            is_verified=True,
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully:")
        print(f"   Email: admin@overseex.com")
        print(f"   Password: Admin@1234")
        print(f"   User ID: {admin_user.id}")
        print(f"   Organization ID: {admin_org.id}")
        print(f"   Plan: None (Super Admin - No Billing)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_overseex_admin()
