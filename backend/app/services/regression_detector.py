"""
Regression Detection Service - Identifies behavioral changes in agents
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.trace import Trace
from app.models.agent import Agent

logger = logging.getLogger(__name__)


class RegressionDetector:
    """
    Detects regressions in agent behavior by comparing against baselines
    
    Features:
    - Baseline tracking
    - Metric deviation detection  
    - Version comparison
    - Behavioral drift alerts
    """
    
    def __init__(self):
        self.deviation_thresholds = {
            "error_rate": 0.10,  # 10% increase in errors
            "duration": 0.30,  # 30% increase in duration
            "cost": 0.25,  # 25% increase in cost
            "token_usage": 0.40  # 40% increase in tokens
        }
    
    def detect_regressions(
        self,
        agent_id: str,
        db: Session,
        lookback_days: int = 7,
        baseline_days: int = 14
    ) -> Dict[str, Any]:
        """
        Detect regressions by comparing recent behavior to baseline
        
        Args:
            agent_id: Agent to analyze
            db: Database session
            lookback_days: Days to analyze for current behavior
            baseline_days: Days to use for baseline (before lookback period)
            
        Returns:
            Dict with regression analysis results
        """
        # Get baseline period traces
        baseline_end = datetime.utcnow() - timedelta(days=lookback_days)
        baseline_start = baseline_end - timedelta(days=baseline_days)
        
        baseline_traces = db.query(Trace).filter(
            Trace.agent_id == agent_id,
            Trace.created_at >= baseline_start,
            Trace.created_at < baseline_end
        ).all()
        
        # Get current period traces
        current_start = datetime.utcnow() - timedelta(days=lookback_days)
        current_traces = db.query(Trace).filter(
            Trace.agent_id == agent_id,
            Trace.created_at >= current_start
        ).all()
        
        if not baseline_traces:
            return {
                "has_baseline": False,
                "message": "Insufficient baseline data"
            }
        
        if not current_traces:
            return {
                "has_baseline": True,
                "has_current_data": False,
                "message": "No recent traces to analyze"
            }
        
        # Calculate baseline metrics
        baseline_metrics = self._calculate_metrics(baseline_traces)
        current_metrics = self._calculate_metrics(current_traces)
        
        # Detect deviations
        regressions = self._detect_deviations(baseline_metrics, current_metrics)
        
        # Get agent info
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.name if agent else "Unknown",
            "has_baseline": True,
            "has_current_data": True,
            "baseline_period": {
                "start": baseline_start.isoformat(),
                "end": baseline_end.isoformat(),
                "trace_count": len(baseline_traces)
            },
            "current_period": {
                "start": current_start.isoformat(),
                "end": datetime.utcnow().isoformat(),
                "trace_count": len(current_traces)
            },
            "baseline_metrics": baseline_metrics,
            "current_metrics": current_metrics,
            "regressions": regressions,
            "has_regressions": len(regressions) > 0,
            "severity": self._calculate_severity(regressions)
        }
    
    def _calculate_metrics(self, traces: List[Trace]) -> Dict[str, Any]:
        """Calculate aggregate metrics from traces"""
        if not traces:
            return {}
        
        # Error rate
        error_count = sum(1 for t in traces if t.status in ["error", "failed", "failure"])
        error_rate = error_count / len(traces)
        
        # Duration stats
        durations = [t.total_duration_ms for t in traces if t.total_duration_ms]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Token usage
        tokens = [t.token_count for t in traces if t.token_count]
        avg_tokens = sum(tokens) / len(tokens) if tokens else 0
        
        # Cost
        costs = []
        for t in traces:
            if t.cost_usd:
                try:
                    cost = float(t.cost_usd)
                    costs.append(cost)
                except (ValueError, TypeError):
                    pass
        
        avg_cost = sum(costs) / len(costs) if costs else 0
        total_cost = sum(costs)
        
        # Tool usage patterns
        tool_usage = defaultdict(int)
        for t in traces:
            trace_data = t.trace_data or {}
            tool_calls = (
                trace_data.get("tool_calls", []) or
                trace_data.get("steps", []) or
                []
            )
            for call in tool_calls:
                tool_name = (
                    call.get("tool") or
                    call.get("name") or
                    call.get("tool_name", "unknown")
                )
                tool_usage[tool_name] += 1
        
        return {
            "trace_count": len(traces),
            "error_rate": error_rate,
            "error_count": error_count,
            "avg_duration_ms": avg_duration,
            "max_duration_ms": max_duration,
            "avg_tokens": avg_tokens,
            "avg_cost": avg_cost,
            "total_cost": total_cost,
            "tool_usage": dict(tool_usage),
            "unique_tools": len(tool_usage)
        }
    
    def _detect_deviations(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect significant deviations from baseline"""
        regressions = []
        
        # Check error rate
        if baseline.get("error_rate", 0) > 0:
            error_rate_change = (
                (current.get("error_rate", 0) - baseline["error_rate"]) /
                baseline["error_rate"]
            )
            
            if error_rate_change > self.deviation_thresholds["error_rate"]:
                regressions.append({
                    "metric": "error_rate",
                    "severity": "critical",
                    "baseline_value": baseline["error_rate"],
                    "current_value": current.get("error_rate", 0),
                    "change_percent": error_rate_change * 100,
                    "message": f"Error rate increased by {error_rate_change*100:.1f}%"
                })
        
        # Check duration
        if baseline.get("avg_duration_ms", 0) > 0:
            duration_change = (
                (current.get("avg_duration_ms", 0) - baseline["avg_duration_ms"]) /
                baseline["avg_duration_ms"]
            )
            
            if duration_change > self.deviation_thresholds["duration"]:
                regressions.append({
                    "metric": "avg_duration_ms",
                    "severity": "warning",
                    "baseline_value": baseline["avg_duration_ms"],
                    "current_value": current.get("avg_duration_ms", 0),
                    "change_percent": duration_change * 100,
                    "message": f"Average duration increased by {duration_change*100:.1f}%"
                })
        
        # Check cost
        if baseline.get("avg_cost", 0) > 0:
            cost_change = (
                (current.get("avg_cost", 0) - baseline["avg_cost"]) /
                baseline["avg_cost"]
            )
            
            if cost_change > self.deviation_thresholds["cost"]:
                regressions.append({
                    "metric": "avg_cost",
                    "severity": "warning",
                    "baseline_value": baseline["avg_cost"],
                    "current_value": current.get("avg_cost", 0),
                    "change_percent": cost_change * 100,
                    "message": f"Average cost increased by {cost_change*100:.1f}%"
                })
        
        # Check token usage
        if baseline.get("avg_tokens", 0) > 0:
            token_change = (
                (current.get("avg_tokens", 0) - baseline["avg_tokens"]) /
                baseline["avg_tokens"]
            )
            
            if token_change > self.deviation_thresholds["token_usage"]:
                regressions.append({
                    "metric": "avg_tokens",
                    "severity": "info",
                    "baseline_value": baseline["avg_tokens"],
                    "current_value": current.get("avg_tokens", 0),
                    "change_percent": token_change * 100,
                    "message": f"Average token usage increased by {token_change*100:.1f}%"
                })
        
        # Check tool usage changes
        baseline_tools = set(baseline.get("tool_usage", {}).keys())
        current_tools = set(current.get("tool_usage", {}).keys())
        
        new_tools = current_tools - baseline_tools
        missing_tools = baseline_tools - current_tools
        
        if new_tools:
            regressions.append({
                "metric": "tool_usage",
                "severity": "info",
                "message": f"New tools detected: {', '.join(new_tools)}",
                "new_tools": list(new_tools)
            })
        
        if missing_tools:
            regressions.append({
                "metric": "tool_usage",
                "severity": "warning",
                "message": f"Previously used tools no longer called: {', '.join(missing_tools)}",
                "missing_tools": list(missing_tools)
            })
        
        return regressions
    
    def _calculate_severity(self, regressions: List[Dict[str, Any]]) -> str:
        """Calculate overall severity level"""
        if not regressions:
            return "none"
        
        severities = [r.get("severity", "info") for r in regressions]
        
        if "critical" in severities:
            return "critical"
        elif "warning" in severities:
            return "warning"
        else:
            return "info"
    
    def compare_versions(
        self,
        agent_id: str,
        version_a: str,
        version_b: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Compare two versions of an agent
        
        Args:
            agent_id: Agent to analyze
            version_a: First version
            version_b: Second version
            db: Database session
            
        Returns:
            Comparison results
        """
        # Get traces for each version
        traces_a = db.query(Trace).filter(
            Trace.agent_id == agent_id,
            Trace.trace_data["version"].astext == version_a
        ).all()
        
        traces_b = db.query(Trace).filter(
            Trace.agent_id == agent_id,
            Trace.trace_data["version"].astext == version_b
        ).all()
        
        if not traces_a or not traces_b:
            return {
                "error": "Insufficient data for comparison",
                "version_a_traces": len(traces_a),
                "version_b_traces": len(traces_b)
            }
        
        # Calculate metrics for each version
        metrics_a = self._calculate_metrics(traces_a)
        metrics_b = self._calculate_metrics(traces_b)
        
        # Detect differences
        differences = self._detect_deviations(metrics_a, metrics_b)
        
        return {
            "agent_id": agent_id,
            "version_a": version_a,
            "version_b": version_b,
            "version_a_metrics": metrics_a,
            "version_b_metrics": metrics_b,
            "differences": differences,
            "has_regressions": any(
                d.get("severity") in ["critical", "warning"]
                for d in differences
            )
        }


# Singleton instance
regression_detector = RegressionDetector()
