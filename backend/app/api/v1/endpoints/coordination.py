"""
Coordination Intelligence API Endpoints

Phase 2 endpoints for multi-agent coordination analysis:
- Coordination issues detection and management
- Corrective suggestions with approve/reject
- Learned patterns management
- Handoff tracking and analysis
- Coordination metrics
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.trace import Trace
from app.models.agent import Agent
from app.models.coordination import (
    CoordinationIssue,
    CorrectiveSuggestion,
    LearnedPattern,
    AgentHandoff,
    CoordinationMetrics,
)
from app.services.coordination_analysis import analyze_coordination, CoordinationIssue as IssueDataclass
from app.services.corrective_traces import generate_corrections

router = APIRouter(prefix="/coordination")


# =====================
# Request/Response Models
# =====================

class CoordinationIssueResponse(BaseModel):
    id: str
    trace_id: Optional[str]
    issue_type: str
    severity: str
    title: str
    description: str
    affected_agents: Optional[List[str]]
    evidence: Optional[Dict[str, Any]]
    suggested_fix: Optional[str]
    fix_confidence: Optional[float]
    user_feedback: str
    is_resolved: bool
    detected_at: str
    created_at: str


class CoordinationIssueCreate(BaseModel):
    trace_id: Optional[str] = None
    issue_type: str
    severity: str = "medium"
    title: str
    description: str
    affected_agents: Optional[List[str]] = None
    evidence: Optional[Dict[str, Any]] = None
    suggested_fix: Optional[str] = None


class CorrectiveSuggestionResponse(BaseModel):
    id: str
    issue_id: str
    correction_strategy: str
    description: str
    original_flow: Dict[str, Any]
    corrected_flow: Dict[str, Any]
    changes: Optional[List[Dict[str, Any]]]
    confidence: float
    status: str
    is_ml_generated: bool
    created_at: str


class SuggestionFeedback(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    feedback: Optional[str] = None


class HandoffResponse(BaseModel):
    id: str
    trace_id: Optional[str]
    from_agent_id: str
    from_agent_name: Optional[str]
    to_agent_id: str
    to_agent_name: Optional[str]
    task_type: Optional[str]
    status: str
    started_at: str
    completed_at: Optional[str]
    duration_ms: Optional[int]
    error_message: Optional[str]
    state_drift_detected: bool


class LearnedPatternResponse(BaseModel):
    id: str
    org_id: str
    issue_type: str  # Mapped from pattern_type for frontend compatibility
    pattern_type: str
    pattern_name: str
    pattern_signature: str  # JSON stringified for frontend display
    correction_template: str  # JSON stringified for frontend display
    times_applied: int
    times_approved: int
    times_rejected: int
    success_rate: float
    is_active: bool
    created_at: str
    last_applied_at: Optional[str] = None


class CoordinationMetricsResponse(BaseModel):
    total_issues: int
    critical_issues: int
    high_issues: int
    resolved_issues: int
    resolution_rate: float
    total_handoffs: int
    handoff_success_rate: float
    suggestions_generated: int
    suggestion_approval_rate: float
    issues_by_type: Dict[str, int]


class AnalyzeRequest(BaseModel):
    trace_ids: Optional[List[str]] = None
    agent_ids: Optional[List[str]] = None
    time_window_hours: int = 24


# =====================
# Coordination Issues Endpoints
# =====================

@router.get("/issues", response_model=List[CoordinationIssueResponse])
async def list_coordination_issues(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    issue_type: Optional[str] = Query(None, description="Filter by issue type"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List coordination issues for the organization"""

    query = db.query(CoordinationIssue).filter(
        CoordinationIssue.org_id == current_user.org_id
    )

    if severity:
        query = query.filter(CoordinationIssue.severity == severity)
    if issue_type:
        query = query.filter(CoordinationIssue.issue_type == issue_type)
    if resolved is not None:
        query = query.filter(CoordinationIssue.is_resolved == resolved)

    issues = query.order_by(desc(CoordinationIssue.detected_at)).offset(offset).limit(limit).all()

    return [
        CoordinationIssueResponse(
            id=str(issue.id),
            trace_id=str(issue.trace_id) if issue.trace_id else None,
            issue_type=issue.issue_type,
            severity=issue.severity,
            title=issue.title,
            description=issue.description,
            affected_agents=issue.affected_agents,
            evidence=issue.evidence,
            suggested_fix=issue.suggested_fix,
            fix_confidence=issue.fix_confidence,
            user_feedback=issue.user_feedback or "pending",
            is_resolved=issue.is_resolved,
            detected_at=issue.detected_at.isoformat() if issue.detected_at else "",
            created_at=issue.created_at.isoformat() if issue.created_at else "",
        )
        for issue in issues
    ]


@router.get("/issues/{issue_id}", response_model=CoordinationIssueResponse)
async def get_coordination_issue(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific coordination issue"""

    issue = db.query(CoordinationIssue).filter(
        CoordinationIssue.id == issue_id,
        CoordinationIssue.org_id == current_user.org_id
    ).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return CoordinationIssueResponse(
        id=str(issue.id),
        trace_id=str(issue.trace_id) if issue.trace_id else None,
        issue_type=issue.issue_type,
        severity=issue.severity,
        title=issue.title,
        description=issue.description,
        affected_agents=issue.affected_agents,
        evidence=issue.evidence,
        suggested_fix=issue.suggested_fix,
        fix_confidence=issue.fix_confidence,
        user_feedback=issue.user_feedback or "pending",
        is_resolved=issue.is_resolved,
        detected_at=issue.detected_at.isoformat() if issue.detected_at else "",
        created_at=issue.created_at.isoformat() if issue.created_at else "",
    )


@router.post("/issues/{issue_id}/resolve")
async def resolve_issue(
    issue_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an issue as resolved"""

    issue = db.query(CoordinationIssue).filter(
        CoordinationIssue.id == issue_id,
        CoordinationIssue.org_id == current_user.org_id
    ).first()

    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    issue.is_resolved = True
    issue.resolved_at = datetime.utcnow()
    issue.resolved_by = current_user.id

    db.commit()

    return {"status": "resolved", "issue_id": str(issue.id)}


@router.post("/analyze")
async def analyze_traces(
    request: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze traces for coordination issues.

    This endpoint runs the coordination analyzer on the specified traces
    or all recent traces for the specified agents.
    """

    # Build query for traces
    query = db.query(Trace).join(Agent).filter(Agent.org_id == current_user.org_id)

    if request.trace_ids:
        query = query.filter(Trace.id.in_(request.trace_ids))
    elif request.agent_ids:
        query = query.filter(Trace.agent_id.in_(request.agent_ids))

    # Time window filter
    cutoff = datetime.utcnow() - timedelta(hours=request.time_window_hours)
    query = query.filter(Trace.created_at >= cutoff)

    traces = query.limit(1000).all()

    if not traces:
        return {
            "status": "no_traces",
            "issues_detected": 0,
            "issues": []
        }

    # Convert to dict format for analyzer
    trace_dicts = [
        {
            "id": str(trace.id),
            "agent_id": str(trace.agent_id),
            "trace_data": trace.trace_data or {},
            "status": trace.status,
            "created_at": trace.created_at.isoformat() if trace.created_at else None,
            "error_message": trace.trace_data.get("error") if trace.trace_data else None
        }
        for trace in traces
    ]

    # Run coordination analysis
    detected_issues = analyze_coordination(trace_dicts)

    # Store detected issues in database
    stored_issues = []
    for issue in detected_issues:
        db_issue = CoordinationIssue(
            org_id=current_user.org_id,
            issue_type=issue.issue_type.value if hasattr(issue.issue_type, 'value') else str(issue.issue_type),
            severity=issue.severity,
            title=f"{issue.issue_type} detected",
            description=issue.description,
            affected_agents=issue.affected_agents,
            evidence=issue.evidence,
            suggested_fix=issue.suggested_fix,
            detected_at=datetime.utcnow()
        )
        db.add(db_issue)
        stored_issues.append(db_issue)

    db.commit()

    # Generate corrective suggestions for each issue
    for db_issue, issue in zip(stored_issues, detected_issues):
        corrections = generate_corrections(trace_dicts)
        for correction in corrections[:3]:  # Limit to top 3 suggestions per issue
            suggestion = CorrectiveSuggestion(
                issue_id=db_issue.id,
                org_id=current_user.org_id,
                correction_strategy=correction.correction_strategy.value if hasattr(correction.correction_strategy, 'value') else str(correction.correction_strategy),
                description=correction.description,
                original_flow={"traces": trace_dicts[:5]},  # Sample of original traces
                corrected_flow=correction.corrected_trace,
                changes=correction.changes,
                confidence=correction.confidence,
                is_ml_generated=False
            )
            db.add(suggestion)

    db.commit()

    return {
        "status": "analyzed",
        "traces_analyzed": len(traces),
        "issues_detected": len(detected_issues),
        "issues": [
            {
                "id": str(issue.id),
                "issue_type": issue.issue_type,
                "severity": issue.severity,
                "title": issue.title,
                "description": issue.description
            }
            for issue in stored_issues
        ]
    }


# =====================
# Corrective Suggestions Endpoints
# =====================

@router.get("/suggestions", response_model=List[CorrectiveSuggestionResponse])
async def list_suggestions(
    status: Optional[str] = Query(None, description="Filter by status (pending, approved, rejected)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List corrective suggestions"""

    query = db.query(CorrectiveSuggestion).filter(
        CorrectiveSuggestion.org_id == current_user.org_id
    )

    if status:
        query = query.filter(CorrectiveSuggestion.status == status)

    suggestions = query.order_by(desc(CorrectiveSuggestion.created_at)).offset(offset).limit(limit).all()

    return [
        CorrectiveSuggestionResponse(
            id=str(s.id),
            issue_id=str(s.issue_id),
            correction_strategy=s.correction_strategy,
            description=s.description,
            original_flow=s.original_flow or {},
            corrected_flow=s.corrected_flow or {},
            changes=s.changes,
            confidence=s.confidence,
            status=s.status or "pending",
            is_ml_generated=s.is_ml_generated or False,
            created_at=s.created_at.isoformat() if s.created_at else "",
        )
        for s in suggestions
    ]


@router.get("/suggestions/{suggestion_id}", response_model=CorrectiveSuggestionResponse)
async def get_suggestion(
    suggestion_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific corrective suggestion"""

    suggestion = db.query(CorrectiveSuggestion).filter(
        CorrectiveSuggestion.id == suggestion_id,
        CorrectiveSuggestion.org_id == current_user.org_id
    ).first()

    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    return CorrectiveSuggestionResponse(
        id=str(suggestion.id),
        issue_id=str(suggestion.issue_id),
        correction_strategy=suggestion.correction_strategy,
        description=suggestion.description,
        original_flow=suggestion.original_flow or {},
        corrected_flow=suggestion.corrected_flow or {},
        changes=suggestion.changes,
        confidence=suggestion.confidence,
        status=suggestion.status or "pending",
        is_ml_generated=suggestion.is_ml_generated or False,
        created_at=suggestion.created_at.isoformat() if suggestion.created_at else "",
    )


@router.post("/suggestions/{suggestion_id}/feedback")
async def provide_suggestion_feedback(
    suggestion_id: str,
    feedback: SuggestionFeedback,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject a corrective suggestion.

    This feedback is used to train the pattern learning system.
    """

    suggestion = db.query(CorrectiveSuggestion).filter(
        CorrectiveSuggestion.id == suggestion_id,
        CorrectiveSuggestion.org_id == current_user.org_id
    ).first()

    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    suggestion.status = feedback.status
    suggestion.user_feedback = feedback.feedback

    if feedback.status == "approved":
        suggestion.applied = True
        suggestion.applied_at = datetime.utcnow()

        # Create learned pattern from approved suggestion
        pattern = LearnedPattern(
            org_id=current_user.org_id,
            pattern_type=suggestion.correction_strategy,
            pattern_name=f"Learned from suggestion {suggestion_id[:8]}",
            pattern_signature=suggestion.original_flow,
            correction_template=suggestion.corrected_flow,
            source_suggestion_id=suggestion.id,
            times_applied=1,
            success_rate=1.0
        )
        db.add(pattern)

    db.commit()

    return {
        "status": "feedback_recorded",
        "suggestion_id": str(suggestion.id),
        "feedback_status": feedback.status,
        "pattern_learned": feedback.status == "approved"
    }


# =====================
# Handoff Tracking Endpoints
# =====================

@router.get("/handoffs", response_model=List[HandoffResponse])
async def list_handoffs(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List agent handoffs"""

    query = db.query(AgentHandoff).filter(
        AgentHandoff.org_id == current_user.org_id
    )

    if agent_id:
        query = query.filter(
            (AgentHandoff.from_agent_id == agent_id) | (AgentHandoff.to_agent_id == agent_id)
        )
    if status:
        query = query.filter(AgentHandoff.status == status)

    handoffs = query.order_by(desc(AgentHandoff.started_at)).offset(offset).limit(limit).all()

    # Get agent names
    agent_ids = set()
    for h in handoffs:
        agent_ids.add(h.from_agent_id)
        agent_ids.add(h.to_agent_id)

    agents = db.query(Agent).filter(Agent.id.in_(agent_ids)).all()
    agent_names = {str(a.id): a.name for a in agents}

    return [
        HandoffResponse(
            id=str(h.id),
            trace_id=str(h.trace_id) if h.trace_id else None,
            from_agent_id=str(h.from_agent_id),
            from_agent_name=agent_names.get(str(h.from_agent_id)),
            to_agent_id=str(h.to_agent_id),
            to_agent_name=agent_names.get(str(h.to_agent_id)),
            task_type=h.task_type,
            status=h.status or "pending",
            started_at=h.started_at.isoformat() if h.started_at else "",
            completed_at=h.completed_at.isoformat() if h.completed_at else None,
            duration_ms=h.duration_ms,
            error_message=h.error_message,
            state_drift_detected=h.state_drift_detected or False,
        )
        for h in handoffs
    ]


@router.get("/handoffs/stats")
async def get_handoff_stats(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    time_window_hours: int = Query(24, ge=1, le=720),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get handoff statistics"""

    cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)

    query = db.query(AgentHandoff).filter(
        AgentHandoff.org_id == current_user.org_id,
        AgentHandoff.started_at >= cutoff
    )

    if agent_id:
        query = query.filter(
            (AgentHandoff.from_agent_id == agent_id) | (AgentHandoff.to_agent_id == agent_id)
        )

    total = query.count()
    successful = query.filter(AgentHandoff.status == "completed").count()
    failed = query.filter(AgentHandoff.status == "failed").count()
    with_drift = query.filter(AgentHandoff.state_drift_detected == True).count()

    avg_duration = db.query(func.avg(AgentHandoff.duration_ms)).filter(
        AgentHandoff.org_id == current_user.org_id,
        AgentHandoff.started_at >= cutoff,
        AgentHandoff.duration_ms.isnot(None)
    ).scalar() or 0

    return {
        "time_window_hours": time_window_hours,
        "total_handoffs": total,
        "successful_handoffs": successful,
        "failed_handoffs": failed,
        "success_rate": round((successful / total * 100) if total > 0 else 0, 1),
        "handoffs_with_drift": with_drift,
        "drift_rate": round((with_drift / total * 100) if total > 0 else 0, 1),
        "avg_duration_ms": round(avg_duration, 2)
    }


# =====================
# Learned Patterns Endpoints
# =====================

@router.get("/patterns", response_model=List[LearnedPatternResponse])
async def list_learned_patterns(
    pattern_type: Optional[str] = Query(None, description="Filter by pattern type"),
    active_only: bool = Query(False, description="Only return active patterns"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List learned patterns"""
    import json

    query = db.query(LearnedPattern).filter(
        LearnedPattern.org_id == current_user.org_id
    )

    if pattern_type:
        query = query.filter(LearnedPattern.pattern_type == pattern_type)
    if active_only:
        query = query.filter(LearnedPattern.is_active == True)

    patterns = query.order_by(desc(LearnedPattern.success_rate)).all()

    # Helper to stringify JSONB fields for frontend display
    def jsonb_to_string(value):
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return json.dumps(value, indent=2)

    # Calculate times_approved and times_rejected based on success_rate
    def calculate_approved_rejected(times_applied, success_rate):
        if times_applied == 0:
            return 0, 0
        times_approved = int(times_applied * success_rate)
        times_rejected = times_applied - times_approved
        return times_approved, times_rejected

    return [
        LearnedPatternResponse(
            id=str(p.id),
            org_id=str(p.org_id),
            issue_type=p.pattern_type,  # Map pattern_type to issue_type for frontend
            pattern_type=p.pattern_type,
            pattern_name=p.pattern_name,
            pattern_signature=jsonb_to_string(p.pattern_signature),
            correction_template=jsonb_to_string(p.correction_template),
            times_applied=p.times_applied,
            times_approved=calculate_approved_rejected(p.times_applied, p.success_rate)[0],
            times_rejected=calculate_approved_rejected(p.times_applied, p.success_rate)[1],
            success_rate=p.success_rate * 100 if p.success_rate <= 1 else p.success_rate,  # Ensure percentage
            is_active=p.is_active,
            created_at=p.created_at.isoformat() if p.created_at else "",
            last_applied_at=p.last_applied_at.isoformat() if p.last_applied_at else None,
        )
        for p in patterns
    ]


@router.delete("/patterns/{pattern_id}")
async def deactivate_pattern(
    pattern_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a learned pattern"""

    pattern = db.query(LearnedPattern).filter(
        LearnedPattern.id == pattern_id,
        LearnedPattern.org_id == current_user.org_id
    ).first()

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    pattern.is_active = False
    db.commit()

    return {"status": "deactivated", "pattern_id": str(pattern.id)}


# =====================
# Metrics Endpoint
# =====================

@router.get("/metrics", response_model=CoordinationMetricsResponse)
async def get_coordination_metrics(
    time_window_hours: int = Query(24, ge=1, le=720),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get coordination metrics for the organization"""

    cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)

    # Issue metrics
    issues_query = db.query(CoordinationIssue).filter(
        CoordinationIssue.org_id == current_user.org_id,
        CoordinationIssue.detected_at >= cutoff
    )

    total_issues = issues_query.count()
    critical_issues = issues_query.filter(CoordinationIssue.severity == "critical").count()
    high_issues = issues_query.filter(CoordinationIssue.severity == "high").count()
    resolved_issues = issues_query.filter(CoordinationIssue.is_resolved == True).count()

    # Issues by type
    issues_by_type = {}
    for issue_type in ["state_drift", "handoff_failure", "broken_assumption", "duplicate_work", "circular_dependency"]:
        count = issues_query.filter(CoordinationIssue.issue_type == issue_type).count()
        issues_by_type[issue_type] = count

    # Handoff metrics
    handoffs_query = db.query(AgentHandoff).filter(
        AgentHandoff.org_id == current_user.org_id,
        AgentHandoff.started_at >= cutoff
    )

    total_handoffs = handoffs_query.count()
    successful_handoffs = handoffs_query.filter(AgentHandoff.status == "completed").count()
    handoff_success_rate = (successful_handoffs / total_handoffs * 100) if total_handoffs > 0 else 0

    # Suggestion metrics
    suggestions_query = db.query(CorrectiveSuggestion).filter(
        CorrectiveSuggestion.org_id == current_user.org_id,
        CorrectiveSuggestion.created_at >= cutoff
    )

    suggestions_generated = suggestions_query.count()
    suggestions_approved = suggestions_query.filter(CorrectiveSuggestion.status == "approved").count()
    suggestion_approval_rate = (suggestions_approved / suggestions_generated * 100) if suggestions_generated > 0 else 0

    return CoordinationMetricsResponse(
        total_issues=total_issues,
        critical_issues=critical_issues,
        high_issues=high_issues,
        resolved_issues=resolved_issues,
        resolution_rate=round((resolved_issues / total_issues * 100) if total_issues > 0 else 0, 1),
        total_handoffs=total_handoffs,
        handoff_success_rate=round(handoff_success_rate, 1),
        suggestions_generated=suggestions_generated,
        suggestion_approval_rate=round(suggestion_approval_rate, 1),
        issues_by_type=issues_by_type
    )


# =====================
# Coordination Graph Data
# =====================

@router.get("/graph")
async def get_coordination_graph(
    time_window_hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get coordination graph data for visualization.

    Returns nodes (agents) and edges (handoffs) for rendering
    an interactive coordination diagram.
    """

    cutoff = datetime.utcnow() - timedelta(hours=time_window_hours)

    # Get all agents for the organization
    agents = db.query(Agent).filter(Agent.org_id == current_user.org_id).all()

    # Get handoffs in the time window
    handoffs = db.query(AgentHandoff).filter(
        AgentHandoff.org_id == current_user.org_id,
        AgentHandoff.started_at >= cutoff
    ).all()

    # Build nodes
    nodes = []
    for agent in agents:
        # Count traces for this agent
        trace_count = db.query(func.count(Trace.id)).filter(
            Trace.agent_id == agent.id,
            Trace.created_at >= cutoff
        ).scalar() or 0

        # Count issues affecting this agent
        issue_count = db.query(func.count(CoordinationIssue.id)).filter(
            CoordinationIssue.org_id == current_user.org_id,
            CoordinationIssue.affected_agents.contains([agent.name]),
            CoordinationIssue.detected_at >= cutoff
        ).scalar() or 0

        nodes.append({
            "id": str(agent.id),
            "label": agent.name,
            "type": "agent",
            "trace_count": trace_count,
            "issue_count": issue_count,
            "status": "healthy" if issue_count == 0 else ("warning" if issue_count < 3 else "error")
        })

    # Build edges from handoffs
    edge_counts = {}
    for handoff in handoffs:
        key = f"{handoff.from_agent_id}-{handoff.to_agent_id}"
        if key not in edge_counts:
            edge_counts[key] = {
                "source": str(handoff.from_agent_id),
                "target": str(handoff.to_agent_id),
                "count": 0,
                "successful": 0,
                "failed": 0
            }
        edge_counts[key]["count"] += 1
        if handoff.status == "completed":
            edge_counts[key]["successful"] += 1
        elif handoff.status == "failed":
            edge_counts[key]["failed"] += 1

    edges = []
    for key, data in edge_counts.items():
        success_rate = (data["successful"] / data["count"] * 100) if data["count"] > 0 else 0
        edges.append({
            "id": key,
            "source": data["source"],
            "target": data["target"],
            "count": data["count"],
            "successful": data["successful"],
            "failed": data["failed"],
            "success_rate": round(success_rate, 1),
            "status": "success" if success_rate >= 90 else ("warning" if success_rate >= 70 else "error")
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "time_window_hours": time_window_hours,
        "generated_at": datetime.utcnow().isoformat()
    }
