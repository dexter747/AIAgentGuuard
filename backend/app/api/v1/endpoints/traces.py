"""
Trace management endpoints with database integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.trace import Trace
from app.models.agent import Agent
from app.models.user import User
from app.services.dodo_payments import check_usage_limit

router = APIRouter(prefix="/traces")


# Request/Response Models
class TraceCreate(BaseModel):
    agent_id: str
    trace_data: dict
    status: Optional[str] = "success"
    total_duration_ms: Optional[int] = None
    token_count: Optional[int] = None
    cost_usd: Optional[str] = None


class TraceResponse(BaseModel):
    id: str
    agent_id: str
    agent_name: Optional[str]
    trace_data: dict
    status: str
    start_time: Optional[str]
    end_time: Optional[str]
    total_duration_ms: Optional[int]
    token_count: Optional[int]
    cost_usd: Optional[str]
    created_at: str


@router.get("/", response_model=dict)
async def list_traces(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all traces for the current organization"""
    
    # Build query
    query = db.query(Trace).join(Agent).filter(
        Agent.org_id == current_user.org_id
    )
    
    # Apply filters
    if agent_id:
        query = query.filter(Trace.agent_id == agent_id)
    if status:
        query = query.filter(Trace.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    traces = query.order_by(Trace.created_at.desc()).offset(offset).limit(limit).all()
    
    # Format response
    result = []
    for trace in traces:
        agent = db.query(Agent).filter(Agent.id == trace.agent_id).first()
        result.append({
            "id": str(trace.id),
            "agent_id": str(trace.agent_id),
            "agent_name": agent.name if agent else "Unknown",
            "status": trace.status or "unknown",
            "start_time": trace.start_time.isoformat() if trace.start_time else None,
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "total_duration_ms": trace.total_duration_ms,
            "token_count": trace.token_count,
            "cost_usd": trace.cost_usd,
            "created_at": trace.created_at.isoformat() if trace.created_at else "",
            "trace_data": trace.trace_data or {}
        })
    
    return {
        "traces": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/", response_model=TraceResponse, status_code=status.HTTP_201_CREATED)
async def create_trace(
    trace_data: TraceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new trace"""
    
    # Check plan limits before creating
    can_create, current_count, limit = check_usage_limit(current_user, "traces", db)
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Monthly trace limit reached ({current_count}/{limit}). Please upgrade your plan for more traces."
        )
    
    # Verify agent belongs to user's organization
    agent = db.query(Agent).filter(
        Agent.id == trace_data.agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Extract timing information from trace_data if present
    start_time = None
    end_time = None
    if "timestamp" in trace_data.trace_data:
        try:
            start_time = datetime.fromisoformat(trace_data.trace_data["timestamp"])
        except:
            pass
    
    # Create trace
    trace = Trace(
        agent_id=trace_data.agent_id,
        trace_data=trace_data.trace_data,
        status=trace_data.status,
        start_time=start_time,
        end_time=end_time,
        total_duration_ms=trace_data.total_duration_ms,
        token_count=trace_data.token_count,
        cost_usd=trace_data.cost_usd
    )
    
    db.add(trace)
    db.commit()
    db.refresh(trace)
    
    return TraceResponse(
        id=str(trace.id),
        agent_id=str(trace.agent_id),
        agent_name=agent.name,
        trace_data=trace.trace_data,
        status=trace.status or "unknown",
        start_time=trace.start_time.isoformat() if trace.start_time else None,
        end_time=trace.end_time.isoformat() if trace.end_time else None,
        total_duration_ms=trace.total_duration_ms,
        token_count=trace.token_count,
        cost_usd=trace.cost_usd,
        created_at=trace.created_at.isoformat() if trace.created_at else ""
    )


@router.get("/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific trace"""
    
    trace = db.query(Trace).join(Agent).filter(
        Trace.id == trace_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found"
        )
    
    agent = db.query(Agent).filter(Agent.id == trace.agent_id).first()
    
    return TraceResponse(
        id=str(trace.id),
        agent_id=str(trace.agent_id),
        agent_name=agent.name if agent else "Unknown",
        trace_data=trace.trace_data,
        status=trace.status or "unknown",
        start_time=trace.start_time.isoformat() if trace.start_time else None,
        end_time=trace.end_time.isoformat() if trace.end_time else None,
        total_duration_ms=trace.total_duration_ms,
        token_count=trace.token_count,
        cost_usd=trace.cost_usd,
        created_at=trace.created_at.isoformat() if trace.created_at else ""
    )


@router.delete("/{trace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trace(
    trace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a trace"""
    
    trace = db.query(Trace).join(Agent).filter(
        Trace.id == trace_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trace not found"
        )
    
    db.delete(trace)
    db.commit()
    
    return None
