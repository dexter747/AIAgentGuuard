"""
Corrective Trace Generation

Generates corrected execution traces based on detected coordination failures.
This is Competitor's "killer feature" - we're implementing our own version.

When a multi-agent workflow fails, this service:
1. Analyzes the failed trace
2. Identifies the root cause
3. Generates a corrected trace showing what SHOULD have happened
4. Allows users to approve/reject corrections for model learning
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import copy

from .coordination_analysis import (
    CoordinationAnalyzer,
    CoordinationIssue,
    CoordinationIssueType
)


class CorrectionStrategy(str, Enum):
    """Strategies for generating corrections."""
    REORDER = "reorder"  # Reorder agent executions
    ADD_SYNC = "add_synchronization"  # Add state sync step
    ADD_CHECK = "add_precondition_check"  # Add precondition validation
    REMOVE_DUPLICATE = "remove_duplicate"  # Remove duplicate work
    BREAK_CYCLE = "break_cycle"  # Break circular dependency
    RETRY = "retry"  # Retry failed step


@dataclass
class TraceCorrection:
    """
    Represents a suggested correction to a trace.
    """
    original_trace_id: str
    correction_strategy: CorrectionStrategy
    description: str
    confidence: float  # 0-1 confidence score
    corrected_trace: Dict[str, Any]
    changes: List[Dict[str, Any]]
    issue: CoordinationIssue
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_trace_id": self.original_trace_id,
            "correction_strategy": self.correction_strategy,
            "description": self.description,
            "confidence": self.confidence,
            "corrected_trace": self.corrected_trace,
            "changes": self.changes,
            "issue": self.issue.to_dict() if self.issue else None,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


class CorrectiveTraceGenerator:
    """
    Generates corrected traces for failed multi-agent workflows.
    
    Usage:
        >>> generator = CorrectiveTraceGenerator()
        >>> failed_trace = get_failed_trace(trace_id)
        >>> corrections = generator.generate_corrections(failed_trace)
        >>> for correction in corrections:
        ...     print(f"Strategy: {correction.correction_strategy}")
        ...     print(f"Confidence: {correction.confidence}")
    """
    
    def __init__(self):
        """Initialize corrective trace generator."""
        self.analyzer = CoordinationAnalyzer()
        self.correction_history: List[TraceCorrection] = []
        self.approved_patterns: List[Dict] = []  # Patterns learned from approvals
    
    def generate_corrections(
        self,
        failed_traces: List[Dict[str, Any]],
        context_traces: Optional[List[Dict[str, Any]]] = None
    ) -> List[TraceCorrection]:
        """
        Generate correction suggestions for failed traces.
        
        Args:
            failed_traces: Traces from a failed workflow
            context_traces: Additional context (successful runs, related traces)
            
        Returns:
            List of correction suggestions
        """
        corrections = []
        
        # Analyze coordination issues
        all_traces = failed_traces + (context_traces or [])
        issues = self.analyzer.analyze_coordination(all_traces)
        
        # Generate corrections for each issue
        for issue in issues:
            correction = self._generate_correction_for_issue(issue, failed_traces)
            if correction:
                corrections.append(correction)
        
        # Sort by confidence
        corrections.sort(key=lambda c: c.confidence, reverse=True)
        
        return corrections
    
    def _generate_correction_for_issue(
        self,
        issue: CoordinationIssue,
        traces: List[Dict[str, Any]]
    ) -> Optional[TraceCorrection]:
        """Generate a correction for a specific issue."""
        
        if issue.issue_type == CoordinationIssueType.STATE_DRIFT:
            return self._correct_state_drift(issue, traces)
        
        elif issue.issue_type == CoordinationIssueType.BROKEN_ASSUMPTION:
            return self._correct_broken_assumption(issue, traces)
        
        elif issue.issue_type == CoordinationIssueType.HANDOFF_FAILURE:
            return self._correct_handoff_failure(issue, traces)
        
        elif issue.issue_type == CoordinationIssueType.DUPLICATE_WORK:
            return self._correct_duplicate_work(issue, traces)
        
        elif issue.issue_type == CoordinationIssueType.CIRCULAR_DEPENDENCY:
            return self._correct_circular_dependency(issue, traces)
        
        return None
    
    def _correct_state_drift(
        self,
        issue: CoordinationIssue,
        traces: List[Dict[str, Any]]
    ) -> TraceCorrection:
        """
        Generate correction for state drift.
        
        Solution: Add state synchronization step between agents.
        """
        affected_agents = issue.affected_agents
        mismatches = issue.evidence.get("mismatches", [])
        
        # Create corrected trace with sync step
        corrected_trace = {
            "type": "corrected_workflow",
            "original_agents": affected_agents,
            "steps": []
        }
        
        # Add state sync step
        sync_step = {
            "type": "state_synchronization",
            "action": "sync_state",
            "agents": affected_agents,
            "synced_keys": [m["key"] for m in mismatches],
            "description": f"Synchronize state for keys: {', '.join(m['key'] for m in mismatches)}"
        }
        
        corrected_trace["steps"].append(sync_step)
        
        # Add original steps with corrected state
        for trace in traces:
            if trace.get("agent_id") in affected_agents:
                step = {
                    "type": "agent_execution",
                    "agent_id": trace.get("agent_id"),
                    "input": trace.get("trace_data", {}).get("input"),
                    "expected_state": issue.evidence.get("agent1_state")  # Use unified state
                }
                corrected_trace["steps"].append(step)
        
        changes = [{
            "type": "add_step",
            "step": sync_step,
            "reason": "Added state synchronization to prevent drift"
        }]
        
        return TraceCorrection(
            original_trace_id=traces[0].get("id", "unknown"),
            correction_strategy=CorrectionStrategy.ADD_SYNC,
            description=f"Add state synchronization between {' and '.join(affected_agents)}",
            confidence=0.85,
            corrected_trace=corrected_trace,
            changes=changes,
            issue=issue
        )
    
    def _correct_broken_assumption(
        self,
        issue: CoordinationIssue,
        traces: List[Dict[str, Any]]
    ) -> TraceCorrection:
        """
        Generate correction for broken assumption.
        
        Solution: Add precondition check before execution.
        """
        error_msg = issue.evidence.get("error_message", "")
        agent_id = issue.affected_agents[0] if issue.affected_agents else "unknown"
        
        # Extract precondition from error
        precondition = self._extract_precondition(error_msg)
        
        corrected_trace = {
            "type": "corrected_workflow",
            "steps": [
                {
                    "type": "precondition_check",
                    "check": precondition,
                    "agent_id": agent_id,
                    "on_fail": "abort_or_create_resource"
                },
                {
                    "type": "agent_execution",
                    "agent_id": agent_id,
                    "condition": f"precondition_check.passed"
                }
            ]
        }
        
        changes = [{
            "type": "add_step",
            "step": corrected_trace["steps"][0],
            "reason": f"Added precondition check: {precondition}"
        }]
        
        return TraceCorrection(
            original_trace_id=issue.evidence.get("trace_id", "unknown"),
            correction_strategy=CorrectionStrategy.ADD_CHECK,
            description=f"Add precondition check before {agent_id} execution",
            confidence=0.80,
            corrected_trace=corrected_trace,
            changes=changes,
            issue=issue
        )
    
    def _extract_precondition(self, error_message: str) -> str:
        """Extract precondition from error message."""
        error_lower = error_message.lower()
        
        if "not found" in error_lower or "does not exist" in error_lower:
            return "check_resource_exists"
        elif "permission" in error_lower or "access" in error_lower:
            return "check_permissions"
        elif "null" in error_lower or "undefined" in error_lower:
            return "check_not_null"
        elif "timeout" in error_lower:
            return "check_service_available"
        else:
            return "validate_preconditions"
    
    def _correct_handoff_failure(
        self,
        issue: CoordinationIssue,
        traces: List[Dict[str, Any]]
    ) -> TraceCorrection:
        """
        Generate correction for handoff failure.
        
        Solution: Add acknowledgment protocol.
        """
        handoff = issue.evidence.get("handoff", {})
        from_agent = handoff.get("from_agent", "unknown")
        to_agent = handoff.get("to_agent", "unknown")
        
        corrected_trace = {
            "type": "corrected_workflow",
            "steps": [
                {
                    "type": "agent_execution",
                    "agent_id": from_agent,
                    "produces": "task_for_handoff"
                },
                {
                    "type": "handoff",
                    "from": from_agent,
                    "to": to_agent,
                    "protocol": "acknowledgment",
                    "timeout_seconds": 30,
                    "on_timeout": "retry_or_escalate"
                },
                {
                    "type": "acknowledgment",
                    "agent_id": to_agent,
                    "confirms": "task_received"
                },
                {
                    "type": "agent_execution",
                    "agent_id": to_agent,
                    "depends_on": "acknowledgment"
                }
            ]
        }
        
        changes = [{
            "type": "add_protocol",
            "protocol": "acknowledgment",
            "reason": "Added acknowledgment protocol for reliable handoffs"
        }]
        
        return TraceCorrection(
            original_trace_id=handoff.get("trace_id", "unknown"),
            correction_strategy=CorrectionStrategy.ADD_SYNC,
            description=f"Add acknowledgment protocol for {from_agent} -> {to_agent} handoff",
            confidence=0.90,
            corrected_trace=corrected_trace,
            changes=changes,
            issue=issue
        )
    
    def _correct_duplicate_work(
        self,
        issue: CoordinationIssue,
        traces: List[Dict[str, Any]]
    ) -> TraceCorrection:
        """
        Generate correction for duplicate work.
        
        Solution: Add coordinator/locking pattern.
        """
        affected_agents = issue.affected_agents
        
        corrected_trace = {
            "type": "corrected_workflow",
            "steps": [
                {
                    "type": "coordinator",
                    "action": "acquire_task_lock",
                    "task_id": "unique_task_id",
                    "ttl_seconds": 60
                },
                {
                    "type": "agent_selection",
                    "strategy": "first_available",
                    "candidates": affected_agents,
                    "select_one": True
                },
                {
                    "type": "agent_execution",
                    "agent_id": "${selected_agent}",
                    "holds_lock": True
                },
                {
                    "type": "coordinator",
                    "action": "release_task_lock"
                }
            ]
        }
        
        changes = [{
            "type": "add_coordination",
            "pattern": "task_locking",
            "reason": "Added task locking to prevent duplicate work"
        }]
        
        return TraceCorrection(
            original_trace_id=issue.evidence.get("trace_ids", ["unknown"])[0],
            correction_strategy=CorrectionStrategy.REMOVE_DUPLICATE,
            description=f"Add task locking to prevent {len(affected_agents)} agents from duplicating work",
            confidence=0.88,
            corrected_trace=corrected_trace,
            changes=changes,
            issue=issue
        )
    
    def _correct_circular_dependency(
        self,
        issue: CoordinationIssue,
        traces: List[Dict[str, Any]]
    ) -> TraceCorrection:
        """
        Generate correction for circular dependency.
        
        Solution: Break cycle by introducing async pattern.
        """
        cycle = issue.evidence.get("cycle", [])
        
        corrected_trace = {
            "type": "corrected_workflow",
            "steps": [
                {
                    "type": "async_initialization",
                    "agents": cycle,
                    "pattern": "event_driven"
                }
            ]
        }
        
        # Break cycle by making one agent async
        break_point = cycle[0] if cycle else "unknown"
        
        for i, agent in enumerate(cycle):
            if i == len(cycle) - 1:
                # Last agent in cycle - make async
                corrected_trace["steps"].append({
                    "type": "async_execution",
                    "agent_id": agent,
                    "publishes_event": f"{agent}_completed",
                    "does_not_wait_for": cycle[0]  # Break the cycle
                })
            else:
                corrected_trace["steps"].append({
                    "type": "agent_execution",
                    "agent_id": agent,
                    "waits_for_event": f"{cycle[i-1]}_completed" if i > 0 else None
                })
        
        changes = [{
            "type": "break_cycle",
            "at_agent": break_point,
            "pattern": "async_event_driven",
            "reason": f"Converted {break_point} to async to break circular dependency"
        }]
        
        return TraceCorrection(
            original_trace_id="workflow",
            correction_strategy=CorrectionStrategy.BREAK_CYCLE,
            description=f"Break circular dependency by making {break_point} async",
            confidence=0.75,
            corrected_trace=corrected_trace,
            changes=changes,
            issue=issue
        )
    
    def apply_correction(
        self,
        correction: TraceCorrection,
        approve: bool = True
    ) -> Dict[str, Any]:
        """
        Apply a correction (approve/reject).
        
        Args:
            correction: The correction to apply
            approve: True to approve, False to reject
            
        Returns:
            Updated correction status
        """
        correction.status = "approved" if approve else "rejected"
        
        if approve:
            # Store approved pattern for learning
            self.approved_patterns.append({
                "issue_type": correction.issue.issue_type,
                "strategy": correction.correction_strategy,
                "pattern": correction.corrected_trace,
                "approved_at": datetime.now().isoformat()
            })
        
        self.correction_history.append(correction)
        
        return {
            "correction_id": correction.original_trace_id,
            "status": correction.status,
            "learned": approve
        }
    
    def get_similar_corrections(
        self,
        issue: CoordinationIssue
    ) -> List[TraceCorrection]:
        """
        Find similar approved corrections for learning.
        
        Args:
            issue: The issue to find similar corrections for
            
        Returns:
            List of similar approved corrections
        """
        similar = []
        
        for correction in self.correction_history:
            if (correction.status == "approved" and
                correction.issue.issue_type == issue.issue_type):
                similar.append(correction)
        
        return similar


# Global instance
_generator_instance: Optional[CorrectiveTraceGenerator] = None


def get_generator() -> CorrectiveTraceGenerator:
    """Get or create global generator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = CorrectiveTraceGenerator()
    return _generator_instance


def generate_corrections(
    failed_traces: List[Dict[str, Any]],
    context_traces: Optional[List[Dict[str, Any]]] = None
) -> List[TraceCorrection]:
    """Convenience function to generate corrections."""
    generator = get_generator()
    return generator.generate_corrections(failed_traces, context_traces)
