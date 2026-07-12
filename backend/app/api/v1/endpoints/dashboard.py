"""
Dashboard statistics endpoints with real database queries
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.trace import Trace
from app.models.agent import Agent
from app.models.user import User

router = APIRouter(prefix="/dashboard")


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get dashboard statistics for the current organization"""
    
    # Get all agents for this organization
    agent_ids = db.query(Agent.id).filter(
        Agent.org_id == current_user.org_id
    ).all()
    agent_ids = [str(agent[0]) for agent in agent_ids]
    
    # Total traces
    total_traces = db.query(func.count(Trace.id)).filter(
        Trace.agent_id.in_(agent_ids)
    ).scalar() or 0
    
    # Success rate
    success_count = db.query(func.count(Trace.id)).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.status == "success"
    ).scalar() or 0
    
    success_rate = (success_count / total_traces * 100) if total_traces > 0 else 0
    
    # Total errors
    error_count = db.query(func.count(Trace.id)).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.status.in_(["error", "failed", "failure"])
    ).scalar() or 0
    
    # Average duration
    avg_duration = db.query(func.avg(Trace.total_duration_ms)).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.total_duration_ms.isnot(None)
    ).scalar() or 0
    avg_duration_seconds = round(avg_duration / 1000, 1) if avg_duration else 0
    
    # Total cost (sum of all cost_usd values)
    # Note: cost_usd is stored as string, so we need to handle conversion carefully
    total_cost = 0
    cost_traces = db.query(Trace.cost_usd).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.cost_usd.isnot(None)
    ).all()
    
    for trace_cost in cost_traces:
        try:
            if trace_cost[0]:
                total_cost += float(trace_cost[0])
        except (ValueError, TypeError):
            pass
    total_cost = round(total_cost, 2)
    
    # Traces today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    traces_today = db.query(func.count(Trace.id)).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.created_at >= today_start
    ).scalar() or 0
    
    # Get yesterday's stats for change calculation
    yesterday_start = today_start - timedelta(days=1)
    traces_yesterday = db.query(func.count(Trace.id)).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.created_at >= yesterday_start,
        Trace.created_at < today_start
    ).scalar() or 0
    
    # Calculate change percentages
    traces_change = 0
    if traces_yesterday > 0:
        traces_change = round(((traces_today - traces_yesterday) / traces_yesterday) * 100, 1)
    
    return {
        "totalTraces": total_traces,
        "successRate": round(success_rate, 1),
        "totalErrors": error_count,
        "avgDuration": avg_duration_seconds,
        "totalCost": total_cost,
        "tracesToday": traces_today,
        "changePercent": {
            "traces": traces_change,
            "success_rate": 0,  # TODO: Calculate from yesterday
            "errors": 0  # TODO: Calculate from yesterday
        }
    }


@router.get("/recent-traces")
async def get_recent_traces(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent traces for the organization"""
    
    # Get agent IDs for this organization
    agent_ids = db.query(Agent.id).filter(
        Agent.org_id == current_user.org_id
    ).all()
    agent_ids = [str(agent[0]) for agent in agent_ids]
    
    # Get recent traces
    traces = db.query(Trace).filter(
        Trace.agent_id.in_(agent_ids)
    ).order_by(Trace.created_at.desc()).limit(limit).all()
    
    result = []
    for trace in traces:
        agent = db.query(Agent).filter(Agent.id == trace.agent_id).first()
        result.append({
            "id": str(trace.id),
            "agent_name": agent.name if agent else "Unknown",
            "status": trace.status or "unknown",
            "duration_ms": trace.total_duration_ms,
            "created_at": trace.created_at.isoformat() if trace.created_at else ""
        })
    
    return {"traces": result}


@router.get("/recent-errors")
async def get_recent_errors(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent errors for the organization"""
    
    # Get agent IDs for this organization
    agent_ids = db.query(Agent.id).filter(
        Agent.org_id == current_user.org_id
    ).all()
    agent_ids = [str(agent[0]) for agent in agent_ids]
    
    # Get recent error traces
    traces = db.query(Trace).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.status.in_(["error", "failed", "failure"])
    ).order_by(Trace.created_at.desc()).limit(limit).all()
    
    result = []
    for trace in traces:
        agent = db.query(Agent).filter(Agent.id == trace.agent_id).first()
        error_message = ""
        if trace.trace_data and isinstance(trace.trace_data, dict):
            error_message = trace.trace_data.get("error_message", "Unknown error")
        
        result.append({
            "id": str(trace.id),
            "agent_name": agent.name if agent else "Unknown",
            "error_message": error_message,
            "created_at": trace.created_at.isoformat() if trace.created_at else ""
        })
    
    return {"errors": result}
