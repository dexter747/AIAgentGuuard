"""
HealthCheck model
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class HealthCheck(Base):
    __tablename__ = "health_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    
    # Health check configuration
    endpoint = Column(String(500), nullable=False)  # URL to check
    interval_minutes = Column(Integer, default=5, nullable=False)  # Check every N minutes
    timeout_seconds = Column(Integer, default=30, nullable=False)  # Request timeout
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Enable/disable check
    
    # Latest probe results
    probe_region = Column(String(50), nullable=True)  # us-east-1, eu-west-1
    status = Column(String(50), nullable=True)  # healthy, degraded, unhealthy
    response_time_ms = Column(Integer, nullable=True)
    response_body = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="health_checks")
