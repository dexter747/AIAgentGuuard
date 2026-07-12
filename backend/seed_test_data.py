"""
Seed script to create initial test data
"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.user import User, Organization, UserRole
from app.core.jwt import get_password_hash
import secrets

db = SessionLocal()

try:
    # Check if data already exists
    existing_org = db.query(Organization).first()
    if existing_org:
        print("✅ Database already has data")
        print(f"   Organization: {existing_org.name}")
        user = db.query(User).filter(User.org_id == existing_org.id).first()
        if user:
            print(f"   User: {user.email}")
            print(f"   API Key: {user.api_key}")
        sys.exit(0)
    
    # Create test organization
    org = Organization(name="Test Organization")
    db.add(org)
    db.flush()
    print(f"✅ Created organization: {org.name}")
    
    # Create test user
    api_key = f"ag_live_{secrets.token_hex(24)}"
    # Use a shorter password to avoid bcrypt 72 byte limit
    password = "test123"
    user = User(
        org_id=org.id,
        email="test@agentguard.ai",
        password_hash=get_password_hash(password),
        role=UserRole.ADMIN,
        api_key=api_key
    )
    db.add(user)
    db.commit()
    
    print(f"✅ Created user: {user.email}")
    print(f"   Password: {password}")
    print(f"   API Key: {api_key}")
    print()
    print("🎉 Seed data created successfully!")
    print()
    print("You can now:")
    print(f"  - Login with email: test@agentguard.ai / password123")
    print(f"  - Use API key: {api_key}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
