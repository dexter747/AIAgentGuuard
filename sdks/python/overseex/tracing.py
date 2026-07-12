"""
OverseeX Tracing Module

Provides span and trace context management for tracing agent executions.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
from functools import wraps
import time
import uuid
import threading


@dataclass
class Span:
    """
    Represents a traced span of execution.

    Spans capture timing, inputs, outputs, and metadata for a unit of work.
    """
    name: str
    agent_id: Optional[str] = None
    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Timing
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    # Data
    input_data: Any = None
    output_data: Any = None
    status: str = "pending"
    error: Optional[str] = None

    # Trace data (tool calls, LLM calls, etc.)
    trace_data: Dict[str, Any] = field(default_factory=dict)

    # Child spans
    children: List["Span"] = field(default_factory=list)

    def set_input(self, data: Any):
        """Set the input data for this span."""
        self.input_data = data

    def set_output(self, data: Any):
        """Set the output data for this span."""
        self.output_data = data

    def set_status(self, status: str):
        """Set the status (success, error, pending)."""
        self.status = status

    def set_error(self, error: str):
        """Set error message."""
        self.error = error
        self.status = "error"

    def set_attribute(self, key: str, value: Any):
        """Set a custom attribute in metadata."""
        self.metadata[key] = value

    def add_tag(self, tag: str):
        """Add a tag to the span."""
        if tag not in self.tags:
            self.tags.append(tag)

    def record_llm_call(
        self,
        model: str,
        messages: Any,
        response: Any,
        usage: Optional[Dict[str, Any]] = None,
        duration_ms: int = 0,
        cost: float = 0.0,
    ):
        """
        Record an LLM call within this span.

        Args:
            model: Model name (e.g., "gpt-4", "claude-3-opus")
            messages: Input messages (list of dicts or string)
            response: LLM response (dict or string)
            usage: Token usage info (e.g., {"tokens": 150, "latency_ms": 500})
            duration_ms: Duration in milliseconds
            cost: Estimated cost
        """
        if "llm_calls" not in self.trace_data:
            self.trace_data["llm_calls"] = []

        # Normalize messages to string for storage
        if isinstance(messages, list):
            prompt_str = str(messages)[:2000]
        else:
            prompt_str = str(messages)[:2000]

        # Normalize response
        if isinstance(response, dict):
            response_str = str(response)[:2000]
        else:
            response_str = str(response)[:2000]

        # Extract token info
        tokens = 0
        if usage:
            tokens = usage.get("tokens", 0) or usage.get("total_tokens", 0)
            if usage.get("latency_ms"):
                duration_ms = usage.get("latency_ms", duration_ms)

        self.trace_data["llm_calls"].append({
            "model": model,
            "prompt": prompt_str,
            "response": response_str,
            "tokens": tokens,
            "duration_ms": duration_ms,
            "cost": cost,
            "usage": usage,
            "timestamp": time.time(),
        })

    def record_tool_call(
        self,
        tool_name: str,
        input_data: Any,
        output_data: Any,
        duration_ms: int = 0,
        success: bool = True,
    ):
        """
        Record a tool call within this span.

        Args:
            tool_name: Name of the tool called
            input_data: Input parameters to the tool
            output_data: Output/result from the tool
            duration_ms: Duration in milliseconds
            success: Whether the tool call succeeded
        """
        if "tool_calls" not in self.trace_data:
            self.trace_data["tool_calls"] = []

        self.trace_data["tool_calls"].append({
            "tool": tool_name,
            "input": str(input_data)[:1000],
            "output": str(output_data)[:1000],
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": time.time(),
        })

    def record_handoff(
        self,
        from_agent: str,
        to_agent: str,
        context: Optional[Dict[str, Any]] = None,
        handoff_type: str = "delegation",
        reason: Optional[str] = None,
    ):
        """
        Record an agent handoff within this span.

        Args:
            from_agent: Source agent ID/name
            to_agent: Target agent ID/name
            context: Context data passed during handoff
            handoff_type: Type of handoff (delegation, escalation, completion, error)
            reason: Optional reason for the handoff
        """
        if "handoffs" not in self.trace_data:
            self.trace_data["handoffs"] = []

        self.trace_data["handoffs"].append({
            "from_agent": from_agent,
            "to_agent": to_agent,
            "context": context or {},
            "handoff_type": handoff_type,
            "reason": reason,
            "timestamp": time.time(),
        })

    def end(self):
        """End the span and calculate duration."""
        self.end_time = time.time()

    @property
    def duration_ms(self) -> int:
        """Get duration in milliseconds."""
        if self.end_time is None:
            return int((time.time() - self.start_time) * 1000)
        return int((self.end_time - self.start_time) * 1000)

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "agent_id": self.agent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "error": self.error,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "trace_data": self.trace_data,
            "metadata": self.metadata,
            "tags": self.tags,
            "children": [child.to_dict() for child in self.children],
        }


class TraceContext:
    """
    Thread-local trace context for managing active spans.

    Allows nested spans to automatically link to their parents.
    """

    _local = threading.local()

    @classmethod
    def get_current_span(cls) -> Optional[Span]:
        """Get the current active span."""
        stack = getattr(cls._local, "span_stack", None)
        if stack:
            return stack[-1]
        return None

    @classmethod
    def push_span(cls, span: Span):
        """Push a span onto the context stack."""
        if not hasattr(cls._local, "span_stack"):
            cls._local.span_stack = []

        # Link to parent
        parent = cls.get_current_span()
        if parent:
            span.parent_span_id = parent.span_id
            parent.children.append(span)

        cls._local.span_stack.append(span)

    @classmethod
    def pop_span(cls) -> Optional[Span]:
        """Pop the current span from the context stack."""
        stack = getattr(cls._local, "span_stack", None)
        if stack:
            return stack.pop()
        return None

    @classmethod
    def clear(cls):
        """Clear the trace context."""
        cls._local.span_stack = []


def trace(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    capture_args: bool = True,
):
    """
    Standalone trace decorator (for use without OverseeX client).

    This creates local spans but doesn't send them to the API.
    Use client.trace for full functionality.

    Usage:
        @trace
        def my_function():
            pass

        @trace(name="custom_name")
        def my_function():
            pass
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            span_name = name or fn.__name__
            span = Span(name=span_name)

            TraceContext.push_span(span)

            try:
                if capture_args:
                    span.set_input({"args": args, "kwargs": kwargs})

                result = fn(*args, **kwargs)

                span.set_output(result)
                span.set_status("success")
                return result

            except Exception as e:
                span.set_error(str(e))
                raise
            finally:
                span.end()
                TraceContext.pop_span()

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


@contextmanager
def span_context(name: str, **kwargs):
    """
    Context manager for creating a span (standalone, without client).

    Usage:
        with span_context("operation") as span:
            span.set_attribute("key", "value")
            do_work()
    """
    span = Span(name=name, **kwargs)
    TraceContext.push_span(span)

    try:
        yield span
    except Exception as e:
        span.set_error(str(e))
        raise
    finally:
        span.end()
        TraceContext.pop_span()
