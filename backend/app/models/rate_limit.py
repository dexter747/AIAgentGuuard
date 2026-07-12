"""
Rate limit tracking model
"""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class RateLimit(Base):
    __tablename__ = "rate_limits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Time windows
    window_type = Column(String(20), nullable=False)  # 'minute', 'hour', 'day'
    window_start = Column(DateTime, nullable=False, index=True)
    
    # Counts
    request_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RateLimit {self.api_key_id} {self.window_type}={self.request_count}>"
