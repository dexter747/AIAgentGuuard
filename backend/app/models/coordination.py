"""
Coordination Intelligence Models

Database models for storing multi-agent coordination analysis results,
corrective suggestions, and learned patterns for Phase 2 features.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base


class CoordinationIssueType(str, enum.Enum):
    """Types of coordination issues that can be detected."""
    STATE_DRIFT = "state_drift"
    BROKEN_ASSUMPTION = "broken_assumption"
    HANDOFF_FAILURE = "handoff_failure"
    DUPLICATE_WORK = "duplicate_work"
    MISSING_DELEGATION = "missing_delegation"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    TIMEOUT = "timeout"
    SCHEMA_MISMATCH = "schema_mismatch"


class IssueSeverity(str, enum.Enum):
    """Severity levels for coordination issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FeedbackStatus(str, enum.Enum):
    """Status of user feedback on suggestions."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CoordinationIssue(Base):
    """
    Stores detected coordination issues from multi-agent traces.

    This is a core Phase 2 table that tracks:
    - State drift between agents
    - Broken assumptions/preconditions
    - Failed handoffs
    - Duplicate work detection
    - Circular dependencies
    """
    __tablename__ = "coordination_issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=True, index=True)

    # Issue classification
    issue_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="medium", index=True)

    # Issue details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    affected_agents = Column(ARRAY(String), nullable=True)

    # Evidence and context
    evidence = Column(JSONB, nullable=True)  # Detailed evidence data
    context = Column(JSONB, nullable=True)   # Additional context

    # Suggested fix
    suggested_fix = Column(Text, nullable=True)
    fix_confidence = Column(Float, nullable=True)  # 0-1 confidence score

    # User feedback
    user_feedback = Column(String(20), default="pending")
    feedback_comment = Column(Text, nullable=True)
    feedback_at = Column(DateTime, nullable=True)

    # Status tracking
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    trace = relationship("Trace")
    suggestions = relationship("CorrectiveSuggestion", back_populates="issue")


class CorrectiveSuggestion(Base):
    """
    Stores ML-powered corrective suggestions for coordination issues.

    When a coordination issue is detected, this table stores:
    - The original failed flow
    - The suggested corrected flow
    - User approval/rejection for learning
    """
    __tablename__ = "corrective_suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("coordination_issues.id"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    # Correction details
    correction_strategy = Column(String(50), nullable=False)  # reorder, add_sync, add_check, etc.
    description = Column(Text, nullable=False)

    # Flow comparison
    original_flow = Column(JSONB, nullable=False)   # What happened
    corrected_flow = Column(JSONB, nullable=False)  # What should happen
    changes = Column(JSONB, nullable=True)          # List of specific changes

    # Confidence and learning
    confidence = Column(Float, nullable=False, default=0.5)
    is_ml_generated = Column(Boolean, default=False)
    model_version = Column(String(50), nullable=True)

    # User feedback for learning
    status = Column(String(20), default="pending")  # pending, approved, rejected
    user_feedback = Column(Text, nullable=True)
    applied = Column(Boolean, default=False)
    applied_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issue = relationship("CoordinationIssue", back_populates="suggestions")
    organization = relationship("Organization")


class LearnedPattern(Base):
    """
    Stores patterns learned from user feedback on suggestions.

    When users approve corrections, the pattern is stored here
    to improve future suggestions for similar issues.
    """
    __tablename__ = "learned_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    # Pattern classification
    pattern_type = Column(String(50), nullable=False, index=True)  # Maps to issue_type
    pattern_name = Column(String(255), nullable=False)

    # Pattern data
    pattern_signature = Column(JSONB, nullable=False)  # How to identify this pattern
    correction_template = Column(JSONB, nullable=False)  # How to fix it

    # Learning metrics
    times_applied = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # Approval rate when suggested
    last_applied_at = Column(DateTime, nullable=True)

    # Source tracking
    source_suggestion_id = Column(UUID(as_uuid=True), ForeignKey("corrective_suggestions.id"), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")


class AgentHandoff(Base):
    """
    Tracks handoffs between agents for coordination analysis.

    This table enables:
    - Handoff success rate tracking
    - Bottleneck identification
    - Communication pattern analysis
    """
    __tablename__ = "agent_handoffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=True, index=True)

    # Handoff participants
    from_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    to_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)

    # Handoff details
    task_type = Column(String(100), nullable=True)
    task_data = Column(JSONB, nullable=True)

    # Handoff status
    status = Column(String(20), default="pending")  # pending, completed, failed, timeout
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # Failure tracking
    error_message = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True)

    # State comparison
    sender_state = Column(JSONB, nullable=True)    # State when sent
    receiver_state = Column(JSONB, nullable=True)  # State when received
    state_drift_detected = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    trace = relationship("Trace")
    from_agent = relationship("Agent", foreign_keys=[from_agent_id])
    to_agent = relationship("Agent", foreign_keys=[to_agent_id])


class CoordinationMetrics(Base):
    """
    Aggregated coordination metrics for dashboards.

    Pre-computed metrics for fast dashboard loading:
    - Daily/weekly/monthly aggregates
    - Per-agent success rates
    - Handoff performance
    """
    __tablename__ = "coordination_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True, index=True)

    # Time period
    period_type = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)

    # Issue counts
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    high_issues = Column(Integer, default=0)
    medium_issues = Column(Integer, default=0)
    low_issues = Column(Integer, default=0)

    # Issue breakdown by type
    state_drift_count = Column(Integer, default=0)
    handoff_failure_count = Column(Integer, default=0)
    broken_assumption_count = Column(Integer, default=0)
    duplicate_work_count = Column(Integer, default=0)
    circular_dependency_count = Column(Integer, default=0)

    # Resolution metrics
    resolved_issues = Column(Integer, default=0)
    avg_resolution_time_ms = Column(Integer, nullable=True)

    # Handoff metrics
    total_handoffs = Column(Integer, default=0)
    successful_handoffs = Column(Integer, default=0)
    failed_handoffs = Column(Integer, default=0)
    handoff_success_rate = Column(Float, nullable=True)
    avg_handoff_duration_ms = Column(Integer, nullable=True)

    # Suggestion metrics
    suggestions_generated = Column(Integer, default=0)
    suggestions_approved = Column(Integer, default=0)
    suggestions_rejected = Column(Integer, default=0)
    suggestion_approval_rate = Column(Float, nullable=True)

    # Timestamps
    computed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    agent = relationship("Agent")
