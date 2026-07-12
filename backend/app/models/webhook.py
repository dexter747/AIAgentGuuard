"""
Webhook model for database storage
"""
from sqlalchemy import Column, String, ARRAY, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    url = Column(String, nullable=False)
    events = Column(ARRAY(String), nullable=False)  # List of event types
    is_active = Column(Boolean, default=True)
    secret = Column(String)  # For webhook signature verification
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    organization = relationship("Organization")
