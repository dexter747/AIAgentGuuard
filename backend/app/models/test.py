"""
Test and TestRun models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Test(Base):
    __tablename__ = "tests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(Text, nullable=False)  # pytest code
    source_trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", back_populates="tests")
    test_runs = relationship("TestRun", back_populates="test")


class TestRun(Base):
    __tablename__ = "test_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.id"), nullable=False)
    status = Column(String(50), nullable=True)  # pending, running, passed, failed
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    test = relationship("Test", back_populates="test_runs")
