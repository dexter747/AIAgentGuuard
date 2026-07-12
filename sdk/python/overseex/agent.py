"""
Agent models and utilities
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Agent:
    """
    Represents an AI agent registered in AgentGuard.
    """
    id: str
    name: str
    endpoint_url: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Agent":
        """Create Agent from API response dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            endpoint_url=data["endpoint_url"],
            description=data.get("description"),
            config=data.get("config"),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
                if data.get("created_at") else None
        )
