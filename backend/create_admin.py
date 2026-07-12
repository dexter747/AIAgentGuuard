#!/usr/bin/env python3
"""Create admin user for OverseeX"""
from app.core.database import SessionLocal
from app.models.user import User, Organization, UserRole
from app.core.security import get_password_hash
import uuid

db = SessionLocal()

# Check if admin exists
admin = db.query(User).filter(User.email == "admin@agentguard.ai").first()

if admin:
    print("✅ Admin user already exists:")
    print(f"   Email: admin@agentguard.ai")
    print(f"   Password: admin123")
    print(f"   Organization: {admin.organization.name}")
else:
    # Get or create admin org
    org = db.query(Organization).filter(Organization.name == "AgentGuard Admin").first()
    if not org:
        org = Organization(name="AgentGuard Admin")
        db.add(org)
        db.flush()
    
    # Create admin user
    admin = User(
        email="admin@agentguard.ai",
        password_hash=get_password_hash("admin123"),
        full_name="Admin User",
        org_id=org.id,
        role=UserRole.ADMIN,
        is_admin=True,
        api_key=f"ag_live_admin_{uuid.uuid4().hex[:24]}"
    )
    db.add(admin)
    db.commit()
    
    print("✅ Admin user created successfully!")
    print(f"   Email: admin@agentguard.ai")
    print(f"   Password: admin123")
    print(f"   Organization: {org.name}")

db.close()
