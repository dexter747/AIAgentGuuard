"""
API Key model for access management
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid
import secrets

from app.core.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    key_prefix = Column(String(20), nullable=False)  # e.g., "ag_live_abc123"
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("User")
    
    @staticmethod
    def generate_key(prefix: str = "ag_live") -> tuple[str, str]:
        """Generate a new API key with prefix and full key"""
        random_part = secrets.token_urlsafe(32)
        key = f"{prefix}_{random_part}"
        # Create display prefix (first 8 chars after prefix)
        key_prefix = f"{prefix}_{random_part[:8]}"
        return key, key_prefix
    
    @property
    def is_valid(self) -> bool:
        """Check if key is valid (active and not expired)"""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
