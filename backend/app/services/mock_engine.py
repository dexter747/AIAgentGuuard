"""
Tool Mocking Service for OverseeX
Intelligent mocking system for API calls during agent testing.
"""
import json
import re
import hashlib
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from contextlib import contextmanager
import logging
import copy

logger = logging.getLogger(__name__)


@dataclass
class MockResponse:
    """Represents a mock API response."""
    status_code: int = 200
    body: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    delay_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "status_code": self.status_code,
            "body": self.body,
            "headers": self.headers,
            "delay_ms": self.delay_ms
        }


@dataclass  
class MockCall:
    """Records a mock call for verification."""
    tool_name: str
    method: str
    args: tuple
    kwargs: Dict[str, Any]
    response: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ToolMock:
    """
    Mock for a single tool/API.
    Supports conditional responses, failure injection, and stateful mocking.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.calls: List[MockCall] = []
        self.responses: List[Dict[str, Any]] = []
        self.default_response: Optional[MockResponse] = None
        self.failure_mode: Optional[Dict[str, Any]] = None
        self.state: Dict[str, Any] = {}
        self.call_count = 0
        
    def set_response(
        self,
        response: Any,
        status_code: int = 200,
        condition: Optional[Callable] = None,
        match_args: Optional[Dict[str, Any]] = None
    ):
        """
        Set a response for this mock.
        
        Args:
            response: The response body to return
            status_code: HTTP status code
            condition: Optional callable that takes (args, kwargs) and returns bool
            match_args: Optional dict of argument patterns to match
        """
        self.responses.append({
            "response": MockResponse(status_code=status_code, body=response),
            "condition": condition,
            "match_args": match_args
        })
        
    def set_default_response(self, response: Any, status_code: int = 200):
        """Set the default response when no conditions match."""
        self.default_response = MockResponse(status_code=status_code, body=response)
        
    def inject_failure(
        self,
        error_type: str = "timeout",
        error_code: Optional[int] = None,
        error_message: str = "Mock failure",
        probability: float = 1.0
    ):
        """
        Inject failures for testing error handling.
        
        Args:
            error_type: Type of failure (timeout, rate_limit, server_error, connection_error)
            error_code: HTTP error code
            error_message: Error message to return
            probability: Probability of failure (0.0-1.0)
        """
        self.failure_mode = {
            "type": error_type,
            "code": error_code or self._get_default_error_code(error_type),
            "message": error_message,
            "probability": probability
        }
        
    def _get_default_error_code(self, error_type: str) -> int:
        """Get default error code for error type."""
        codes = {
            "timeout": 408,
            "rate_limit": 429,
            "server_error": 500,
            "connection_error": 503,
            "not_found": 404,
            "unauthorized": 401,
            "forbidden": 403
        }
        return codes.get(error_type, 500)
    
    def clear_failure(self):
        """Clear failure injection."""
        self.failure_mode = None
        
    def __call__(self, *args, **kwargs) -> Any:
        """Execute the mock and return appropriate response."""
        import random
        
        self.call_count += 1
        
        # Check for failure injection
        if self.failure_mode:
            if random.random() < self.failure_mode["probability"]:
                error = MockError(
                    error_type=self.failure_mode["type"],
                    status_code=self.failure_mode["code"],
                    message=self.failure_mode["message"]
                )
                self._record_call(args, kwargs, error)
                raise error
        
        # Find matching response
        response = self._find_matching_response(args, kwargs)
        
        # Record the call
        self._record_call(args, kwargs, response)
        
        return response.body if isinstance(response, MockResponse) else response
    
    def _find_matching_response(self, args: tuple, kwargs: Dict) -> MockResponse:
        """Find the appropriate response for the given arguments."""
        for resp_config in self.responses:
            condition = resp_config.get("condition")
            match_args = resp_config.get("match_args")
            
            # Check condition function
            if condition and not condition(args, kwargs):
                continue
                
            # Check argument matching
            if match_args:
                if not self._args_match(kwargs, match_args):
                    continue
            
            return resp_config["response"]
        
        # Return default response
        if self.default_response:
            return self.default_response
            
        # Generate default response based on tool type
        return MockResponse(status_code=200, body={"status": "ok", "mock": True})
    
    def _args_match(self, kwargs: Dict, patterns: Dict) -> bool:
        """Check if kwargs match the patterns."""
        for key, pattern in patterns.items():
            if key not in kwargs:
                return False
            value = kwargs[key]
            
            if isinstance(pattern, str) and pattern.startswith("regex:"):
                if not re.match(pattern[6:], str(value)):
                    return False
            elif isinstance(pattern, type):
                if not isinstance(value, pattern):
                    return False
            elif value != pattern:
                return False
                
        return True
    
    def _record_call(self, args: tuple, kwargs: Dict, response: Any):
        """Record a call for later verification."""
        self.calls.append(MockCall(
            tool_name=self.name,
            method="__call__",
            args=args,
            kwargs=kwargs,
            response=response
        ))
        
    @property
    def called(self) -> bool:
        """Whether this mock was called."""
        return len(self.calls) > 0
    
    @property
    def call_args(self) -> Optional[tuple]:
        """Arguments of the last call."""
        if self.calls:
            last_call = self.calls[-1]
            return last_call.args, last_call.kwargs
        return None
    
    @property
    def call_args_list(self) -> List[tuple]:
        """List of all call arguments."""
        return [(c.args, c.kwargs) for c in self.calls]
    
    def assert_called(self):
        """Assert that the mock was called."""
        assert self.called, f"Expected {self.name} to be called, but it wasn't"
        
    def assert_called_with(self, *args, **kwargs):
        """Assert the mock was called with specific arguments."""
        assert self.called, f"Expected {self.name} to be called"
        last_args, last_kwargs = self.call_args
        assert last_args == args, f"Expected args {args}, got {last_args}"
        assert last_kwargs == kwargs, f"Expected kwargs {kwargs}, got {last_kwargs}"
        
    def assert_called_times(self, count: int):
        """Assert the mock was called a specific number of times."""
        assert self.call_count == count, f"Expected {count} calls, got {self.call_count}"
        
    def reset(self):
        """Reset the mock state."""
        self.calls = []
        self.call_count = 0
        self.state = {}


class MockError(Exception):
    """Exception raised by mock failures."""
    
    def __init__(self, error_type: str, status_code: int, message: str):
        self.error_type = error_type
        self.status_code = status_code
        self.message = message
        super().__init__(f"{error_type}: {message} (status: {status_code})")


class MockEngine:
    """
    Central mock engine that manages all tool mocks.
    Provides trace-based response generation and stateful mocking.
    """
    
    # Pre-configured mock responses for common tools
    TOOL_TEMPLATES = {
        "openai": {
            "chat.completions.create": MockResponse(
                status_code=200,
                body={
                    "id": "mock-completion-id",
                    "object": "chat.completion",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "This is a mock response from the AI."
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
                }
            )
        },
        "stripe": {
            "charges.create": MockResponse(
                status_code=200,
                body={
                    "id": "ch_mock_123",
                    "object": "charge",
                    "amount": 2000,
                    "currency": "usd",
                    "status": "succeeded"
                }
            ),
            "customers.create": MockResponse(
                status_code=200,
                body={
                    "id": "cus_mock_123",
                    "object": "customer",
                    "email": "mock@example.com"
                }
            )
        },
        "google_calendar": {
            "events.insert": MockResponse(
                status_code=200,
                body={
                    "id": "evt_mock_123",
                    "status": "confirmed",
                    "summary": "Mock Event",
                    "start": {"dateTime": "2026-01-25T14:00:00Z"},
                    "end": {"dateTime": "2026-01-25T15:00:00Z"}
                }
            ),
            "events.list": MockResponse(
                status_code=200,
                body={"items": []}
            )
        },
        "slack": {
            "chat.postMessage": MockResponse(
                status_code=200,
                body={
                    "ok": True,
                    "channel": "C123456",
                    "ts": "1234567890.123456",
                    "message": {"text": "Mock message"}
                }
            )
        },
        "sendgrid": {
            "mail.send": MockResponse(
                status_code=202,
                body={"status": "accepted"}
            )
        },
        "twilio": {
            "messages.create": MockResponse(
                status_code=201,
                body={
                    "sid": "SM_mock_123",
                    "status": "queued"
                }
            )
        }
    }
    
    def __init__(self):
        self.mocks: Dict[str, ToolMock] = {}
        self.trace_responses: Dict[str, List[Dict]] = {}  # Hash -> responses from traces
        self.global_state: Dict[str, Any] = {}
        self.call_history: List[MockCall] = []
        
    def get_mock(self, tool_name: str) -> ToolMock:
        """Get or create a mock for a tool."""
        if tool_name not in self.mocks:
            self.mocks[tool_name] = ToolMock(tool_name)
            self._apply_template(tool_name)
        return self.mocks[tool_name]
    
    def __getitem__(self, tool_name: str) -> ToolMock:
        """Allow dictionary-style access to mocks."""
        return self.get_mock(tool_name)
    
    def _apply_template(self, tool_name: str):
        """Apply pre-configured templates if available."""
        # Check for exact match
        if tool_name in self.TOOL_TEMPLATES:
            for method, response in self.TOOL_TEMPLATES[tool_name].items():
                self.mocks[tool_name].set_response(response.body, response.status_code)
            return
            
        # Check for partial match (e.g., "stripe.charges" matches "stripe")
        for template_name in self.TOOL_TEMPLATES:
            if tool_name.startswith(template_name):
                method_part = tool_name[len(template_name) + 1:] if len(tool_name) > len(template_name) else None
                templates = self.TOOL_TEMPLATES[template_name]
                
                if method_part and method_part in templates:
                    response = templates[method_part]
                    self.mocks[tool_name].set_response(response.body, response.status_code)
                elif templates:
                    # Use first template as default
                    first_response = list(templates.values())[0]
                    self.mocks[tool_name].set_response(first_response.body, first_response.status_code)
    
    def learn_from_trace(self, trace_data: Dict[str, Any]):
        """
        Learn mock responses from a trace.
        Extracts tool calls and their responses to use in future mocks.
        """
        tool_calls = []
        
        # Extract tool calls from various trace formats
        if "tool_calls" in trace_data:
            tool_calls = trace_data["tool_calls"]
        elif "steps" in trace_data:
            tool_calls = [s for s in trace_data["steps"] if s.get("type") == "tool_call"]
        elif "metadata" in trace_data and "tool_calls" in trace_data["metadata"]:
            tool_calls = trace_data["metadata"]["tool_calls"]
        
        for call in tool_calls:
            tool_name = call.get("tool", call.get("name", "unknown"))
            args = call.get("args", call.get("input", {}))
            response = call.get("response", call.get("output", {}))
            
            # Create a hash for the call signature
            call_hash = self._hash_call(tool_name, args)
            
            if call_hash not in self.trace_responses:
                self.trace_responses[call_hash] = []
            
            self.trace_responses[call_hash].append({
                "args": args,
                "response": response,
                "trace_id": trace_data.get("id"),
                "timestamp": trace_data.get("created_at")
            })
            
            # Also configure the mock
            mock = self.get_mock(tool_name)
            mock.set_response(response, match_args=args if isinstance(args, dict) else None)
    
    def _hash_call(self, tool_name: str, args: Any) -> str:
        """Create a hash for a tool call signature."""
        data = json.dumps({"tool": tool_name, "args": args}, sort_keys=True, default=str)
        return hashlib.md5(data.encode()).hexdigest()
    
    def inject_failure(
        self,
        tool_name: str,
        error_type: str = "server_error",
        error_code: Optional[int] = None,
        probability: float = 1.0
    ):
        """Inject a failure for a specific tool."""
        mock = self.get_mock(tool_name)
        mock.inject_failure(error_type, error_code, probability=probability)
        
    def clear_failures(self):
        """Clear all failure injections."""
        for mock in self.mocks.values():
            mock.clear_failure()
            
    def reset_all(self):
        """Reset all mocks."""
        for mock in self.mocks.values():
            mock.reset()
        self.call_history = []
        self.global_state = {}
        
    def get_call_history(self) -> List[Dict[str, Any]]:
        """Get the complete call history across all mocks."""
        all_calls = []
        for mock in self.mocks.values():
            for call in mock.calls:
                all_calls.append({
                    "tool": call.tool_name,
                    "args": call.args,
                    "kwargs": call.kwargs,
                    "response": call.response,
                    "timestamp": call.timestamp.isoformat()
                })
        return sorted(all_calls, key=lambda x: x["timestamp"])
    
    def verify_call_sequence(self, expected_sequence: List[str]) -> bool:
        """
        Verify that tools were called in the expected sequence.
        
        Args:
            expected_sequence: List of tool names in expected order
            
        Returns:
            True if sequence matches, False otherwise
        """
        actual_sequence = [c["tool"] for c in self.get_call_history()]
        return actual_sequence == expected_sequence
    
    def get_cost_savings(self) -> Dict[str, Any]:
        """
        Calculate cost savings from using mocks instead of real APIs.
        """
        # Estimated costs per API call
        api_costs = {
            "openai": 0.03,  # ~$0.03 per GPT-4 call
            "stripe": 0.01,
            "sendgrid": 0.001,
            "twilio": 0.0075,
            "google_calendar": 0.0001,
            "slack": 0.0001
        }
        
        total_saved = 0.0
        breakdown = {}
        
        for mock in self.mocks.values():
            cost_per_call = 0.0
            for cost_prefix, cost in api_costs.items():
                if mock.name.startswith(cost_prefix):
                    cost_per_call = cost
                    break
            
            saved = mock.call_count * cost_per_call
            if saved > 0:
                breakdown[mock.name] = {
                    "calls": mock.call_count,
                    "cost_per_call": cost_per_call,
                    "saved": saved
                }
                total_saved += saved
        
        return {
            "total_saved": round(total_saved, 4),
            "breakdown": breakdown,
            "total_mock_calls": sum(m.call_count for m in self.mocks.values())
        }


# Context manager for easy mock usage
@contextmanager
def mock_tools(engine: Optional[MockEngine] = None):
    """
    Context manager for mocking tools during agent execution.
    
    Usage:
        with mock_tools() as mocks:
            mocks['stripe'].set_response({"status": "succeeded"})
            result = agent.run("process payment")
            mocks['stripe'].assert_called()
    """
    mock_engine = engine or MockEngine()
    try:
        yield mock_engine
    finally:
        # Log cost savings
        savings = mock_engine.get_cost_savings()
        if savings["total_saved"] > 0:
            logger.info(f"Mock cost savings: ${savings['total_saved']:.4f}")


# Singleton instance
mock_engine = MockEngine()
