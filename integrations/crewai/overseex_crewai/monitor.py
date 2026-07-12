"""
OverseeX CrewAI Monitor

Core monitoring functionality for CrewAI workflows.
Captures agent handoffs, task execution, tool calls, and coordination patterns.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from contextlib import contextmanager
import time
import logging
import json
import os
import requests
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("overseex.crewai")


class HandoffStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    crewai_id: str
    overseex_id: Optional[str]
    role: str
    goal: str
    backstory: Optional[str]
    allow_delegation: bool
    tools: List[str]


@dataclass
class Handoff:
    """Represents a handoff between two agents."""
    from_agent: str
    to_agent: str
    task_type: str
    started_at: float
    completed_at: Optional[float] = None
    status: HandoffStatus = HandoffStatus.PENDING
    sender_state: Optional[Dict] = None
    receiver_state: Optional[Dict] = None
    error_message: Optional[str] = None


@dataclass
class TraceData:
    """Data collected during task execution."""
    agent_id: str
    agent_role: str
    task_description: str
    started_at: float
    completed_at: Optional[float] = None
    status: str = "pending"
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)
    tool_calls: List[Dict] = field(default_factory=list)
    coordination_events: List[Dict] = field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class OverseeXCrewAICallback:
    """
    Callback handler for CrewAI that captures execution traces.

    This is the core class that hooks into CrewAI's execution lifecycle.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        capture_tools: bool = True,
        capture_coordination: bool = True,
        capture_state: bool = True,
        auto_register_agents: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize OverseeX callback for CrewAI.

        Args:
            api_key: OverseeX API key (ag_live_* or ag_test_*)
            base_url: OverseeX API URL (defaults to https://api.overseex.com)
            capture_tools: Whether to capture tool calls
            capture_coordination: Whether to capture inter-agent coordination
            capture_state: Whether to capture agent state at handoffs
            auto_register_agents: Whether to auto-register agents in OverseeX
            verbose: Enable verbose logging
        """
        self.api_key = api_key
        self.base_url = base_url or os.getenv("OVERSEEX_API_URL", "https://api.overseex.com")
        self.capture_tools = capture_tools
        self.capture_coordination = capture_coordination
        self.capture_state = capture_state
        self.auto_register_agents = auto_register_agents
        self.verbose = verbose

        # Internal state
        self.agents: Dict[str, AgentInfo] = {}
        self.active_traces: Dict[str, TraceData] = {}
        self.handoffs: List[Handoff] = []
        self.crew_execution_id: Optional[str] = None

        if verbose:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make API request to OverseeX."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code in (200, 201):
                return response.json()
            else:
                logger.warning(f"API request failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    def _get_agent_key(self, agent) -> str:
        """Generate unique key for CrewAI agent."""
        return f"{agent.role}_{id(agent)}"

    def register_agent(self, agent) -> Optional[str]:
        """
        Register a CrewAI agent with OverseeX.

        Args:
            agent: CrewAI Agent instance

        Returns:
            OverseeX agent ID if successful, None otherwise
        """
        agent_key = self._get_agent_key(agent)

        if agent_key in self.agents:
            return self.agents[agent_key].overseex_id

        # Extract agent info
        agent_info = AgentInfo(
            crewai_id=agent_key,
            overseex_id=None,
            role=agent.role or "Unnamed Agent",
            goal=agent.goal or "",
            backstory=getattr(agent, 'backstory', None),
            allow_delegation=getattr(agent, 'allow_delegation', False),
            tools=[t.__class__.__name__ for t in getattr(agent, 'tools', []) or []],
        )

        if self.auto_register_agents:
            # Register with OverseeX API
            result = self._make_request("POST", "/api/v1/agents/", {
                "name": agent_info.role,
                "endpoint_url": f"crewai://{agent_key}",
            })

            if result:
                agent_info.overseex_id = result.get("id")
                logger.info(f"Registered agent: {agent_info.role} -> {agent_info.overseex_id}")

        self.agents[agent_key] = agent_info
        return agent_info.overseex_id

    def on_crew_start(self, crew):
        """Called when crew execution starts."""
        self.crew_execution_id = f"crew_{int(time.time())}_{id(crew)}"
        logger.info(f"Crew execution started: {self.crew_execution_id}")

        # Register all agents
        for agent in crew.agents:
            self.register_agent(agent)

    def on_task_start(self, task, agent, crew):
        """
        Called when a task starts execution.

        Args:
            task: CrewAI Task instance
            agent: Agent executing the task
            crew: Crew instance
        """
        agent_key = self._get_agent_key(agent)
        agent_info = self.agents.get(agent_key)

        if not agent_info:
            agent_info = AgentInfo(
                crewai_id=agent_key,
                overseex_id=None,
                role=agent.role,
                goal=agent.goal,
                backstory=None,
                allow_delegation=False,
                tools=[],
            )
            self.agents[agent_key] = agent_info

        trace_key = f"{agent_key}_{id(task)}"

        # Create trace data
        trace = TraceData(
            agent_id=agent_info.overseex_id or agent_key,
            agent_role=agent_info.role,
            task_description=task.description,
            started_at=time.time(),
            input_data={
                "task": task.description,
                "expected_output": getattr(task, 'expected_output', None),
                "context": [t.description for t in getattr(task, 'context', []) or []],
            },
            metadata={
                "crew_execution_id": self.crew_execution_id,
                "agent_role": agent_info.role,
                "agent_goal": agent_info.goal,
                "allow_delegation": agent_info.allow_delegation,
                "crew_size": len(crew.agents),
            }
        )

        self.active_traces[trace_key] = trace
        logger.debug(f"Task started: {agent_info.role} - {task.description[:50]}...")

    def on_tool_call(self, agent, tool_name: str, tool_input: Any, tool_output: Any):
        """
        Called when an agent uses a tool.

        Args:
            agent: Agent using the tool
            tool_name: Name of the tool
            tool_input: Input to the tool
            tool_output: Output from the tool
        """
        if not self.capture_tools:
            return

        agent_key = self._get_agent_key(agent)

        # Find active trace for this agent
        for trace_key, trace in self.active_traces.items():
            if trace_key.startswith(agent_key):
                trace.tool_calls.append({
                    "tool": tool_name,
                    "input": self._truncate(str(tool_input), 500),
                    "output": self._truncate(str(tool_output), 500),
                    "timestamp": time.time(),
                })
                break

    def on_agent_delegation(self, from_agent, to_agent, task_description: str, context: Dict = None):
        """
        Called when one agent delegates to another.

        This is key for handoff tracking in Phase 2 coordination analysis.

        Args:
            from_agent: Source agent
            to_agent: Target agent
            task_description: What's being delegated
            context: Optional context data
        """
        if not self.capture_coordination:
            return

        from_key = self._get_agent_key(from_agent)
        to_key = self._get_agent_key(to_agent)

        # Record handoff
        handoff = Handoff(
            from_agent=from_key,
            to_agent=to_key,
            task_type="delegation",
            started_at=time.time(),
            sender_state=context if self.capture_state else None,
        )
        self.handoffs.append(handoff)

        # Add coordination event to active trace
        for trace_key, trace in self.active_traces.items():
            if trace_key.startswith(from_key):
                trace.coordination_events.append({
                    "type": "delegation",
                    "from": from_agent.role,
                    "to": to_agent.role,
                    "task": self._truncate(task_description, 200),
                    "timestamp": time.time(),
                })
                break

        logger.info(f"Delegation: {from_agent.role} -> {to_agent.role}")

    def on_task_complete(self, task, agent, output, crew):
        """
        Called when a task completes successfully.

        Args:
            task: Completed task
            agent: Agent that completed the task
            output: Task output
            crew: Crew instance
        """
        agent_key = self._get_agent_key(agent)
        trace_key = f"{agent_key}_{id(task)}"

        if trace_key not in self.active_traces:
            return

        trace = self.active_traces[trace_key]
        trace.completed_at = time.time()
        trace.status = "success"
        trace.output_data = {
            "result": self._truncate(str(output), 1000),
            "completed": True,
        }

        # Calculate duration
        duration_ms = int((trace.completed_at - trace.started_at) * 1000)

        # Send trace to OverseeX
        self._send_trace(trace, duration_ms)

        # Clean up
        del self.active_traces[trace_key]

        # Mark related handoffs as completed
        for handoff in self.handoffs:
            if handoff.to_agent == agent_key and handoff.status == HandoffStatus.PENDING:
                handoff.completed_at = time.time()
                handoff.status = HandoffStatus.COMPLETED
                self._send_handoff(handoff)

    def on_task_error(self, task, agent, error: Exception, crew):
        """
        Called when a task fails.

        Args:
            task: Failed task
            agent: Agent that encountered the error
            error: The exception
            crew: Crew instance
        """
        agent_key = self._get_agent_key(agent)
        trace_key = f"{agent_key}_{id(task)}"

        if trace_key not in self.active_traces:
            return

        trace = self.active_traces[trace_key]
        trace.completed_at = time.time()
        trace.status = "error"
        trace.error_message = str(error)
        trace.output_data = {
            "error": str(error),
            "error_type": type(error).__name__,
        }

        duration_ms = int((trace.completed_at - trace.started_at) * 1000)

        # Send trace
        self._send_trace(trace, duration_ms)

        # Clean up
        del self.active_traces[trace_key]

        # Mark handoffs as failed
        for handoff in self.handoffs:
            if handoff.to_agent == agent_key and handoff.status == HandoffStatus.PENDING:
                handoff.completed_at = time.time()
                handoff.status = HandoffStatus.FAILED
                handoff.error_message = str(error)
                self._send_handoff(handoff)

        logger.error(f"Task error: {agent.role} - {error}")

    def on_crew_complete(self, crew, output):
        """Called when crew execution completes."""
        logger.info(f"Crew execution completed: {self.crew_execution_id}")

        # Flush any remaining traces
        for trace_key, trace in list(self.active_traces.items()):
            trace.completed_at = time.time()
            trace.status = "completed"
            duration_ms = int((trace.completed_at - trace.started_at) * 1000)
            self._send_trace(trace, duration_ms)

        self.active_traces.clear()

        # Trigger coordination analysis
        self._trigger_coordination_analysis()

    def _send_trace(self, trace: TraceData, duration_ms: int):
        """Send trace to OverseeX API."""
        agent_info = None
        for info in self.agents.values():
            if info.overseex_id == trace.agent_id or info.crewai_id == trace.agent_id:
                agent_info = info
                break

        if not agent_info or not agent_info.overseex_id:
            logger.warning(f"Cannot send trace: agent not registered")
            return

        trace_data = {
            "agent_id": agent_info.overseex_id,
            "trace_data": {
                "input": trace.input_data,
                "output": trace.output_data,
                "tool_calls": trace.tool_calls,
                "coordination": trace.coordination_events,
                "metadata": trace.metadata,
            },
            "status": trace.status,
            "total_duration_ms": duration_ms,
        }

        if trace.error_message:
            trace_data["trace_data"]["error"] = trace.error_message

        result = self._make_request("POST", "/api/v1/traces/", trace_data)

        if result:
            logger.info(f"Trace sent: {result.get('id', 'unknown')} ({trace.agent_role})")
        else:
            logger.warning(f"Failed to send trace for {trace.agent_role}")

    def _send_handoff(self, handoff: Handoff):
        """Send handoff data to OverseeX coordination API."""
        from_agent = self.agents.get(handoff.from_agent)
        to_agent = self.agents.get(handoff.to_agent)

        if not from_agent or not to_agent:
            return

        if not from_agent.overseex_id or not to_agent.overseex_id:
            return

        handoff_data = {
            "from_agent_id": from_agent.overseex_id,
            "to_agent_id": to_agent.overseex_id,
            "task_type": handoff.task_type,
            "status": handoff.status.value,
            "duration_ms": int((handoff.completed_at - handoff.started_at) * 1000) if handoff.completed_at else None,
            "sender_state": handoff.sender_state,
            "receiver_state": handoff.receiver_state,
            "error_message": handoff.error_message,
        }

        # Note: This endpoint is part of Phase 2
        self._make_request("POST", "/api/v1/coordination/handoffs/", handoff_data)

    def _trigger_coordination_analysis(self):
        """Trigger coordination analysis for the completed crew execution."""
        if not self.capture_coordination:
            return

        # Get agent IDs for analysis
        agent_ids = [
            info.overseex_id for info in self.agents.values()
            if info.overseex_id
        ]

        if not agent_ids:
            return

        # Trigger analysis
        self._make_request("POST", "/api/v1/coordination/analyze", {
            "agent_ids": agent_ids,
            "time_window_hours": 1,  # Analyze last hour
        })

        logger.info("Triggered coordination analysis")

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."


class CrewMonitor:
    """
    Context manager for monitoring CrewAI crews.

    Usage:
        with CrewMonitor(api_key="ag_live_...") as monitor:
            crew = Crew(agents=[...], tasks=[...])
            result = crew.kickoff()
    """

    def __init__(self, api_key: str, **kwargs):
        """Initialize crew monitor."""
        self.callback = OverseeXCrewAICallback(api_key, **kwargs)
        self._original_kickoff = None

    def __enter__(self):
        """Start monitoring."""
        from .hooks import install_hooks
        install_hooks(self.callback)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop monitoring."""
        from .hooks import uninstall_hooks
        uninstall_hooks()
        return False


def monitor_crew(crew, api_key: str, **kwargs):
    """
    Simple function to monitor a CrewAI crew.

    Args:
        crew: CrewAI Crew instance
        api_key: OverseeX API key
        **kwargs: Additional options for OverseeXCrewAICallback

    Returns:
        The callback instance (for accessing trace data)

    Usage:
        crew = Crew(agents=[...], tasks=[...])
        monitor = monitor_crew(crew, api_key="ag_live_...")
        result = crew.kickoff()
    """
    callback = OverseeXCrewAICallback(api_key, **kwargs)
    callback.on_crew_start(crew)

    # Install hooks for this specific crew
    from .hooks import install_crew_hooks
    install_crew_hooks(crew, callback)

    return callback
