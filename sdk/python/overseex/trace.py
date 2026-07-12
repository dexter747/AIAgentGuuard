"""
Trace models and utilities
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TraceStatus(str, Enum):
    """Trace execution status."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    PENDING = "pending"


@dataclass
class Trace:
    """
    Represents an agent execution trace.
    """
    id: str
    agent_id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    status: str
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    token_count: Optional[int] = None
    cost: Optional[float] = None
    created_at: Optional[datetime] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Trace":
        """Create Trace from API response dictionary."""
        # Handle trace_data format from API
        trace_data = data.get("trace_data", {})
        input_data = trace_data.get("input", data.get("input_data", {}))
        output_data = trace_data.get("output", data.get("output_data", {}))
        metadata = trace_data.get("metadata", data.get("metadata", {}))
        
        # Handle duration from different field names
        duration = data.get("total_duration_ms") or data.get("duration_ms")
        
        # Handle cost from string or float
        cost_val = data.get("cost_usd") or data.get("cost")
        cost = float(cost_val) if cost_val else None
        
        return cls(
            id=data["id"],
            agent_id=data["agent_id"],
            input_data=input_data,
            output_data=output_data,
            status=data.get("status", "unknown"),
            error_message=trace_data.get("error") or data.get("error_message"),
            metadata=metadata,
            duration_ms=duration,
            token_count=data.get("token_count"),
            cost=cost,
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
                if data.get("created_at") else None
        )
    
    def is_success(self) -> bool:
        """Check if trace execution was successful."""
        return self.status == TraceStatus.SUCCESS
    
    def is_error(self) -> bool:
        """Check if trace execution had an error."""
        return self.status == TraceStatus.ERROR
