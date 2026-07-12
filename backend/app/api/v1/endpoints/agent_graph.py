"""
Multi-Agent Graph Visualization Endpoints
Extracts agent-to-agent coordination from traces and builds execution graphs
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.agent import Agent
from app.models.trace import Trace

router = APIRouter(prefix="/agent-graph")


# Response Models
class GraphNode(BaseModel):
    id: str
    label: str
    agent_id: str
    agent_name: str
    model: Optional[str] = None
    call_count: int = 0
    avg_duration_ms: float = 0
    error_count: int = 0
    status: str = "healthy"  # healthy, degraded, unhealthy


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    call_count: int = 0
    avg_duration_ms: float = 0
    animated: bool = False
    label: Optional[str] = None
    status: str = "active"  # active, unused, error


class GraphStats(BaseModel):
    total_agents: int
    active_paths: int
    total_duration_ms: float
    parallelization_score: float  # 0-100%
    efficiency_score: float  # 0-100%


class AgentGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    stats: GraphStats
    generated_at: str


@router.get("/", response_model=AgentGraphResponse)
async def get_agent_graph(
    agent_id: Optional[str] = None,
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate multi-agent execution graph from traces.
    
    Parameters:
    - agent_id: Optional specific agent to analyze (otherwise all agents)
    - hours: Time window to analyze (default: last 24 hours)
    
    Returns interactive graph data with nodes and edges
    """
    
    # Get user's agents
    query = db.query(Agent).filter(Agent.org_id == current_user.org_id)
    if agent_id:
        query = query.filter(Agent.id == agent_id)
    agents = query.all()
    
    if not agents:
        return AgentGraphResponse(
            nodes=[],
            edges=[],
            stats=GraphStats(
                total_agents=0,
                active_paths=0,
                total_duration_ms=0,
                parallelization_score=0,
                efficiency_score=0
            ),
            generated_at=datetime.utcnow().isoformat()
        )
    
    # Get traces from the time window
    since = datetime.utcnow() - timedelta(hours=hours)
    agent_ids = [a.id for a in agents]
    
    traces = db.query(Trace).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.created_at >= since
    ).all()
    
    if not traces:
        # Return agents as nodes with no edges
        nodes = []
        for agent in agents:
            nodes.append(GraphNode(
                id=str(agent.id),
                label=agent.name,
                agent_id=str(agent.id),
                agent_name=agent.name,
                model=_extract_model_from_agent(agent),
                call_count=0,
                avg_duration_ms=0,
                error_count=0,
                status="healthy"
            ))
        
        return AgentGraphResponse(
            nodes=nodes,
            edges=[],
            stats=GraphStats(
                total_agents=len(nodes),
                active_paths=0,
                total_duration_ms=0,
                parallelization_score=0,
                efficiency_score=0
            ),
            generated_at=datetime.utcnow().isoformat()
        )
    
    # Build agent map
    agent_map = {str(a.id): a for a in agents}
    
    # Analyze traces to extract coordination patterns
    node_stats = defaultdict(lambda: {
        "call_count": 0,
        "total_duration": 0,
        "error_count": 0,
        "durations": []
    })
    
    edge_stats = defaultdict(lambda: {
        "call_count": 0,
        "total_duration": 0,
        "durations": []
    })
    
    for trace in traces:
        agent_id = str(trace.agent_id)
        duration = trace.total_duration_ms or 0
        has_error = trace.status == "error"
        
        # Update node stats
        node_stats[agent_id]["call_count"] += 1
        node_stats[agent_id]["total_duration"] += duration
        node_stats[agent_id]["durations"].append(duration)
        if has_error:
            node_stats[agent_id]["error_count"] += 1
        
        # Extract agent-to-agent calls from trace_data
        if trace.trace_data and isinstance(trace.trace_data, dict):
            agent_calls = _extract_agent_calls(trace.trace_data)
            
            for call in agent_calls:
                source = agent_id
                target = call.get("target_agent_id")
                if target and target in agent_map:
                    edge_key = f"{source}->{target}"
                    edge_stats[edge_key]["call_count"] += 1
                    call_duration = call.get("duration_ms", 0)
                    edge_stats[edge_key]["total_duration"] += call_duration
                    edge_stats[edge_key]["durations"].append(call_duration)
    
    # Build nodes
    nodes = []
    for agent_id, agent in agent_map.items():
        stats = node_stats[agent_id]
        avg_duration = stats["total_duration"] / stats["call_count"] if stats["call_count"] > 0 else 0
        error_rate = stats["error_count"] / stats["call_count"] if stats["call_count"] > 0 else 0
        
        # Determine status
        status = "healthy"
        if error_rate > 0.3:
            status = "unhealthy"
        elif error_rate > 0.1:
            status = "degraded"
        
        nodes.append(GraphNode(
            id=agent_id,
            label=agent.name,
            agent_id=agent_id,
            agent_name=agent.name,
            model=_extract_model_from_agent(agent),
            call_count=stats["call_count"],
            avg_duration_ms=round(avg_duration, 2),
            error_count=stats["error_count"],
            status=status
        ))
    
    # Build edges
    edges = []
    active_paths = 0
    for edge_key, stats in edge_stats.items():
        source, target = edge_key.split("->")
        avg_duration = stats["total_duration"] / stats["call_count"] if stats["call_count"] > 0 else 0
        
        # Edge is animated if used recently and frequently
        animated = stats["call_count"] > len(traces) * 0.1
        
        status_label = "active" if stats["call_count"] > 0 else "unused"
        if animated:
            active_paths += 1
        
        # Format duration label
        if avg_duration < 1000:
            label = f"{avg_duration:.0f}ms"
        else:
            label = f"{avg_duration/1000:.1f}s"
        
        edges.append(GraphEdge(
            id=f"e-{source}-{target}",
            source=source,
            target=target,
            call_count=stats["call_count"],
            avg_duration_ms=round(avg_duration, 2),
            animated=animated,
            label=label,
            status=status_label
        ))
    
    # Calculate stats
    total_duration = sum(s["total_duration"] for s in node_stats.values())
    
    # Calculate parallelization score (simplified)
    # Higher score if multiple agents run concurrently
    parallelization = min(100, (len(edges) / max(len(nodes), 1)) * 50)
    
    # Calculate efficiency score (lower error rate = higher efficiency)
    total_calls = sum(s["call_count"] for s in node_stats.values())
    total_errors = sum(s["error_count"] for s in node_stats.values())
    error_rate = total_errors / total_calls if total_calls > 0 else 0
    efficiency = (1 - error_rate) * 100
    
    stats = GraphStats(
        total_agents=len(nodes),
        active_paths=active_paths,
        total_duration_ms=round(total_duration, 2),
        parallelization_score=round(parallelization, 2),
        efficiency_score=round(efficiency, 2)
    )
    
    return AgentGraphResponse(
        nodes=nodes,
        edges=edges,
        stats=stats,
        generated_at=datetime.utcnow().isoformat()
    )


def _extract_model_from_agent(agent: Agent) -> Optional[str]:
    """Extract model name from agent configuration"""
    # Try to get from agent name or metadata
    name_lower = agent.name.lower()
    if "gpt-4" in name_lower:
        return "GPT-4"
    elif "gpt-3.5" in name_lower:
        return "GPT-3.5"
    elif "claude" in name_lower:
        return "Claude"
    return None


def _extract_agent_calls(trace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract agent-to-agent calls from trace data.
    
    Looks for patterns like:
    - "agent_calls": [{"agent": "...", "duration": ...}]
    - "steps": [{"type": "agent_call", "agent_id": "...", ...}]
    - Nested agent traces
    """
    agent_calls = []
    
    # Check for explicit agent_calls field
    if "agent_calls" in trace_data:
        for call in trace_data["agent_calls"]:
            agent_calls.append({
                "target_agent_id": call.get("agent_id") or call.get("agent"),
                "duration_ms": call.get("duration_ms") or call.get("duration", 0)
            })
    
    # Check for steps with agent calls
    if "steps" in trace_data:
        for step in trace_data["steps"]:
            if step.get("type") == "agent_call" or step.get("step_type") == "agent":
                agent_calls.append({
                    "target_agent_id": step.get("agent_id"),
                    "duration_ms": step.get("duration_ms", 0)
                })
    
    # Check for nested traces (multi-agent coordination)
    if "sub_traces" in trace_data:
        for sub_trace in trace_data["sub_traces"]:
            agent_calls.append({
                "target_agent_id": sub_trace.get("agent_id"),
                "duration_ms": sub_trace.get("duration_ms", 0)
            })
    
    return agent_calls


@router.get("/coordination-issues")
async def detect_coordination_issues(
    agent_id: Optional[str] = None,
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detect coordination issues in multi-agent systems:
    - State drift
    - Broken assumptions
    - Coordination breakdowns
    - Bottlenecks
    """
    
    issues = []
    
    # Get user's agents
    query = db.query(Agent).filter(Agent.org_id == current_user.org_id)
    if agent_id:
        query = query.filter(Agent.id == agent_id)
    agents = query.all()
    
    if not agents:
        return {"issues": []}
    
    # Get traces
    since = datetime.utcnow() - timedelta(hours=hours)
    agent_ids = [a.id for a in agents]
    
    traces = db.query(Trace).filter(
        Trace.agent_id.in_(agent_ids),
        Trace.created_at >= since
    ).all()
    
    # Detect bottlenecks (agents with high avg duration)
    agent_durations = defaultdict(list)
    for trace in traces:
        if trace.total_duration_ms:
            agent_durations[str(trace.agent_id)].append(trace.total_duration_ms)
    
    for agent_id, durations in agent_durations.items():
        avg_duration = sum(durations) / len(durations)
        if avg_duration > 5000:  # > 5 seconds
            agent = next((a for a in agents if str(a.id) == agent_id), None)
            if agent:
                issues.append({
                    "type": "bottleneck",
                    "severity": "warning",
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "description": f"{agent.name} has high average duration ({avg_duration/1000:.1f}s)",
                    "avg_duration_ms": round(avg_duration, 2),
                    "suggestion": "Consider optimizing prompt, caching, or parallel execution"
                })
    
    # Detect coordination breakdowns (high error rates in multi-agent flows)
    error_traces = [t for t in traces if t.status == "error"]
    if error_traces:
        error_rate = len(error_traces) / len(traces)
        if error_rate > 0.2:
            issues.append({
                "type": "coordination_breakdown",
                "severity": "critical" if error_rate > 0.4 else "warning",
                "description": f"High error rate ({error_rate*100:.1f}%) detected in agent coordination",
                "error_count": len(error_traces),
                "total_traces": len(traces),
                "suggestion": "Check agent handoffs and data passing between agents"
            })
    
    return {
        "issues": issues,
        "analyzed_traces": len(traces),
        "analyzed_agents": len(agents),
        "time_window_hours": hours
    }
