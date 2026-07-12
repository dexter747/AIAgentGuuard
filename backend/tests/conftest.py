"""
Pytest configuration and fixtures for backend testing.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from main import app
from app.core.database import Base, get_db
from app.models.user import User, Organization
from app.models.agent import Agent
from app.models.api_key import APIKey
from app.core.security import get_password_hash, create_access_token
import uuid


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_organization(db: Session) -> Organization:
    """Create a test organization."""
    org = Organization(
        id=str(uuid.uuid4()),
        name="Test Organization",
        subscription_tier="pro"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_user(db: Session, test_organization: Organization) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_api_key(db: Session, test_user: User, test_organization: Organization) -> APIKey:
    """Create a test API key."""
    api_key = APIKey(
        id=str(uuid.uuid4()),
        name="Test API Key",
        key_hash=get_password_hash("test_api_key_12345"),
        user_id=test_user.id,
        organization_id=test_organization.id,
        is_active=True
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key


@pytest.fixture
def test_agent(db: Session, test_user: User, test_organization: Organization) -> Agent:
    """Create a test agent."""
    agent = Agent(
        id=str(uuid.uuid4()),
        name="Test Agent",
        description="A test agent",
        user_id=test_user.id,
        organization_id=test_organization.id,
        status="active"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Generate authentication headers with JWT token."""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def api_key_headers(test_api_key: APIKey) -> dict:
    """Generate headers with API key."""
    return {"X-API-Key": "test_api_key_12345"}


@pytest.fixture
def admin_user(db: Session, test_organization: Organization) -> User:
    """Create an admin user."""
    user = User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        organization_id=test_organization.id,
        is_active=True,
        is_verified=True,
        is_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis for caching tests."""
    from unittest.mock import MagicMock
    
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None
    mock_redis_client.set.return_value = True
    mock_redis_client.delete.return_value = 1
    
    monkeypatch.setattr("app.services.cache_service.cache.redis_client", mock_redis_client)
    return mock_redis_client
