"""
Traces API endpoints
"""
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/traces")


class TraceData(BaseModel):
    """Trace data schema"""
    agent_id: Optional[str] = None
    trace_data: dict


class TraceResponse(BaseModel):
    id: str
    agent: str
    status: str
    timestamp: str
    duration: str
    steps: int
    confidence: int


@router.get("/", response_model=dict)
async def list_traces():
    """List all traces"""
    return {
        "traces": [
            {
                "id": "trace-1",
                "agent": "Agent A",
                "status": "success",
                "timestamp": "2 mins ago",
                "duration": "1.2s",
                "steps": 5,
                "confidence": 95
            }
        ]
    }


@router.post("/")
async def create_trace(data: TraceData):
    """Create a new trace"""
    return {
        "id": "new-trace",
        "agent_id": data.agent_id,
        "status": "created"
    }


@router.get("/{trace_id}")
async def get_trace(trace_id: str):
    """Get trace by ID"""
    return {
        "id": trace_id,
        "agent": "Agent",
        "status": "success"
    }
