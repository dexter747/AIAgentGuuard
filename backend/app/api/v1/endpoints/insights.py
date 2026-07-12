"""
Insights endpoints - AI-powered analysis
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.agent import Agent
from app.models.trace import Trace

router = APIRouter(prefix="/insights")


class InsightResponse(BaseModel):
    insight_type: str  # 'anomaly', 'performance', 'cost', 'pattern', 'root_cause', 'recommendation'
    severity: str  # 'info', 'warning', 'critical'
    title: str
    description: str
    affected_agents: List[str]
    evidence: Dict[str, Any]
    recommendation: Optional[str] = None
    created_at: str


class CoordinationIssueResponse(BaseModel):
    issue_type: str
    severity: str
    description: str
    affected_agents: List[str]
    evidence: Dict[str, Any]
    suggested_fix: Optional[str] = None


@router.get("/", response_model=List[InsightResponse])
async def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered insights from trace analysis"""
    insights = []
    
    # Get traces from last 7 days for the user's organization
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Get user's agents first
    user_agents = db.query(Agent.id).filter(
        Agent.org_id == current_user.org_id
    ).all()
    agent_ids = [a.id for a in user_agents]
    
    if not agent_ids:
        return insights
    
    traces = db.query(Trace).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.created_at >= seven_days_ago
    ).all()
    
    if not traces:
        return insights
    
    # Helper to get agent name from trace
    agent_map = {a.id: a for a in db.query(Agent).filter(Agent.id.in_(agent_ids)).all()}
    
    def get_agent_name(trace):
        return agent_map.get(trace.agent_id, {}).name if agent_map.get(trace.agent_id) else None
    
    def get_trace_error(trace):
        """Extract error from trace_data JSONB"""
        if trace.trace_data and isinstance(trace.trace_data, dict):
            return trace.trace_data.get("error")
        return None
    
    def get_trace_cost(trace):
        """Extract cost from trace_data or cost_usd field"""
        if trace.cost_usd:
            try:
                return float(trace.cost_usd)
            except:
                return None
        if trace.trace_data and isinstance(trace.trace_data, dict):
            return trace.trace_data.get("cost")
        return None
    
    # Calculate error rate
    total_traces = len(traces)
    error_traces = [t for t in traces if get_trace_error(t) is not None or t.status == "error"]
    error_rate = len(error_traces) / total_traces if total_traces > 0 else 0
    
    if error_rate > 0.2:  # More than 20% errors
        affected = list(set([get_agent_name(t) for t in error_traces if get_agent_name(t)]))
        insights.append({
            "insight_type": "anomaly",
            "severity": "critical" if error_rate > 0.4 else "warning",
            "title": f"High error rate detected",
            "description": f"Error rate is {error_rate*100:.1f}% ({len(error_traces)}/{total_traces} traces)",
            "affected_agents": affected,
            "evidence": {
                "error_rate": error_rate,
                "total_traces": total_traces,
                "error_traces": len(error_traces)
            },
            "recommendation": "Review recent errors in traces and check agent configuration",
            "created_at": datetime.utcnow().isoformat()
        })
    
    # Calculate average duration
    durations = [t.total_duration_ms for t in traces if t.total_duration_ms]
    if durations:
        avg_duration = sum(durations) / len(durations)
        if avg_duration > 5000:  # More than 5 seconds
            slow_agents = {}
            for t in traces:
                agent_name = get_agent_name(t)
                if t.total_duration_ms and t.total_duration_ms > 5000 and agent_name:
                    slow_agents[agent_name] = slow_agents.get(agent_name, 0) + 1
            
            if slow_agents:
                worst_agent = max(slow_agents.items(), key=lambda x: x[1])
                insights.append({
                    "insight_type": "performance",
                    "severity": "warning",
                    "title": f"Slow response times detected",
                    "description": f"Average execution time is {avg_duration/1000:.1f}s",
                    "affected_agents": list(slow_agents.keys()),
                    "evidence": {
                        "avg_duration_ms": avg_duration,
                        "max_duration_ms": max(durations),
                        "min_duration_ms": min(durations),
                        "sample_size": len(durations)
                    },
                    "recommendation": "Consider caching, parallel processing, or prompt optimization",
                    "created_at": datetime.utcnow().isoformat()
                })
    
    # Calculate cost trends (if cost data available)
    costs = [get_trace_cost(t) for t in traces if get_trace_cost(t)]
    if costs and len(costs) > 10:
        recent_costs = costs[-7:]  # Last 7 traces
        older_costs = costs[:-7]
        recent_avg = sum(recent_costs) / len(recent_costs)
        older_avg = sum(older_costs) / len(older_costs) if older_costs else 0
        
        if older_avg > 0 and recent_avg > older_avg * 1.5:  # 50% increase
            increase_pct = ((recent_avg - older_avg) / older_avg) * 100
            recent_agents = list(set([get_agent_name(t) for t in traces[-7:] if get_agent_name(t)]))
            insights.append({
                "insight_type": "cost",
                "severity": "warning",
                "title": "Cost increase trend detected",
                "description": f"Recent costs are {increase_pct:.1f}% above average",
                "affected_agents": recent_agents,
                "evidence": {
                    "recent_avg": recent_avg,
                    "older_avg": older_avg,
                    "increase_pct": increase_pct
                },
                "recommendation": "Review recent changes and optimize high-cost operations",
                "created_at": datetime.utcnow().isoformat()
            })
    
    # Detect usage patterns
    hour_counts = {}
    for t in traces:
        hour = t.created_at.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    if hour_counts:
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])
        if peak_hour[1] / total_traces > 0.3:  # More than 30% in one hour
            insights.append({
                "insight_type": "pattern",
                "severity": "info",
                "title": "Peak usage pattern detected",
                "description": f"{(peak_hour[1]/total_traces)*100:.1f}% of traces occur at {peak_hour[0]:02d}:00",
                "affected_agents": [],
                "evidence": {
                    "peak_hour": peak_hour[0],
                    "peak_count": peak_hour[1],
                    "total_traces": total_traces
                },
                "recommendation": "Consider scaling infrastructure during peak hours",
                "created_at": datetime.utcnow().isoformat()
            })
    
    return insights


@router.get("/coordination", response_model=List[CoordinationIssueResponse])
async def get_coordination_issues(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get coordination issues between agents"""
    # This would analyze multi-agent traces for coordination problems
    # For now, return empty as it requires more complex trace analysis
    return []
