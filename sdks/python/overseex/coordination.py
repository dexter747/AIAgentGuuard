"""
OverseeX Coordination Client

Client for accessing multi-agent coordination intelligence features.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from .models import (
    CoordinationIssue,
    CorrectiveSuggestion,
    LearnedPattern,
    AgentHandoff,
    CoordinationMetrics,
)

if TYPE_CHECKING:
    from .client import OverseeX


class CoordinationClient:
    """
    Client for coordination intelligence features.

    Access via the main client:
        client = OverseeX(api_key="...")
        issues = client.coordination.list_issues()

    Features:
    - List and analyze coordination issues (state drift, handoff failures, etc.)
    - Get corrective suggestions with ML-powered confidence scores
    - Provide feedback to improve suggestions
    - View learned patterns
    - Track agent handoffs
    """

    def __init__(self, client: "OverseeX"):
        """Initialize coordination client."""
        self._client = client

    def _request(self, method: str, path: str, **kwargs):
        """Make API request via parent client."""
        return self._client._request(method, f"/api/v1/coordination{path}", **kwargs)

    # ==================
    # Issues
    # ==================

    def list_issues(
        self,
        issue_type: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[CoordinationIssue]:
        """
        List coordination issues.

        Args:
            issue_type: Filter by type (state_drift, handoff_failure, etc.)
            severity: Filter by severity (critical, high, medium, low)
            status: Filter by status (open, resolved, ignored)
            limit: Max results to return
            offset: Pagination offset

        Returns:
            List of CoordinationIssue objects
        """
        params = {"limit": limit, "offset": offset}
        if issue_type:
            params["issue_type"] = issue_type
        if severity:
            params["severity"] = severity
        if status:
            params["status"] = status

        data = self._request("GET", "/issues", params=params)
        items = data.get("items", data) if isinstance(data, dict) else data
        return [CoordinationIssue(**issue) for issue in items]

    def get_issue(self, issue_id: str) -> CoordinationIssue:
        """Get a specific coordination issue."""
        data = self._request("GET", f"/issues/{issue_id}")
        return CoordinationIssue(**data)

    def resolve_issue(self, issue_id: str, resolution_notes: Optional[str] = None) -> Dict[str, Any]:
        """Mark an issue as resolved."""
        return self._request("POST", f"/issues/{issue_id}/resolve", data={
            "resolution_notes": resolution_notes,
        })

    def ignore_issue(self, issue_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Mark an issue as ignored."""
        return self._request("POST", f"/issues/{issue_id}/ignore", data={
            "reason": reason,
        })

    # ==================
    # Suggestions
    # ==================

    def list_suggestions(
        self,
        status: Optional[str] = None,
        min_confidence: Optional[float] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[CorrectiveSuggestion]:
        """
        List corrective suggestions.

        Args:
            status: Filter by status (pending, approved, rejected)
            min_confidence: Minimum confidence score (0-1)
            limit: Max results to return
            offset: Pagination offset

        Returns:
            List of CorrectiveSuggestion objects
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if min_confidence is not None:
            params["min_confidence"] = min_confidence

        data = self._request("GET", "/suggestions", params=params)
        items = data.get("items", data) if isinstance(data, dict) else data
        return [CorrectiveSuggestion(**s) for s in items]

    def get_suggestion(self, suggestion_id: str) -> CorrectiveSuggestion:
        """Get a specific suggestion."""
        data = self._request("GET", f"/suggestions/{suggestion_id}")
        return CorrectiveSuggestion(**data)

    def approve_suggestion(
        self,
        suggestion_id: str,
        feedback_notes: Optional[str] = None,
        applied_changes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Approve a suggestion.

        When approved, the suggestion pattern is learned for future use.

        Args:
            suggestion_id: ID of the suggestion to approve
            feedback_notes: Optional notes about the approval
            applied_changes: Optional details of how the fix was applied

        Returns:
            Response including pattern learning status
        """
        return self._request("POST", f"/suggestions/{suggestion_id}/feedback", data={
            "approved": True,
            "feedback_notes": feedback_notes,
            "applied_changes": applied_changes,
        })

    def reject_suggestion(
        self,
        suggestion_id: str,
        feedback_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reject a suggestion.

        Args:
            suggestion_id: ID of the suggestion to reject
            feedback_notes: Reason for rejection (helps improve future suggestions)

        Returns:
            Response with updated status
        """
        return self._request("POST", f"/suggestions/{suggestion_id}/feedback", data={
            "approved": False,
            "feedback_notes": feedback_notes,
        })

    # ==================
    # Patterns
    # ==================

    def list_patterns(
        self,
        issue_type: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0,
    ) -> List[LearnedPattern]:
        """
        List learned patterns.

        Patterns are learned from approved suggestions and used
        to improve future recommendation confidence.

        Args:
            issue_type: Filter by issue type
            is_active: Only show active patterns (default True)
            limit: Max results
            offset: Pagination offset

        Returns:
            List of LearnedPattern objects
        """
        params = {"limit": limit, "offset": offset, "is_active": is_active}
        if issue_type:
            params["issue_type"] = issue_type

        data = self._request("GET", "/patterns", params=params)
        items = data.get("items", data) if isinstance(data, dict) else data
        return [LearnedPattern(**p) for p in items]

    def get_pattern(self, pattern_id: str) -> LearnedPattern:
        """Get a specific pattern."""
        data = self._request("GET", f"/patterns/{pattern_id}")
        return LearnedPattern(**data)

    def deactivate_pattern(self, pattern_id: str) -> Dict[str, Any]:
        """Deactivate a pattern (stop using it for recommendations)."""
        return self._request("POST", f"/patterns/{pattern_id}/deactivate")

    # ==================
    # Handoffs
    # ==================

    def list_handoffs(
        self,
        trace_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[AgentHandoff]:
        """
        List agent handoffs.

        Args:
            trace_id: Filter by trace ID
            agent_id: Filter by agent ID (as source or target)
            limit: Max results
            offset: Pagination offset

        Returns:
            List of AgentHandoff objects
        """
        params = {"limit": limit, "offset": offset}
        if trace_id:
            params["trace_id"] = trace_id
        if agent_id:
            params["agent_id"] = agent_id

        data = self._request("GET", "/handoffs", params=params)
        items = data.get("items", data) if isinstance(data, dict) else data
        return [AgentHandoff(**h) for h in items]

    def get_handoff_stats(
        self,
        agent_id: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get handoff statistics.

        Args:
            agent_id: Filter by agent ID
            days: Number of days to analyze

        Returns:
            Statistics including success rate, average duration, etc.
        """
        params = {"days": days}
        if agent_id:
            params["agent_id"] = agent_id

        return self._request("GET", "/handoffs/stats", params=params)

    # ==================
    # Metrics
    # ==================

    def get_metrics(
        self,
        agent_id: Optional[str] = None,
        days: int = 7,
    ) -> CoordinationMetrics:
        """
        Get coordination metrics.

        Args:
            agent_id: Filter by agent ID
            days: Number of days to analyze

        Returns:
            CoordinationMetrics object with aggregated data
        """
        params = {"days": days}
        if agent_id:
            params["agent_id"] = agent_id

        data = self._request("GET", "/metrics", params=params)
        return CoordinationMetrics(**data)

    # ==================
    # Analysis
    # ==================

    def analyze_traces(
        self,
        trace_ids: List[str],
        auto_create_issues: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze traces for coordination issues.

        Args:
            trace_ids: List of trace IDs to analyze
            auto_create_issues: Automatically create issues for detected problems

        Returns:
            Analysis results including detected issues
        """
        return self._request("POST", "/analyze", data={
            "trace_ids": trace_ids,
            "auto_create_issues": auto_create_issues,
        })

    def get_graph_data(
        self,
        trace_id: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Get coordination graph data for visualization.

        Returns nodes (agents) and edges (handoffs) suitable
        for rendering in a graph visualization library.

        Args:
            trace_id: Get graph for a specific trace
            days: Number of days of data to include

        Returns:
            Graph data with nodes and edges
        """
        params = {"days": days}
        if trace_id:
            params["trace_id"] = trace_id

        return self._request("GET", "/graph", params=params)
