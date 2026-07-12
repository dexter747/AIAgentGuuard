"""
OverseeX Data Models

Pydantic-style data classes for API responses.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Agent:
    """Represents an AI agent."""
    id: str
    name: str
    description: Optional[str] = None
    endpoint_url: Optional[str] = None
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    health_check_interval: Optional[int] = None
    last_health_check: Optional[str] = None
    health_status: Optional[str] = None
    traces_total: Optional[int] = None
    traces_today: Optional[int] = None
    success_rate: Optional[float] = None
    avg_latency: Optional[float] = None

    def __post_init__(self):
        if isinstance(self.metadata, type(None)):
            self.metadata = {}


@dataclass
class Trace:
    """Represents an execution trace."""
    id: str
    agent_id: str
    input_data: Any = None
    output_data: Any = None
    status: str = "success"
    error_message: Optional[str] = None
    total_duration_ms: Optional[int] = None
    token_count: Optional[int] = None
    cost_usd: Optional[str] = None
    trace_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    agent_name: Optional[str] = None  # API returns this field
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.trace_data, type(None)):
            self.trace_data = {}
        if isinstance(self.metadata, type(None)):
            self.metadata = {}
        if isinstance(self.tags, type(None)):
            self.tags = []

    @property
    def llm_calls(self) -> List[Dict[str, Any]]:
        """Get LLM calls from trace data."""
        return self.trace_data.get("llm_calls", [])

    @property
    def tool_calls(self) -> List[Dict[str, Any]]:
        """Get tool calls from trace data."""
        return self.trace_data.get("tool_calls", [])

    @property
    def handoffs(self) -> List[Dict[str, Any]]:
        """Get agent handoffs from trace data."""
        return self.trace_data.get("handoffs", [])

    @property
    def agent_flow(self) -> List[str]:
        """Get the agent flow (sequence of agents)."""
        return self.trace_data.get("agent_flow", [])


@dataclass
class CoordinationIssue:
    """Represents a detected coordination issue."""
    id: str
    org_id: str
    issue_type: str  # state_drift, handoff_failure, broken_assumption, etc.
    severity: str  # critical, high, medium, low
    title: str
    description: str
    trace_id: Optional[str] = None
    affected_agents: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    suggested_fix: Optional[str] = None
    status: str = "open"  # open, resolved, ignored
    resolution_notes: Optional[str] = None
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.affected_agents, type(None)):
            self.affected_agents = []
        if isinstance(self.evidence, type(None)):
            self.evidence = {}

    @property
    def is_critical(self) -> bool:
        """Check if this is a critical issue."""
        return self.severity == "critical"

    @property
    def is_resolved(self) -> bool:
        """Check if the issue is resolved."""
        return self.status == "resolved"


@dataclass
class CorrectiveSuggestion:
    """Represents a corrective suggestion for an issue."""
    id: str
    org_id: str
    suggestion_type: str  # reorder, add_sync, add_check, etc.
    title: str
    description: str
    suggested_fix: Optional[str] = None  # JSON string of corrected trace
    confidence_score: float = 0.0
    priority: str = "medium"
    issue_id: Optional[str] = None
    trace_id: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected
    feedback_notes: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    feedback_at: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.evidence, type(None)):
            self.evidence = {}

    @property
    def is_high_confidence(self) -> bool:
        """Check if this is a high confidence suggestion."""
        return self.confidence_score >= 0.8

    @property
    def is_auto_applicable(self) -> bool:
        """Check if this suggestion can be auto-applied."""
        return self.evidence.get("auto_applicable", False)

    @property
    def similar_patterns_count(self) -> int:
        """Get the number of similar patterns found."""
        return len(self.evidence.get("similar_patterns", []))


@dataclass
class LearnedPattern:
    """Represents a learned pattern from approved suggestions."""
    id: str
    org_id: str
    issue_type: str
    strategy: str
    pattern_data: Dict[str, Any] = field(default_factory=dict)
    success_count: int = 0
    total_applications: int = 0
    success_rate: float = 0.0
    is_active: bool = True
    source_suggestion_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.pattern_data, type(None)):
            self.pattern_data = {}

    @property
    def is_effective(self) -> bool:
        """Check if this pattern is effective (>70% success rate)."""
        return self.success_rate >= 0.7 and self.total_applications >= 3


@dataclass
class AgentHandoff:
    """Represents a handoff between agents."""
    id: str
    org_id: str
    trace_id: str
    from_agent_id: str
    to_agent_id: str
    handoff_type: str = "delegation"  # delegation, escalation, routing
    status: str = "success"  # success, failed, timeout
    context_data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.context_data, type(None)):
            self.context_data = {}

    @property
    def is_successful(self) -> bool:
        """Check if the handoff was successful."""
        return self.status == "success"


@dataclass
class CoordinationMetrics:
    """Aggregated coordination metrics."""
    total_traces: int = 0
    total_issues: int = 0
    total_handoffs: int = 0
    handoff_success_rate: float = 0.0
    avg_handoff_duration_ms: float = 0.0
    issues_by_type: Dict[str, int] = field(default_factory=dict)
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    suggestions_pending: int = 0
    suggestions_approved: int = 0
    suggestions_rejected: int = 0
    approval_rate: float = 0.0
    active_patterns: int = 0
    period_days: int = 7

    def __post_init__(self):
        if isinstance(self.issues_by_type, type(None)):
            self.issues_by_type = {}
        if isinstance(self.issues_by_severity, type(None)):
            self.issues_by_severity = {}

    @property
    def critical_issues(self) -> int:
        """Get count of critical issues."""
        return self.issues_by_severity.get("critical", 0)

    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return self.critical_issues > 0
