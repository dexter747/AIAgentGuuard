"""
Smart Mock Generation Service

Automatically generates mocks by learning from execution traces.
No ML required - uses pattern matching and response templates.
"""
import json
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MockPattern:
    """Represents a learned mock pattern from traces."""
    
    def __init__(
        self,
        tool_name: str,
        input_pattern: Dict[str, Any],
        response: Any,
        frequency: int = 1
    ):
        self.tool_name = tool_name
        self.input_pattern = input_pattern
        self.response = response
        self.frequency = frequency
        self.created_at = datetime.utcnow()
        self.last_seen = datetime.utcnow()
    
    def matches(self, input_data: Dict[str, Any]) -> bool:
        """Check if input matches this pattern."""
        return self._pattern_matches(self.input_pattern, input_data)
    
    def _pattern_matches(self, pattern: Any, data: Any) -> bool:
        """Recursively check pattern matching."""
        if pattern is None:
            return True
        
        if isinstance(pattern, dict) and isinstance(data, dict):
            for key, value in pattern.items():
                if key not in data:
                    return False
                if not self._pattern_matches(value, data[key]):
                    return False
            return True
        
        if isinstance(pattern, str):
            # Support regex patterns
            if pattern.startswith("regex:"):
                return bool(re.match(pattern[6:], str(data)))
            # Support type patterns
            if pattern.startswith("type:"):
                expected_type = pattern[5:]
                return type(data).__name__ == expected_type
            # Support wildcard
            if pattern == "*":
                return True
        
        return pattern == data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "tool_name": self.tool_name,
            "input_pattern": self.input_pattern,
            "response": self.response,
            "frequency": self.frequency,
            "created_at": self.created_at.isoformat(),
            "last_seen": self.last_seen.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockPattern":
        """Create from dictionary."""
        pattern = cls(
            tool_name=data["tool_name"],
            input_pattern=data["input_pattern"],
            response=data["response"],
            frequency=data.get("frequency", 1)
        )
        if "created_at" in data:
            pattern.created_at = datetime.fromisoformat(data["created_at"])
        if "last_seen" in data:
            pattern.last_seen = datetime.fromisoformat(data["last_seen"])
        return pattern


class SmartMockGenerator:
    """
    Learns mock patterns from execution traces and generates
    intelligent mocks without requiring ML.
    
    Features:
    - Pattern extraction from traces
    - Response variation generation
    - Error scenario generation
    - Edge case mock creation
    """
    
    def __init__(self):
        # In-memory pattern storage (would be database in production)
        self.patterns: Dict[str, List[MockPattern]] = defaultdict(list)
        self.api_schemas: Dict[str, Dict] = {}
        
        # Load known API schemas
        self._load_api_schemas()
    
    def _load_api_schemas(self):
        """Load known API response schemas."""
        self.api_schemas = {
            "openai": {
                "chat_completions": {
                    "response_template": {
                        "id": "chatcmpl-{uuid}",
                        "object": "chat.completion",
                        "created": "{timestamp}",
                        "model": "{model}",
                        "choices": [{
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "{content}"
                            },
                            "finish_reason": "stop"
                        }],
                        "usage": {
                            "prompt_tokens": "{prompt_tokens}",
                            "completion_tokens": "{completion_tokens}",
                            "total_tokens": "{total_tokens}"
                        }
                    }
                }
            },
            "stripe": {
                "charges": {
                    "response_template": {
                        "id": "ch_{id}",
                        "object": "charge",
                        "amount": "{amount}",
                        "currency": "{currency}",
                        "status": "succeeded",
                        "paid": True
                    }
                },
                "customers": {
                    "response_template": {
                        "id": "cus_{id}",
                        "object": "customer",
                        "email": "{email}",
                        "created": "{timestamp}"
                    }
                }
            },
            "sendgrid": {
                "send": {
                    "response_template": {
                        "message_id": "{uuid}",
                        "status": "delivered",
                        "timestamp": "{timestamp}"
                    }
                }
            },
            "twilio": {
                "messages": {
                    "response_template": {
                        "sid": "SM{id}",
                        "status": "sent",
                        "to": "{to}",
                        "from": "{from}",
                        "body": "{body}"
                    }
                }
            }
        }
    
    def learn_from_traces(
        self,
        traces: List[Dict[str, Any]],
        min_frequency: int = 2
    ) -> Dict[str, int]:
        """
        Learn mock patterns from execution traces.
        
        Args:
            traces: List of trace data with tool calls
            min_frequency: Minimum occurrences to create pattern
        
        Returns:
            Dict with count of patterns learned per tool
        """
        # Extract tool calls from traces
        tool_calls = []
        for trace in traces:
            metadata = trace.get("metadata", {})
            calls = metadata.get("tool_calls", [])
            tool_calls.extend(calls)
        
        # Group by tool and response pattern
        call_groups = defaultdict(list)
        for call in tool_calls:
            tool_name = call.get("name", call.get("tool", "unknown"))
            pattern_key = self._get_call_pattern_key(call)
            call_groups[(tool_name, pattern_key)].append(call)
        
        # Create patterns from frequent groups
        patterns_learned = defaultdict(int)
        
        for (tool_name, pattern_key), calls in call_groups.items():
            if len(calls) >= min_frequency:
                # Extract common pattern
                input_pattern = self._extract_input_pattern(calls)
                response_template = self._extract_response_template(calls)
                
                # Create and store pattern
                pattern = MockPattern(
                    tool_name=tool_name,
                    input_pattern=input_pattern,
                    response=response_template,
                    frequency=len(calls)
                )
                
                # Check if pattern already exists
                existing = self._find_similar_pattern(tool_name, input_pattern)
                if existing:
                    existing.frequency += len(calls)
                    existing.last_seen = datetime.utcnow()
                else:
                    self.patterns[tool_name].append(pattern)
                
                patterns_learned[tool_name] += 1
        
        return dict(patterns_learned)
    
    def _get_call_pattern_key(self, call: Dict) -> str:
        """Get pattern key for grouping similar calls."""
        tool_name = call.get("name", call.get("tool", ""))
        input_data = call.get("input", call.get("args", {}))
        
        # Create key from input structure
        if isinstance(input_data, dict):
            keys = sorted(input_data.keys())
            return f"{tool_name}:{':'.join(keys)}"
        return f"{tool_name}:simple"
    
    def _extract_input_pattern(self, calls: List[Dict]) -> Dict[str, Any]:
        """Extract common input pattern from similar calls."""
        if not calls:
            return {}
        
        # Get all input structures
        inputs = [call.get("input", call.get("args", {})) for call in calls]
        
        if not inputs or not isinstance(inputs[0], dict):
            return {"input": "type:str"}
        
        # Find common keys
        common_keys = set(inputs[0].keys())
        for inp in inputs[1:]:
            if isinstance(inp, dict):
                common_keys &= set(inp.keys())
        
        # Build pattern
        pattern = {}
        for key in common_keys:
            values = [inp.get(key) for inp in inputs if isinstance(inp, dict)]
            pattern[key] = self._infer_value_pattern(values)
        
        return pattern
    
    def _infer_value_pattern(self, values: List[Any]) -> Any:
        """Infer pattern for a list of values."""
        if not values:
            return "*"
        
        # Check if all same
        if len(set(str(v) for v in values)) == 1:
            return values[0]
        
        # Check type consistency
        types = set(type(v).__name__ for v in values if v is not None)
        if len(types) == 1:
            return f"type:{list(types)[0]}"
        
        return "*"
    
    def _extract_response_template(self, calls: List[Dict]) -> Any:
        """Extract response template from similar calls."""
        responses = [
            call.get("output", call.get("response", {}))
            for call in calls
        ]
        
        if not responses:
            return {"status": "ok"}
        
        # Use first response as template, replacing variable parts
        template = responses[0]
        
        if isinstance(template, dict):
            # Mark variable fields
            template = self._templatize_response(responses)
        
        return template
    
    def _templatize_response(self, responses: List[Dict]) -> Dict:
        """Create response template with variable markers."""
        if not responses:
            return {}
        
        template = {}
        first = responses[0]
        
        if not isinstance(first, dict):
            return {"response": first}
        
        for key in first.keys():
            values = [r.get(key) for r in responses if isinstance(r, dict)]
            
            if len(set(str(v) for v in values)) == 1:
                # Static value
                template[key] = values[0]
            else:
                # Variable value - create placeholder
                template[key] = f"{{{key}}}"
        
        return template
    
    def _find_similar_pattern(
        self,
        tool_name: str,
        input_pattern: Dict
    ) -> Optional[MockPattern]:
        """Find existing similar pattern."""
        for pattern in self.patterns.get(tool_name, []):
            if pattern.input_pattern == input_pattern:
                return pattern
        return None
    
    def generate_mock(
        self,
        tool_name: str,
        input_data: Optional[Dict] = None,
        scenario: str = "success"
    ) -> Dict[str, Any]:
        """
        Generate a mock for a tool.
        
        Args:
            tool_name: Name of the tool to mock
            input_data: Optional input data for context
            scenario: success, error, timeout, rate_limit
        
        Returns:
            Mock configuration with response and settings
        """
        # Check learned patterns first
        if tool_name in self.patterns:
            for pattern in sorted(
                self.patterns[tool_name],
                key=lambda p: p.frequency,
                reverse=True
            ):
                if input_data is None or pattern.matches(input_data):
                    response = self._populate_template(pattern.response)
                    return self._build_mock_config(
                        tool_name, response, scenario, pattern.frequency
                    )
        
        # Check API schemas
        api_response = self._generate_from_schema(tool_name, input_data)
        if api_response:
            return self._build_mock_config(tool_name, api_response, scenario)
        
        # Generate generic mock
        return self._generate_generic_mock(tool_name, input_data, scenario)
    
    def _populate_template(self, template: Any) -> Any:
        """Populate template placeholders with realistic values."""
        import uuid
        import time
        import random
        
        if isinstance(template, str):
            # Replace common placeholders
            result = template
            result = result.replace("{uuid}", str(uuid.uuid4())[:8])
            result = result.replace("{id}", str(random.randint(100000, 999999)))
            result = result.replace("{timestamp}", str(int(time.time())))
            return result
        
        if isinstance(template, dict):
            return {k: self._populate_template(v) for k, v in template.items()}
        
        if isinstance(template, list):
            return [self._populate_template(item) for item in template]
        
        return template
    
    def _generate_from_schema(
        self,
        tool_name: str,
        input_data: Optional[Dict]
    ) -> Optional[Dict]:
        """Generate response from known API schema."""
        # Try to match tool to known API
        tool_lower = tool_name.lower()
        
        for api_name, endpoints in self.api_schemas.items():
            if api_name in tool_lower:
                # Find matching endpoint
                for endpoint_name, config in endpoints.items():
                    if endpoint_name in tool_lower:
                        template = config.get("response_template", {})
                        return self._populate_template(template)
        
        return None
    
    def _generate_generic_mock(
        self,
        tool_name: str,
        input_data: Optional[Dict],
        scenario: str
    ) -> Dict[str, Any]:
        """Generate a generic mock response."""
        import uuid
        import time
        
        if scenario == "success":
            response = {
                "status": "success",
                "data": {
                    "id": str(uuid.uuid4())[:8],
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": "Mock response for " + tool_name
                }
            }
        elif scenario == "error":
            response = {
                "status": "error",
                "error": {
                    "code": "MOCK_ERROR",
                    "message": f"Simulated error for {tool_name}"
                }
            }
        elif scenario == "timeout":
            response = {
                "status": "error",
                "error": {
                    "code": "TIMEOUT",
                    "message": "Request timed out"
                }
            }
        elif scenario == "rate_limit":
            response = {
                "status": "error",
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "Rate limit exceeded",
                    "retry_after": 60
                }
            }
        else:
            response = {"status": scenario, "mock": True}
        
        return self._build_mock_config(tool_name, response, scenario)
    
    def _build_mock_config(
        self,
        tool_name: str,
        response: Any,
        scenario: str,
        confidence: int = 0
    ) -> Dict[str, Any]:
        """Build complete mock configuration."""
        config = {
            "tool_name": tool_name,
            "response": response,
            "scenario": scenario,
            "generated_at": datetime.utcnow().isoformat(),
            "confidence": min(confidence * 10, 100) if confidence else 50
        }
        
        # Add error handling for error scenarios
        if scenario == "error":
            config["status_code"] = 500
        elif scenario == "timeout":
            config["status_code"] = 408
            config["delay_ms"] = 30000
        elif scenario == "rate_limit":
            config["status_code"] = 429
            config["headers"] = {"Retry-After": "60"}
        else:
            config["status_code"] = 200
        
        return config
    
    def generate_mock_suite(
        self,
        tool_names: List[str],
        include_errors: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Generate complete mock suite for multiple tools.
        
        Args:
            tool_names: List of tools to mock
            include_errors: Include error scenarios
        
        Returns:
            Dict mapping tool names to list of mock configs
        """
        suite = {}
        
        for tool_name in tool_names:
            mocks = []
            
            # Success mock
            mocks.append(self.generate_mock(tool_name, scenario="success"))
            
            if include_errors:
                # Error scenarios
                mocks.append(self.generate_mock(tool_name, scenario="error"))
                mocks.append(self.generate_mock(tool_name, scenario="timeout"))
                mocks.append(self.generate_mock(tool_name, scenario="rate_limit"))
            
            suite[tool_name] = mocks
        
        return suite
    
    def export_mocks_as_code(
        self,
        mocks: Dict[str, List[Dict]],
        framework: str = "pytest"
    ) -> str:
        """
        Export mock configurations as Python code.
        
        Args:
            mocks: Mock suite from generate_mock_suite
            framework: Test framework (pytest, unittest)
        
        Returns:
            Python code string
        """
        code = '''"""
Auto-generated mock configurations
Generated by OverseeX Smart Mock Generator
"""

from overseex import mock_tools, ToolMock


def get_mocks():
    """Get configured mocks for testing."""
    mocks = {}
    
'''
        
        for tool_name, configs in mocks.items():
            success_config = next(
                (c for c in configs if c["scenario"] == "success"),
                configs[0] if configs else None
            )
            
            if success_config:
                response = json.dumps(success_config["response"], indent=8)
                code += f'''    # {tool_name}
    mocks["{tool_name}"] = ToolMock("{tool_name}")
    mocks["{tool_name}"].set_default_response({response})
    
'''
        
        code += '''    return mocks


# Pytest fixture
@pytest.fixture
def mock_tools_fixture():
    """Fixture providing configured mocks."""
    return get_mocks()
'''
        
        return code
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Get statistics about learned patterns."""
        stats = {
            "total_patterns": sum(len(p) for p in self.patterns.values()),
            "tools_covered": len(self.patterns),
            "patterns_by_tool": {
                name: len(patterns)
                for name, patterns in self.patterns.items()
            },
            "most_frequent": []
        }
        
        # Find most frequent patterns
        all_patterns = []
        for tool_name, patterns in self.patterns.items():
            for pattern in patterns:
                all_patterns.append((tool_name, pattern.frequency, pattern))
        
        all_patterns.sort(key=lambda x: x[1], reverse=True)
        stats["most_frequent"] = [
            {"tool": p[0], "frequency": p[1]}
            for p in all_patterns[:10]
        ]
        
        return stats


# Singleton instance
smart_mock_generator = SmartMockGenerator()
