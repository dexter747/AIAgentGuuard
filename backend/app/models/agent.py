"""
Agent model
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    endpoint_url = Column(String(500), nullable=True)
    health_check_interval = Column(Integer, default=300)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="agents")
    traces = relationship("Trace", back_populates="agent")
    tests = relationship("Test", back_populates="agent")
    health_checks = relationship("HealthCheck", back_populates="agent")
