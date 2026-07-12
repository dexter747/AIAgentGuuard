"""
Database seed script - Create admin user and sample data
Run with: python -m backend.scripts.seed_db
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User, Organization, SubscriptionPlan
from app.models.agent import Agent
from app.core.security import get_password_hash
import uuid
from datetime import datetime

def create_admin_user(db: Session):
    """Create admin user"""
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.email == "admin@agentguard.dev").first()
    if existing_admin:
        print("✅ Admin user already exists")
        return existing_admin
    
    # Create admin organization
    admin_org = Organization(
        id=uuid.uuid4(),
        name="AgentGuard Admin",
        plan=SubscriptionPlan.ENTERPRISE,
        created_at=datetime.utcnow()
    )
    db.add(admin_org)
    db.flush()
    
    # Create admin user
    admin_user = User(
        id=uuid.uuid4(),
        org_id=admin_org.id,
        email="admin@agentguard.dev",
        password_hash=get_password_hash("admin123"),  # Change this in production!
        full_name="Admin User",
        is_active=True,
        is_verified=True,
        is_admin=True,
        created_at=datetime.utcnow()
    )
    db.add(admin_user)
    db.commit()
    
    print("✅ Admin user created:")
    print(f"   Email: admin@agentguard.dev")
    print(f"   Password: admin123")
    print(f"   ⚠️  CHANGE PASSWORD IN PRODUCTION!")
    
    return admin_user


def create_sample_data(db: Session):
    """Create sample organizations and users for testing"""
    
    # Check if sample data already exists
    existing_orgs = db.query(Organization).filter(Organization.name.like("Sample%")).count()
    if existing_orgs > 0:
        print("✅ Sample data already exists")
        return
    
    print("\n📊 Creating sample data...")
    
    # Create 3 sample organizations
    sample_orgs = []
    for i in range(1, 4):
        org = Organization(
            id=uuid.uuid4(),
            name=f"Sample Organization {i}",
            plan=SubscriptionPlan.PRO if i == 1 else SubscriptionPlan.FREE,
            created_at=datetime.utcnow()
        )
        db.add(org)
        sample_orgs.append(org)
    
    db.flush()
    
    # Create users for each organization
    user_count = 0
    for org in sample_orgs:
        for j in range(1, 4):
            user = User(
                id=uuid.uuid4(),
                org_id=org.id,
                email=f"user{user_count+1}@example.com",
                password_hash=get_password_hash("password123"),
                full_name=f"Test User {user_count+1}",
                is_active=True,
                is_verified=True,
                is_admin=False,
                created_at=datetime.utcnow()
            )
            db.add(user)
            user_count += 1
            
            # Create 2 agents for first user of each org
            if j == 1:
                for k in range(1, 3):
                    agent = Agent(
                        id=uuid.uuid4(),
                        name=f"Sample Agent {k} - {org.name}",
                        org_id=org.id,
                        endpoint_url=f"http://agent{k}.example.com",
                        created_at=datetime.utcnow()
                    )
                    db.add(agent)
    
    db.commit()
    print(f"✅ Created {len(sample_orgs)} organizations")
    print(f"✅ Created {user_count} users")
    print(f"✅ Created {len(sample_orgs) * 2} agents")


def main():
    """Main seed function"""
    print("🌱 Seeding database...")
    
    # Create database tables if they don't exist
    from app.models.user import Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create admin user
        create_admin_user(db)
        
        # Create sample data
        create_sample_data(db)
        
        print("\n✅ Database seeded successfully!")
        print("\n🔐 Admin Login:")
        print("   URL: http://localhost:3001")
        print("   Email: admin@agentguard.dev")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
