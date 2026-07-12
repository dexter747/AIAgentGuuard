"""
OverseeX Main Client

Core client class for interacting with the OverseeX API.
"""

from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
from contextlib import contextmanager
import time
import uuid
import logging
import requests

from .tracing import Span, TraceContext
from .coordination import CoordinationClient
from .models import Agent, Trace

logger = logging.getLogger("overseex")


class OverseeX:
    """
    Main OverseeX client for tracing and monitoring AI agents.

    Usage:
        from overseex import OverseeX

        # Initialize
        client = OverseeX(api_key="ox_live_xxx")

        # Trace a function
        @client.trace
        def my_agent(query: str) -> str:
            return llm.generate(query)

        # Use spans for more control
        with client.span("custom_operation") as span:
            result = do_something()
            span.set_attribute("result_size", len(result))

        # Access sub-clients
        issues = client.coordination.list_issues()
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.overseex.com",
        agent_id: Optional[str] = None,
        auto_register_agent: bool = True,
        agent_name: Optional[str] = None,
        timeout: int = 30,
        debug: bool = False,
    ):
        """
        Initialize OverseeX client.

        Args:
            api_key: Your OverseeX API key (starts with ox_live_ or ox_test_)
            base_url: API base URL (default: https://api.overseex.com)
            agent_id: Existing agent ID to use for traces
            auto_register_agent: Auto-create agent if not specified
            agent_name: Name for auto-registered agent
            timeout: Request timeout in seconds
            debug: Enable debug logging
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.debug = debug

        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

        # HTTP session
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OverseeX-Python/0.2.0",
        })

        # Agent setup
        self.agent_id = agent_id
        if not agent_id and auto_register_agent:
            self.agent_id = self._register_agent(agent_name or "Python Agent")
        elif not agent_id:
            # Try to use first available agent
            try:
                agents_response = self._request("GET", "/api/v1/agents", params={"limit": 1})
                # API returns dict with 'items' key
                if isinstance(agents_response, dict) and "items" in agents_response:
                    agents = agents_response["items"]
                elif isinstance(agents_response, list):
                    agents = agents_response
                else:
                    agents = []
                    
                if agents:
                    self.agent_id = agents[0]["id"]
                    logger.info(f"Using existing agent: {agents[0].get('name', 'N/A')} ({self.agent_id})")
                else:
                    raise ValueError("No agents found. Please create an agent first or set auto_register_agent=True")
            except Exception as e:
                logger.warning(f"Failed to fetch agents: {e}")
                self.agent_id = None

        # Active trace context
        self._trace_context: Optional[TraceContext] = None

        # Sub-clients
        self._coordination: Optional[CoordinationClient] = None

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.base_url}{path}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise

    def _register_agent(self, name: str) -> str:
        """Register a new agent and return its ID."""
        try:
            data = self._request("POST", "/api/v1/agents", data={
                "name": name,
                "description": "Auto-registered by OverseeX Python SDK",
                "endpoint_url": "python://local",
                "metadata": {"sdk": "python", "version": "0.2.0"},
            })
            agent_id = data.get("id")
            logger.info(f"Registered agent: {name} ({agent_id})")
            return agent_id
        except Exception as e:
            logger.warning(f"Failed to register agent: {e}")
            return "default-agent"

    @property
    def coordination(self) -> CoordinationClient:
        """Get the coordination sub-client."""
        if self._coordination is None:
            self._coordination = CoordinationClient(self)
        return self._coordination

    # ==================
    # Tracing Methods
    # ==================

    def trace(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        capture_input: bool = True,
        capture_output: bool = True,
        tags: Optional[List[str]] = None,
    ):
        """
        Decorator to trace a function.

        Can be used with or without arguments:

            @client.trace
            def my_func():
                pass

            @client.trace(name="custom_name", tags=["production"])
            def my_func():
                pass
        """
        def decorator(fn: Callable) -> Callable:
            @wraps(fn)
            def wrapper(*args, **kwargs):
                trace_name = name or fn.__name__

                with self.span(trace_name, tags=tags) as span:
                    # Capture input
                    if capture_input:
                        try:
                            input_data = {
                                "args": [str(a)[:500] for a in args],
                                "kwargs": {k: str(v)[:500] for k, v in kwargs.items()},
                            }
                            span.set_input(input_data)
                        except Exception:
                            pass

                    # Execute function
                    try:
                        result = fn(*args, **kwargs)

                        # Capture output
                        if capture_output:
                            try:
                                span.set_output(str(result)[:2000])
                            except Exception:
                                pass

                        span.set_status("success")
                        return result

                    except Exception as e:
                        span.set_status("error")
                        span.set_error(str(e))
                        raise

            return wrapper

        # Handle @client.trace vs @client.trace()
        if func is not None:
            return decorator(func)
        return decorator

    @contextmanager
    def span(
        self,
        name: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Context manager for creating a traced span.

        Usage:
            with client.span("operation_name") as span:
                span.set_attribute("key", "value")
                result = do_something()
        """
        span = Span(
            name=name,
            agent_id=self.agent_id,
            tags=tags or [],
            metadata=metadata or {},
        )

        try:
            yield span
        except Exception as e:
            span.set_status("error")
            span.set_error(str(e))
            raise
        finally:
            span.end()
            self._send_trace(span)

    def _send_trace(self, span: Span):
        """Send a completed span as a trace."""
        try:
            trace_data = {
                "agent_id": span.agent_id,
                "input_data": span.input_data,
                "output_data": span.output_data,
                "status": span.status,
                "error_message": span.error,
                "total_duration_ms": span.duration_ms,
                "trace_data": span.trace_data,
                "metadata": span.metadata,
                "tags": span.tags,
            }
            self._request("POST", "/api/v1/traces", data=trace_data)
            logger.debug(f"Trace sent: {span.name}")
        except Exception as e:
            logger.error(f"Failed to send trace: {e}")

    # ==================
    # Agent Methods
    # ==================

    def list_agents(self) -> List[Agent]:
        """List all agents."""
        data = self._request("GET", "/api/v1/agents")
        return [Agent(**agent) for agent in data]

    def get_agent(self, agent_id: str) -> Agent:
        """Get a specific agent."""
        data = self._request("GET", f"/api/v1/agents/{agent_id}")
        return Agent(**data)

    def create_agent(
        self,
        name: str,
        description: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        """Create a new agent."""
        data = self._request("POST", "/api/v1/agents", data={
            "name": name,
            "description": description,
            "endpoint_url": endpoint_url,
            "metadata": metadata or {},
        })
        return Agent(**data)

    # ==================
    # Trace Methods
    # ==================

    def list_traces(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Trace]:
        """List traces with optional filters."""
        params = {"limit": limit, "offset": offset}
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status

        data = self._request("GET", "/api/v1/traces", params=params)
        
        # Handle different response formats
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("items", data.get("traces", []))
        else:
            items = []
            
        # Parse each trace, handling different formats
        traces = []
        for trace in items:
            if isinstance(trace, dict):
                traces.append(Trace(**trace))
            elif isinstance(trace, str):
                # Some APIs return trace IDs only
                continue
        return traces

    def get_trace(self, trace_id: str) -> Trace:
        """Get a specific trace."""
        data = self._request("GET", f"/api/v1/traces/{trace_id}")
        return Trace(**data)

    def create_trace(
        self,
        input_data: Any,
        output_data: Any = None,
        status: str = "success",
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        trace_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> Trace:
        """Create a trace manually."""
        data = self._request("POST", "/api/v1/traces", data={
            "agent_id": self.agent_id,
            "input_data": input_data,
            "output_data": output_data,
            "status": status,
            "error_message": error_message,
            "total_duration_ms": duration_ms,
            "trace_data": trace_data or {},
            "metadata": metadata or {},
            "tags": tags or [],
        })
        return Trace(**data)

    # ==================
    # Test Methods
    # ==================

    def create_test(
        self,
        name: str,
        input_data: str,
        expected_output: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a test case."""
        return self._request("POST", "/api/v1/tests", data={
            "name": name,
            "agent_id": agent_id or self.agent_id,
            "test_input": input_data,
            "expected_output": expected_output,
        })

    def run_test(self, test_id: str) -> Dict[str, Any]:
        """Run a test."""
        return self._request("POST", f"/api/v1/tests/{test_id}/run")

    # ==================
    # Health Check Methods
    # ==================

    def create_health_check(
        self,
        agent_id: Optional[str] = None,
        check_type: str = "http",
        endpoint: Optional[str] = None,
        interval_seconds: int = 300,
        timeout_seconds: int = 30,
    ) -> Dict[str, Any]:
        """Create a health check."""
        return self._request("POST", "/api/v1/health-checks", data={
            "agent_id": agent_id or self.agent_id,
            "check_type": check_type,
            "endpoint": endpoint,
            "interval_seconds": interval_seconds,
            "timeout_seconds": timeout_seconds,
        })

    # ==================
    # Utility Methods
    # ==================

    def close(self):
        """Close the client and release resources."""
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
