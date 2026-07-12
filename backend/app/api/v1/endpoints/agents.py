"""
Agent management endpoints with database integration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.agent import Agent
from app.models.user import User
from app.services.dodo_payments import check_usage_limit

router = APIRouter(prefix="/agents")


# Request/Response Models
class AgentCreate(BaseModel):
    name: str
    endpoint_url: Optional[str] = None
    health_check_interval: int = 300  # seconds


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    endpoint_url: Optional[str] = None
    health_check_interval: Optional[int] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    endpoint_url: Optional[str]
    health_check_interval: int
    status: str
    created_at: str
    
    # Stats (computed from traces)
    traces_total: int = 0
    traces_today: int = 0
    success_rate: float = 0.0
    avg_latency: float = 0.0


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all agents for the current organization"""
    
    agents = db.query(Agent).filter(Agent.org_id == current_user.org_id).all()
    
    result = []
    for agent in agents:
        # Calculate stats from traces
        from sqlalchemy import func
        from app.models.trace import Trace
        
        total_traces = db.query(func.count(Trace.id)).filter(
            Trace.agent_id == agent.id
        ).scalar() or 0
        
        success_traces = db.query(func.count(Trace.id)).filter(
            Trace.agent_id == agent.id,
            Trace.status == "success"
        ).scalar() or 0
        
        avg_duration = db.query(func.avg(Trace.total_duration_ms)).filter(
            Trace.agent_id == agent.id,
            Trace.total_duration_ms.isnot(None)
        ).scalar() or 0
        
        success_rate = (success_traces / total_traces * 100) if total_traces > 0 else 0
        
        result.append(AgentResponse(
            id=str(agent.id),
            name=agent.name,
            endpoint_url=agent.endpoint_url,
            health_check_interval=agent.health_check_interval,
            status="healthy",  # TODO: Get from latest health check
            created_at=agent.created_at.isoformat() if agent.created_at else "",
            traces_total=total_traces,
            traces_today=0,  # TODO: Calculate today's traces
            success_rate=round(success_rate, 1),
            avg_latency=round(avg_duration / 1000, 2) if avg_duration else 0
        ))
    
    return result


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new agent"""
    
    # Check plan limits before creating
    can_create, current_count, limit = check_usage_limit(current_user, "agents", db)
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Agent limit reached ({current_count}/{limit}). Please upgrade your plan to create more agents."
        )
    
    agent = Agent(
        org_id=current_user.org_id,
        name=agent_data.name,
        endpoint_url=agent_data.endpoint_url,
        health_check_interval=agent_data.health_check_interval
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        endpoint_url=agent.endpoint_url,
        health_check_interval=agent.health_check_interval,
        status="healthy",
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        traces_total=0,
        traces_today=0,
        success_rate=0.0,
        avg_latency=0.0
    )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific agent"""
    
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Calculate stats
    from sqlalchemy import func
    from app.models.trace import Trace
    
    total_traces = db.query(func.count(Trace.id)).filter(
        Trace.agent_id == agent.id
    ).scalar() or 0
    
    success_traces = db.query(func.count(Trace.id)).filter(
        Trace.agent_id == agent.id,
        Trace.status == "success"
    ).scalar() or 0
    
    avg_duration = db.query(func.avg(Trace.total_duration_ms)).filter(
        Trace.agent_id == agent.id
    ).scalar() or 0
    
    success_rate = (success_traces / total_traces * 100) if total_traces > 0 else 0
    
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        endpoint_url=agent.endpoint_url,
        health_check_interval=agent.health_check_interval,
        status="healthy",
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        traces_total=total_traces,
        traces_today=0,
        success_rate=round(success_rate, 1),
        avg_latency=round(avg_duration / 1000, 2) if avg_duration else 0
    )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an agent"""
    
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    if agent_data.name is not None:
        agent.name = agent_data.name
    if agent_data.endpoint_url is not None:
        agent.endpoint_url = agent_data.endpoint_url
    if agent_data.health_check_interval is not None:
        agent.health_check_interval = agent_data.health_check_interval
    
    db.commit()
    db.refresh(agent)
    
    return AgentResponse(
        id=str(agent.id),
        name=agent.name,
        endpoint_url=agent.endpoint_url,
        health_check_interval=agent.health_check_interval,
        status="healthy",
        created_at=agent.created_at.isoformat() if agent.created_at else "",
        traces_total=0,
        traces_today=0,
        success_rate=0.0,
        avg_latency=0.0
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an agent"""
    
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    db.delete(agent)
    db.commit()
    
    return None


@router.get("/{agent_id}/stats")
async def get_agent_stats(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a specific agent"""
    
    # Verify agent belongs to user's organization
    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.org_id == current_user.org_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    from sqlalchemy import func
    from app.models.trace import Trace
    from datetime import datetime, timedelta
    
    # Total traces
    total_traces = db.query(func.count(Trace.id)).filter(
        Trace.agent_id == agent_id
    ).scalar() or 0
    
    # Success traces
    success_traces = db.query(func.count(Trace.id)).filter(
        Trace.agent_id == agent_id,
        Trace.status == "success"
    ).scalar() or 0
    
    # Failed traces
    failed_traces = db.query(func.count(Trace.id)).filter(
        Trace.agent_id == agent_id,
        Trace.status.in_(["error", "failed", "failure"])
    ).scalar() or 0
    
    # Success rate
    success_rate = (success_traces / total_traces * 100) if total_traces > 0 else 0
    
    # Average duration
    avg_duration = db.query(func.avg(Trace.total_duration_ms)).filter(
        Trace.agent_id == agent_id,
        Trace.total_duration_ms.isnot(None)
    ).scalar() or 0
    
    # Total tokens
    total_tokens = db.query(func.sum(Trace.token_count)).filter(
        Trace.agent_id == agent_id,
        Trace.token_count.isnot(None)
    ).scalar() or 0
    
    # Total cost
    total_cost = 0
    cost_traces = db.query(Trace.cost_usd).filter(
        Trace.agent_id == agent_id,
        Trace.cost_usd.isnot(None)
    ).all()
    
    for trace_cost in cost_traces:
        try:
            if trace_cost[0]:
                total_cost += float(trace_cost[0])
        except (ValueError, TypeError):
            pass
    
    # Traces today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    traces_today = db.query(func.count(Trace.id)).filter(
        Trace.agent_id == agent_id,
        Trace.created_at >= today_start
    ).scalar() or 0
    
    # Traces this week
    week_start = today_start - timedelta(days=datetime.utcnow().weekday())
    traces_this_week = db.query(func.count(Trace.id)).filter(
        Trace.agent_id == agent_id,
        Trace.created_at >= week_start
    ).scalar() or 0
    
    # Recent activity (last 24 hours, grouped by hour)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_traces = db.query(
        func.date_trunc('hour', Trace.created_at).label('hour'),
        func.count(Trace.id).label('count')
    ).filter(
        Trace.agent_id == agent_id,
        Trace.created_at >= last_24h
    ).group_by('hour').order_by('hour').all()
    
    activity_data = [
        {
            "timestamp": hour.isoformat() if hour else "",
            "count": count
        }
        for hour, count in recent_traces
    ]
    
    return {
        "agent_id": str(agent.id),
        "agent_name": agent.name,
        "stats": {
            "total_traces": total_traces,
            "success_traces": success_traces,
            "failed_traces": failed_traces,
            "success_rate": round(success_rate, 1),
            "avg_duration_ms": round(avg_duration, 2) if avg_duration else 0,
            "total_tokens": int(total_tokens),
            "total_cost_usd": round(total_cost, 4),
            "traces_today": traces_today,
            "traces_this_week": traces_this_week
        },
        "activity_24h": activity_data,
        "last_updated": datetime.utcnow().isoformat()
    }
