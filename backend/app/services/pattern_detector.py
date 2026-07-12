"""
Pattern Detector Service - Analyzes traces to identify patterns for test generation
"""
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Analyzes agent execution traces to detect patterns that should be tested
    
    Identifies:
    - Common input patterns
    - Tool call sequences
    - Error patterns
    - Performance bottlenecks
    - Edge cases
    """
    
    def __init__(self):
        self.min_pattern_frequency = 2  # Minimum occurrences to consider a pattern
    
    def analyze_traces(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze multiple traces to identify patterns
        
        Args:
            traces: List of trace data dictionaries
            
        Returns:
            Dictionary containing detected patterns and statistics
        """
        if not traces:
            return {
                "total_traces": 0,
                "patterns": [],
                "tool_sequences": [],
                "error_patterns": [],
                "performance_insights": {},
                "edge_cases": []
            }
        
        patterns = {
            "total_traces": len(traces),
            "patterns": self._detect_input_patterns(traces),
            "tool_sequences": self._detect_tool_sequences(traces),
            "error_patterns": self._detect_error_patterns(traces),
            "performance_insights": self._analyze_performance(traces),
            "edge_cases": self._identify_edge_cases(traces)
        }
        
        return patterns
    
    def _detect_input_patterns(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect common input patterns across traces"""
        input_patterns = []
        
        # Extract and categorize inputs
        inputs_by_length = defaultdict(list)
        inputs_by_type = defaultdict(list)
        
        for trace in traces:
            input_data = trace.get("input", "")
            
            # Categorize by length
            length_category = self._categorize_length(len(str(input_data)))
            inputs_by_length[length_category].append(input_data)
            
            # Categorize by type
            input_type = self._detect_input_type(input_data)
            inputs_by_type[input_type].append(input_data)
        
        # Build pattern report
        for length_cat, inputs in inputs_by_length.items():
            if len(inputs) >= self.min_pattern_frequency:
                input_patterns.append({
                    "type": "length_pattern",
                    "category": length_cat,
                    "count": len(inputs),
                    "percentage": (len(inputs) / len(traces)) * 100,
                    "examples": inputs[:3]
                })
        
        for input_type, inputs in inputs_by_type.items():
            if len(inputs) >= self.min_pattern_frequency:
                input_patterns.append({
                    "type": "content_pattern",
                    "category": input_type,
                    "count": len(inputs),
                    "percentage": (len(inputs) / len(traces)) * 100,
                    "examples": inputs[:3]
                })
        
        return input_patterns
    
    def _detect_tool_sequences(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect common tool call sequences"""
        sequences = []
        sequence_counter = Counter()
        
        for trace in traces:
            tool_calls = self._extract_tool_calls(trace)
            if tool_calls:
                # Create sequence string
                tool_names = [tc.get("tool", tc.get("name", "unknown")) for tc in tool_calls]
                sequence = " -> ".join(tool_names)
                sequence_counter[sequence] += 1
        
        # Find patterns (sequences that occur multiple times)
        for sequence, count in sequence_counter.most_common(10):
            if count >= self.min_pattern_frequency:
                sequences.append({
                    "sequence": sequence,
                    "count": count,
                    "percentage": (count / len(traces)) * 100,
                    "tools": sequence.split(" -> ")
                })
        
        return sequences
    
    def _detect_error_patterns(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect common error patterns"""
        error_patterns = []
        error_messages = Counter()
        error_types = Counter()
        
        for trace in traces:
            status = trace.get("status", "success")
            
            if status in ["error", "failed", "failure"]:
                # Extract error information
                error_msg = (
                    trace.get("error") or
                    trace.get("error_message") or
                    trace.get("metadata", {}).get("error", "")
                )
                
                if error_msg:
                    # Normalize error message (remove specific values)
                    normalized = self._normalize_error_message(str(error_msg))
                    error_messages[normalized] += 1
                    
                    # Categorize error type
                    error_type = self._categorize_error(str(error_msg))
                    error_types[error_type] += 1
        
        # Build error patterns
        for error_msg, count in error_messages.most_common(5):
            if count >= self.min_pattern_frequency:
                error_patterns.append({
                    "type": "error_message",
                    "pattern": error_msg,
                    "count": count,
                    "percentage": (count / len(traces)) * 100
                })
        
        for error_type, count in error_types.most_common():
            error_patterns.append({
                "type": "error_category",
                "pattern": error_type,
                "count": count,
                "percentage": (count / len(traces)) * 100
            })
        
        return error_patterns
    
    def _analyze_performance(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance patterns across traces"""
        durations = []
        token_counts = []
        costs = []
        
        for trace in traces:
            # Duration
            duration = trace.get("total_duration_ms") or trace.get("duration_ms", 0)
            if duration:
                durations.append(duration)
            
            # Tokens
            tokens = trace.get("token_count") or trace.get("metadata", {}).get("tokens", 0)
            if tokens:
                token_counts.append(tokens)
            
            # Cost
            cost_str = trace.get("cost_usd", "0")
            try:
                cost = float(cost_str) if cost_str else 0
                if cost > 0:
                    costs.append(cost)
            except (ValueError, TypeError):
                pass
        
        insights = {
            "duration_ms": self._calculate_stats(durations),
            "token_count": self._calculate_stats(token_counts),
            "cost_usd": self._calculate_stats(costs)
        }
        
        # Add performance warnings
        warnings = []
        if durations:
            avg_duration = sum(durations) / len(durations)
            if avg_duration > 5000:
                warnings.append(f"Average duration ({avg_duration:.0f}ms) exceeds 5s")
        
        if costs:
            avg_cost = sum(costs) / len(costs)
            if avg_cost > 0.10:
                warnings.append(f"Average cost (${avg_cost:.4f}) exceeds $0.10")
        
        insights["warnings"] = warnings
        
        return insights
    
    def _identify_edge_cases(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify traces that represent edge cases"""
        edge_cases = []
        
        # Calculate baseline metrics
        durations = [t.get("total_duration_ms", 0) for t in traces if t.get("total_duration_ms")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        for i, trace in enumerate(traces):
            edge_case_reasons = []
            
            input_data = str(trace.get("input", ""))
            
            # Very short input
            if len(input_data.strip()) < 5:
                edge_case_reasons.append("very_short_input")
            
            # Very long input
            if len(input_data) > 2000:
                edge_case_reasons.append("very_long_input")
            
            # Contains special characters
            if re.search(r'[<>{}|\\^~\[\]`@#$%&*]', input_data):
                edge_case_reasons.append("special_characters")
            
            # Unicode or emoji
            if any(ord(char) > 127 for char in input_data):
                edge_case_reasons.append("unicode_content")
            
            # Extreme duration
            duration = trace.get("total_duration_ms", 0)
            if avg_duration > 0:
                if duration > avg_duration * 3:
                    edge_case_reasons.append("extremely_slow")
                elif duration < avg_duration * 0.2 and duration > 0:
                    edge_case_reasons.append("extremely_fast")
            
            # Error cases
            if trace.get("status") in ["error", "failed"]:
                edge_case_reasons.append("error_case")
            
            # High token usage
            tokens = trace.get("token_count", 0)
            if tokens > 4000:
                edge_case_reasons.append("high_token_usage")
            
            # If this trace has edge case characteristics
            if edge_case_reasons:
                edge_cases.append({
                    "trace_index": i,
                    "trace_id": trace.get("id"),
                    "reasons": edge_case_reasons,
                    "input_preview": input_data[:100],
                    "duration_ms": duration
                })
        
        return edge_cases
    
    def _categorize_length(self, length: int) -> str:
        """Categorize input by length"""
        if length < 10:
            return "very_short"
        elif length < 50:
            return "short"
        elif length < 200:
            return "medium"
        elif length < 1000:
            return "long"
        else:
            return "very_long"
    
    def _detect_input_type(self, input_data: Any) -> str:
        """Detect the type of input"""
        input_str = str(input_data)
        
        # Check for question
        if input_str.strip().endswith("?"):
            return "question"
        
        # Check for command
        if any(input_str.lower().startswith(cmd) for cmd in ["create", "delete", "update", "get", "list", "find"]):
            return "command"
        
        # Check for JSON
        if input_str.strip().startswith("{") and input_str.strip().endswith("}"):
            return "json_object"
        
        # Check for structured data
        if ":" in input_str and "," in input_str:
            return "structured_data"
        
        # Check for code
        if any(keyword in input_str for keyword in ["def ", "class ", "function ", "import "]):
            return "code"
        
        return "natural_language"
    
    def _extract_tool_calls(self, trace: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tool calls from trace"""
        tool_calls = []
        
        if "tool_calls" in trace:
            tool_calls = trace["tool_calls"]
        elif "steps" in trace:
            for step in trace["steps"]:
                if step.get("type") == "tool_call" or step.get("tool"):
                    tool_calls.append(step)
        elif "actions" in trace:
            tool_calls = trace["actions"]
        
        return tool_calls
    
    def _normalize_error_message(self, error_msg: str) -> str:
        """Normalize error message by removing specific values"""
        # Remove numbers
        normalized = re.sub(r'\d+', 'N', error_msg)
        
        # Remove UUIDs
        normalized = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            'UUID',
            normalized,
            flags=re.IGNORECASE
        )
        
        # Remove URLs
        normalized = re.sub(r'https?://\S+', 'URL', normalized)
        
        # Remove file paths
        normalized = re.sub(r'/[\w/.-]+', 'PATH', normalized)
        
        return normalized[:200]  # Limit length
    
    def _categorize_error(self, error_msg: str) -> str:
        """Categorize error by type"""
        error_lower = error_msg.lower()
        
        if "timeout" in error_lower:
            return "timeout"
        elif "connection" in error_lower or "network" in error_lower:
            return "network_error"
        elif "authentication" in error_lower or "unauthorized" in error_lower:
            return "auth_error"
        elif "not found" in error_lower or "404" in error_msg:
            return "not_found"
        elif "validation" in error_lower or "invalid" in error_lower:
            return "validation_error"
        elif "rate limit" in error_lower:
            return "rate_limit"
        elif "permission" in error_lower or "forbidden" in error_lower:
            return "permission_error"
        else:
            return "unknown_error"
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistics for a list of values"""
        if not values:
            return {
                "min": 0,
                "max": 0,
                "avg": 0,
                "median": 0,
                "count": 0
            }
        
        sorted_values = sorted(values)
        count = len(values)
        
        return {
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "avg": sum(values) / count,
            "median": sorted_values[count // 2],
            "count": count
        }
    
    def suggest_test_cases(self, patterns: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Suggest test cases based on detected patterns
        
        Args:
            patterns: Output from analyze_traces()
            
        Returns:
            List of suggested test cases with rationale
        """
        suggestions = []
        
        # Suggest tests for common input patterns
        for pattern in patterns.get("patterns", []):
            if pattern["percentage"] > 10:
                suggestions.append({
                    "type": "input_pattern",
                    "rationale": f"{pattern['category']} inputs represent {pattern['percentage']:.1f}% of traffic",
                    "priority": "high" if pattern["percentage"] > 30 else "medium",
                    "example": str(pattern["examples"][0]) if pattern["examples"] else ""
                })
        
        # Suggest tests for common tool sequences
        for sequence in patterns.get("tool_sequences", []):
            if sequence["percentage"] > 5:
                suggestions.append({
                    "type": "tool_sequence",
                    "rationale": f"Tool sequence '{sequence['sequence']}' occurs in {sequence['percentage']:.1f}% of executions",
                    "priority": "high",
                    "example": sequence["sequence"]
                })
        
        # Suggest tests for error patterns
        for error in patterns.get("error_patterns", []):
            if error["count"] >= 2:
                suggestions.append({
                    "type": "error_handling",
                    "rationale": f"Error '{error['pattern']}' occurred {error['count']} times",
                    "priority": "critical",
                    "example": error["pattern"]
                })
        
        # Suggest performance tests
        perf = patterns.get("performance_insights", {})
        if perf.get("warnings"):
            for warning in perf["warnings"]:
                suggestions.append({
                    "type": "performance",
                    "rationale": warning,
                    "priority": "medium",
                    "example": ""
                })
        
        # Suggest edge case tests
        edge_cases = patterns.get("edge_cases", [])
        if len(edge_cases) > 0:
            suggestions.append({
                "type": "edge_cases",
                "rationale": f"Found {len(edge_cases)} edge cases that should be tested",
                "priority": "high",
                "example": f"{len(edge_cases)} unique edge cases identified"
            })
        
        return suggestions


# Singleton instance
pattern_detector = PatternDetector()
