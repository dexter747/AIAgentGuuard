"""
Multi-Agent Coordination Analysis

Detects coordination failures in multi-agent systems:
- State drift: Agents operating on misaligned state
- Broken assumptions: Preconditions violated
- Coordination breakdowns: Failed handoffs between agents

This is AgentGuard's answer to Competitor's core feature.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json


class CoordinationIssueType(str, Enum):
    """Types of coordination issues."""
    STATE_DRIFT = "state_drift"
    BROKEN_ASSUMPTION = "broken_assumption"
    HANDOFF_FAILURE = "handoff_failure"
    DUPLICATE_WORK = "duplicate_work"
    MISSING_DELEGATION = "missing_delegation"
    CIRCULAR_DEPENDENCY = "circular_dependency"


@dataclass
class CoordinationIssue:
    """
    Represents a detected coordination issue.
    """
    issue_type: CoordinationIssueType
    severity: str  # "critical", "high", "medium", "low"
    description: str
    affected_agents: List[str]
    evidence: Dict[str, Any]
    suggested_fix: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "affected_agents": self.affected_agents,
            "evidence": self.evidence,
            "suggested_fix": self.suggested_fix,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class CoordinationAnalyzer:
    """
    Analyzes multi-agent traces for coordination issues.
    
    Usage:
        >>> analyzer = CoordinationAnalyzer()
        >>> traces = get_recent_traces(agent_ids=["agent1", "agent2"])
        >>> issues = analyzer.analyze_coordination(traces)
        >>> for issue in issues:
        ...     print(f"{issue.severity}: {issue.description}")
    """
    
    def __init__(self):
        """Initialize coordination analyzer."""
        self.state_history: Dict[str, List[Dict]] = {}
        self.assumptions_cache: Dict[str, List[str]] = {}
    
    def analyze_coordination(
        self,
        traces: List[Dict[str, Any]]
    ) -> List[CoordinationIssue]:
        """
        Analyze multiple traces for coordination issues.
        
        Args:
            traces: List of trace dictionaries from multiple agents
            
        Returns:
            List of detected coordination issues
        """
        issues: List[CoordinationIssue] = []
        
        # Group traces by timestamp/workflow
        workflows = self._group_traces_by_workflow(traces)
        
        for workflow_id, workflow_traces in workflows.items():
            # Detect state drift
            issues.extend(self._detect_state_drift(workflow_traces))
            
            # Detect broken assumptions
            issues.extend(self._detect_broken_assumptions(workflow_traces))
            
            # Detect handoff failures
            issues.extend(self._detect_handoff_failures(workflow_traces))
            
            # Detect duplicate work
            issues.extend(self._detect_duplicate_work(workflow_traces))
            
            # Detect circular dependencies
            issues.extend(self._detect_circular_dependencies(workflow_traces))
        
        return issues
    
    def _group_traces_by_workflow(
        self,
        traces: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict]]:
        """Group traces by workflow/session ID."""
        workflows: Dict[str, List[Dict]] = {}
        
        for trace in traces:
            # Try to extract workflow ID from metadata
            workflow_id = trace.get("metadata", {}).get("workflow_id")
            
            # If no workflow_id, group by time window (5 minutes)
            if not workflow_id:
                timestamp = trace.get("created_at", datetime.now())
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                # Round to 5-minute window
                window = timestamp.replace(second=0, microsecond=0)
                window = window.replace(minute=(window.minute // 5) * 5)
                workflow_id = f"window_{window.isoformat()}"
            
            if workflow_id not in workflows:
                workflows[workflow_id] = []
            workflows[workflow_id].append(trace)
        
        return workflows
    
    def _detect_state_drift(
        self,
        traces: List[Dict[str, Any]]
    ) -> List[CoordinationIssue]:
        """
        Detect when agents have misaligned state.
        
        Example: Agent A thinks order status is "pending",
                 Agent B thinks it's "confirmed"
        """
        issues = []
        
        # Extract state snapshots from each trace
        state_by_agent: Dict[str, List[Dict]] = {}
        
        for trace in traces:
            agent_id = trace.get("agent_id")
            if not agent_id:
                continue
            
            # Look for state in trace_data
            trace_data = trace.get("trace_data", {})
            state_snapshot = trace_data.get("state", {}) or trace_data.get("metadata", {}).get("state", {})
            
            if state_snapshot:
                if agent_id not in state_by_agent:
                    state_by_agent[agent_id] = []
                state_by_agent[agent_id].append({
                    "timestamp": trace.get("created_at"),
                    "state": state_snapshot,
                    "trace_id": trace.get("id")
                })
        
        # Compare states across agents
        if len(state_by_agent) > 1:
            agent_ids = list(state_by_agent.keys())
            for i in range(len(agent_ids)):
                for j in range(i + 1, len(agent_ids)):
                    agent1 = agent_ids[i]
                    agent2 = agent_ids[j]
                    
                    # Compare latest states
                    state1 = state_by_agent[agent1][-1]["state"]
                    state2 = state_by_agent[agent2][-1]["state"]
                    
                    # Find mismatched keys
                    mismatches = self._find_state_mismatches(state1, state2)
                    
                    if mismatches:
                        issues.append(CoordinationIssue(
                            issue_type=CoordinationIssueType.STATE_DRIFT,
                            severity="high",
                            description=f"State drift detected between {agent1} and {agent2}",
                            affected_agents=[agent1, agent2],
                            evidence={
                                "mismatches": mismatches,
                                "agent1_state": state1,
                                "agent2_state": state2
                            },
                            suggested_fix="Implement state synchronization or event sourcing",
                            timestamp=datetime.now()
                        ))
        
        return issues
    
    def _find_state_mismatches(
        self,
        state1: Dict,
        state2: Dict
    ) -> List[Dict[str, Any]]:
        """Find mismatched keys between two state dictionaries."""
        mismatches = []
        
        # Check common keys
        common_keys = set(state1.keys()) & set(state2.keys())
        for key in common_keys:
            if state1[key] != state2[key]:
                mismatches.append({
                    "key": key,
                    "agent1_value": state1[key],
                    "agent2_value": state2[key]
                })
        
        # Check missing keys
        only_in_1 = set(state1.keys()) - set(state2.keys())
        only_in_2 = set(state2.keys()) - set(state1.keys())
        
        for key in only_in_1:
            mismatches.append({
                "key": key,
                "agent1_value": state1[key],
                "agent2_value": "<missing>"
            })
        
        for key in only_in_2:
            mismatches.append({
                "key": key,
                "agent1_value": "<missing>",
                "agent2_value": state2[key]
            })
        
        return mismatches
    
    def _detect_broken_assumptions(
        self,
        traces: List[Dict[str, Any]]
    ) -> List[CoordinationIssue]:
        """
        Detect when agent preconditions are violated.
        
        Example: Agent assumes file exists, but it was deleted
        """
        issues = []
        
        for trace in traces:
            trace_data = trace.get("trace_data", {})
            metadata = trace_data.get("metadata", {})
            
            # Look for assumption violations in errors
            error_msg = trace.get("error_message", "")
            if error_msg and any(keyword in error_msg.lower() for keyword in [
                "not found", "does not exist", "missing", "undefined",
                "null", "invalid", "precondition", "expected"
            ]):
                issues.append(CoordinationIssue(
                    issue_type=CoordinationIssueType.BROKEN_ASSUMPTION,
                    severity="high",
                    description=f"Precondition violation in {trace.get('agent_id')}",
                    affected_agents=[trace.get("agent_id", "unknown")],
                    evidence={
                        "error_message": error_msg,
                        "trace_id": trace.get("id"),
                        "input_data": trace_data.get("input", {})
                    },
                    suggested_fix="Add precondition checks or defensive programming",
                    timestamp=datetime.now()
                ))
        
        return issues
    
    def _detect_handoff_failures(
        self,
        traces: List[Dict[str, Any]]
    ) -> List[CoordinationIssue]:
        """
        Detect failed task handoffs between agents.
        
        Example: Agent A completes task, Agent B never picks it up
        """
        issues = []
        
        # Look for delegation/handoff patterns
        handoffs: List[Dict] = []
        
        for trace in traces:
            trace_data = trace.get("trace_data", {})
            metadata = trace_data.get("metadata", {})
            
            # Check for delegation metadata
            if "delegation" in metadata or "handoff" in metadata:
                handoffs.append({
                    "from_agent": trace.get("agent_id"),
                    "to_agent": metadata.get("delegation", {}).get("to_agent") or 
                                metadata.get("handoff", {}).get("to_agent"),
                    "task": metadata.get("delegation", {}).get("task") or
                            metadata.get("handoff", {}).get("task"),
                    "timestamp": trace.get("created_at"),
                    "trace_id": trace.get("id")
                })
        
        # Check if delegated tasks were executed
        for handoff in handoffs:
            target_agent = handoff["to_agent"]
            task = handoff["task"]
            
            # Look for traces from target agent after handoff
            target_traces = [
                t for t in traces
                if t.get("agent_id") == target_agent and
                t.get("created_at") > handoff["timestamp"]
            ]
            
            if not target_traces:
                issues.append(CoordinationIssue(
                    issue_type=CoordinationIssueType.HANDOFF_FAILURE,
                    severity="critical",
                    description=f"Task handoff from {handoff['from_agent']} to {target_agent} failed",
                    affected_agents=[handoff["from_agent"], target_agent],
                    evidence={
                        "handoff": handoff,
                        "target_agent_traces": len(target_traces)
                    },
                    suggested_fix="Implement acknowledgment protocol for task handoffs",
                    timestamp=datetime.now()
                ))
        
        return issues
    
    def _detect_duplicate_work(
        self,
        traces: List[Dict[str, Any]]
    ) -> List[CoordinationIssue]:
        """
        Detect when multiple agents do the same work.
        """
        issues = []
        
        # Group traces by similar inputs
        input_groups: Dict[str, List[Dict]] = {}
        
        for trace in traces:
            trace_data = trace.get("trace_data", {})
            input_data = trace_data.get("input", {})
            
            # Create simplified input hash
            input_str = json.dumps(input_data, sort_keys=True)
            
            if input_str not in input_groups:
                input_groups[input_str] = []
            input_groups[input_str].append(trace)
        
        # Check for duplicates
        for input_str, group in input_groups.items():
            if len(group) > 1:
                # Multiple agents processed same input
                agent_ids = [t.get("agent_id") for t in group]
                if len(set(agent_ids)) > 1:  # Different agents
                    issues.append(CoordinationIssue(
                        issue_type=CoordinationIssueType.DUPLICATE_WORK,
                        severity="medium",
                        description=f"Duplicate work detected across {len(set(agent_ids))} agents",
                        affected_agents=list(set(agent_ids)),
                        evidence={
                            "input": input_str[:200],
                            "num_executions": len(group),
                            "trace_ids": [t.get("id") for t in group]
                        },
                        suggested_fix="Implement task locking or coordinator pattern",
                        timestamp=datetime.now()
                    ))
        
        return issues
    
    def _detect_circular_dependencies(
        self,
        traces: List[Dict[str, Any]]
    ) -> List[CoordinationIssue]:
        """
        Detect circular dependencies between agents.
        
        Example: Agent A waits for Agent B, Agent B waits for Agent A
        """
        issues = []
        
        # Build dependency graph
        dependencies: Dict[str, List[str]] = {}
        
        for trace in traces:
            agent_id = trace.get("agent_id")
            metadata = trace.get("trace_data", {}).get("metadata", {})
            
            # Look for "waiting_for" or "depends_on" metadata
            depends_on = metadata.get("depends_on") or metadata.get("waiting_for")
            if depends_on:
                if agent_id not in dependencies:
                    dependencies[agent_id] = []
                if isinstance(depends_on, list):
                    dependencies[agent_id].extend(depends_on)
                else:
                    dependencies[agent_id].append(depends_on)
        
        # Detect cycles using DFS
        def has_cycle(node: str, visited: set, rec_stack: set) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    cycle = has_cycle(neighbor, visited, rec_stack)
                    if cycle:
                        return [node] + cycle
                elif neighbor in rec_stack:
                    return [node, neighbor]
            
            rec_stack.remove(node)
            return None
        
        visited = set()
        for node in dependencies:
            if node not in visited:
                cycle = has_cycle(node, visited, set())
                if cycle:
                    issues.append(CoordinationIssue(
                        issue_type=CoordinationIssueType.CIRCULAR_DEPENDENCY,
                        severity="critical",
                        description=f"Circular dependency detected: {' -> '.join(cycle)}",
                        affected_agents=cycle,
                        evidence={
                            "cycle": cycle,
                            "dependencies": {k: v for k, v in dependencies.items() if k in cycle}
                        },
                        suggested_fix="Refactor agent dependencies to remove cycles",
                        timestamp=datetime.now()
                    ))
        
        return issues


# Global instance
_analyzer_instance: Optional[CoordinationAnalyzer] = None


def get_analyzer() -> CoordinationAnalyzer:
    """Get or create global analyzer instance."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = CoordinationAnalyzer()
    return _analyzer_instance


def analyze_coordination(traces: List[Dict[str, Any]]) -> List[CoordinationIssue]:
    """Convenience function to analyze coordination."""
    analyzer = get_analyzer()
    return analyzer.analyze_coordination(traces)
