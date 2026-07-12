"""
AgentGuard Client - Main SDK interface
"""

import requests
from typing import Optional, Dict, List, Any
from datetime import datetime

from .trace import Trace, TraceStatus
from .agent import Agent
from .exceptions import AgentGuardError, AuthenticationError, RateLimitError


class AgentGuard:
    """
    AgentGuard client for AI agent monitoring and testing.
    
    Usage:
        >>> from agentguard import AgentGuard
        >>> ag = AgentGuard(api_key="ag_live_your_key")
        >>> ag.trace(
        ...     agent_id="agent-123",
        ...     input_data={"query": "Hello"},
        ...     output_data={"response": "Hi there!"},
        ...     status="success"
        ... )
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.overseex.com",
        timeout: int = 30
    ):
        """
        Initialize AgentGuard client.
        
        Args:
            api_key: Your AgentGuard API key (ag_live_*)
            base_url: AgentGuard API base URL (default: localhost for dev)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to AgentGuard API."""
        url = f"{self.base_url}/v1{endpoint}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                raise RateLimitError(
                    f"Rate limit exceeded. Reset at: {response.headers.get('X-RateLimit-Reset')}"
                )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            
            # Handle other errors
            if response.status_code >= 400:
                error_detail = response.json().get("detail", "Unknown error")
                raise AgentGuardError(f"API error: {error_detail}")
            
            return response.json()
            
        except requests.RequestException as e:
            raise AgentGuardError(f"Network error: {str(e)}")
    
    def trace(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        token_count: Optional[int] = None,
        cost: Optional[float] = None
    ) -> Trace:
        """
        Create a trace for agent execution.
        
        Args:
            agent_id: ID of the agent that executed
            input_data: Input data sent to the agent
            output_data: Output data returned by agent
            status: Execution status (success, error, timeout)
            error_message: Error message if status is error
            metadata: Additional metadata (model, temperature, etc.)
            duration_ms: Execution duration in milliseconds
            token_count: Number of tokens used
            cost: Execution cost in USD
            
        Returns:
            Trace object with created trace data
        """
        # Build trace_data object as expected by API
        trace_data_obj = {
            "input": input_data,
            "output": output_data or {},
            "metadata": metadata or {},
        }
        if error_message:
            trace_data_obj["error"] = error_message
        
        # Build request payload matching API schema
        request_data = {
            "agent_id": agent_id,
            "trace_data": trace_data_obj,
            "status": status,
            "total_duration_ms": duration_ms,
            "token_count": token_count,
            "cost_usd": str(cost) if cost else None
        }
        
        result = self._request("POST", "/traces", data=request_data)
        return Trace.from_dict(result)
    
    def get_trace(self, trace_id: str) -> Trace:
        """Get a specific trace by ID."""
        result = self._request("GET", f"/traces/{trace_id}")
        return Trace.from_dict(result)
    
    def list_traces(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Trace]:
        """
        List traces with optional filtering.
        
        Args:
            agent_id: Filter by agent ID
            status: Filter by status (success, error, timeout)
            limit: Maximum number of traces to return
            offset: Number of traces to skip
            
        Returns:
            List of Trace objects
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        if agent_id:
            params["agent_id"] = agent_id
        if status:
            params["status"] = status
        
        response = self._request("GET", "/traces", params=params)
        # Handle paginated response format
        if isinstance(response, dict) and "traces" in response:
            results = response["traces"]
        elif isinstance(response, list):
            results = response
        else:
            results = []
        return [Trace.from_dict(t) for t in results]
    
    def create_agent(
        self,
        name: str,
        endpoint_url: str,
        description: Optional[str] = None,
        config: Optional[Dict] = None
    ) -> Agent:
        """
        Register a new agent.
        
        Args:
            name: Agent name
            endpoint_url: Agent API endpoint
            description: Agent description
            config: Agent configuration
            
        Returns:
            Agent object
        """
        agent_data = {
            "name": name,
            "endpoint_url": endpoint_url,
            "description": description,
            "config": config or {}
        }
        
        result = self._request("POST", "/agents", data=agent_data)
        return Agent.from_dict(result)
    
    def get_agent(self, agent_id: str) -> Agent:
        """Get agent by ID."""
        result = self._request("GET", f"/agents/{agent_id}")
        return Agent.from_dict(result)
    
    def list_agents(self) -> List[Agent]:
        """List all agents."""
        results = self._request("GET", "/agents")
        return [Agent.from_dict(a) for a in results]
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics."""
        return self._request("GET", "/analytics/dashboard/stats")
    
    def get_traces_timeline(self, days: int = 7) -> List[Dict]:
        """Get traces timeline for the last N days."""
        params = {"days": days}
        return self._request("GET", "/analytics/traces-timeline", params=params)
    
    def close(self):
        """Close the HTTP session."""
        self._session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
