"""
AgentGuard CrewAI Integration

Automatic trace capture for CrewAI multi-agent workflows.

Install:
    pip install agentguard-crewai

Usage:
    from agentguard_crewai import AgentGuardObserver
    from crewai import Crew, Agent, Task
    
    # Your agents and tasks
    agents = [...]
    tasks = [...]
    
    # Create crew with AgentGuard observer
    crew = Crew(agents=agents, tasks=tasks)
    observer = AgentGuardObserver(api_key="ag_live_your_key")
    crew.add_observer(observer)
    
    # Run crew - traces automatically captured!
    result = crew.kickoff()
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import sys

try:
    from crewai import Agent, Task, Crew
    from crewai.tools import BaseTool
except ImportError:
    raise ImportError(
        "CrewAI is not installed. Install it with: pip install crewai"
    )

try:
    from agentguard import AgentGuard
except ImportError:
    raise ImportError(
        "AgentGuard SDK is not installed. Install it with: pip install agentguard"
    )


class AgentGuardObserver:
    """
    CrewAI observer that automatically captures execution traces.
    
    Captures:
    - Agent interactions and coordination
    - Task executions and handoffs
    - Tool calls and results
    - Multi-agent state transitions
    - Errors and failures
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        capture_tools: bool = True,
        capture_coordination: bool = True,
        auto_register_agents: bool = True
    ):
        """
        Initialize AgentGuard observer for CrewAI.
        
        Args:
            api_key: AgentGuard API key
            base_url: AgentGuard API base URL
            capture_tools: Capture tool calls in traces
            capture_coordination: Capture inter-agent coordination
            auto_register_agents: Automatically register agents in AgentGuard
        """
        self.client = AgentGuard(api_key=api_key, base_url=base_url)
        self.capture_tools = capture_tools
        self.capture_coordination = capture_coordination
        self.auto_register_agents = auto_register_agents
        
        self.agent_registry: Dict[str, str] = {}  # CrewAI agent -> AgentGuard agent_id
        self.active_traces: Dict[str, Dict[str, Any]] = {}
        self.coordination_state: Dict[str, Any] = {}
    
    def register_crew_agents(self, crew: Crew):
        """
        Register all agents in a crew with AgentGuard.
        
        Args:
            crew: CrewAI Crew instance
        """
        if not self.auto_register_agents:
            return
        
        for agent in crew.agents:
            agent_key = self._get_agent_key(agent)
            if agent_key not in self.agent_registry:
                try:
                    ag_agent = self.client.create_agent(
                        name=agent.role or "Unnamed Agent",
                        endpoint_url=f"crewai://{agent_key}",
                        description=agent.goal or "",
                        config={
                            "role": agent.role,
                            "goal": agent.goal,
                            "backstory": agent.backstory,
                            "verbose": agent.verbose,
                            "allow_delegation": agent.allow_delegation,
                        }
                    )
                    self.agent_registry[agent_key] = ag_agent.id
                    print(f"✅ Registered agent: {agent.role} ({ag_agent.id})")
                except Exception as e:
                    print(f"⚠️ Failed to register agent {agent.role}: {e}")
    
    def _get_agent_key(self, agent: Agent) -> str:
        """Generate unique key for CrewAI agent."""
        return f"{agent.role}_{id(agent)}"
    
    def on_task_start(self, task: Task, agent: Agent, crew: Crew):
        """
        Called when a task starts execution.
        
        Args:
            task: Task being executed
            agent: Agent executing the task
            crew: Crew instance
        """
        agent_key = self._get_agent_key(agent)
        agent_id = self.agent_registry.get(agent_key)
        
        if not agent_id:
            return
        
        trace_key = f"{agent_key}_{id(task)}"
        self.active_traces[trace_key] = {
            "agent_id": agent_id,
            "agent_key": agent_key,
            "task_description": task.description,
            "start_time": time.time(),
            "input_data": {
                "task": task.description,
                "expected_output": task.expected_output,
                "context": [t.description for t in task.context] if task.context else [],
                "tools": [t.__class__.__name__ for t in (task.tools or [])] if self.capture_tools else [],
            },
            "coordination": {
                "allow_delegation": agent.allow_delegation,
                "crew_size": len(crew.agents),
                "agent_role": agent.role,
            } if self.capture_coordination else {},
            "tool_calls": [],
            "errors": []
        }
    
    def on_tool_use(self, agent: Agent, tool: BaseTool, tool_input: Any, tool_output: Any):
        """
        Called when an agent uses a tool.
        
        Args:
            agent: Agent using the tool
            tool: Tool being used
            tool_input: Input to the tool
            tool_output: Output from the tool
        """
        if not self.capture_tools:
            return
        
        agent_key = self._get_agent_key(agent)
        
        # Find active trace for this agent
        for trace_key, trace_data in self.active_traces.items():
            if trace_data["agent_key"] == agent_key:
                trace_data["tool_calls"].append({
                    "tool": tool.__class__.__name__,
                    "input": str(tool_input)[:500],  # Truncate long inputs
                    "output": str(tool_output)[:500],  # Truncate long outputs
                    "timestamp": time.time()
                })
                break
    
    def on_agent_coordination(
        self,
        source_agent: Agent,
        target_agent: Agent,
        message: str,
        crew: Crew
    ):
        """
        Called when agents coordinate (delegation, collaboration).
        
        Args:
            source_agent: Agent initiating coordination
            target_agent: Agent receiving coordination
            message: Coordination message
            crew: Crew instance
        """
        if not self.capture_coordination:
            return
        
        coordination_event = {
            "from": source_agent.role,
            "to": target_agent.role,
            "message": message[:500],
            "timestamp": time.time()
        }
        
        # Track coordination in global state
        if "events" not in self.coordination_state:
            self.coordination_state["events"] = []
        self.coordination_state["events"].append(coordination_event)
    
    def on_task_complete(
        self,
        task: Task,
        agent: Agent,
        output: Any,
        crew: Crew
    ):
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
        
        trace_data = self.active_traces[trace_key]
        duration_ms = int((time.time() - trace_data["start_time"]) * 1000)
        
        try:
            # Create trace in AgentGuard
            trace = self.client.trace(
                agent_id=trace_data["agent_id"],
                input_data=trace_data["input_data"],
                output_data={
                    "result": str(output)[:1000],  # Truncate long outputs
                    "task_completed": True,
                },
                status="success",
                metadata={
                    "tool_calls": trace_data["tool_calls"],
                    "coordination": trace_data["coordination"],
                    "crew_coordination_events": self.coordination_state.get("events", [])[-5:],  # Last 5 events
                },
                duration_ms=duration_ms
            )
            print(f"✅ Trace captured: {trace.id} ({agent.role})")
        except Exception as e:
            print(f"⚠️ Failed to create trace: {e}")
        finally:
            # Clean up
            del self.active_traces[trace_key]
    
    def on_task_error(
        self,
        task: Task,
        agent: Agent,
        error: Exception,
        crew: Crew
    ):
        """
        Called when a task fails with an error.
        
        Args:
            task: Failed task
            agent: Agent that encountered the error
            error: Exception that occurred
            crew: Crew instance
        """
        agent_key = self._get_agent_key(agent)
        trace_key = f"{agent_key}_{id(task)}"
        
        if trace_key not in self.active_traces:
            return
        
        trace_data = self.active_traces[trace_key]
        duration_ms = int((time.time() - trace_data["start_time"]) * 1000)
        
        try:
            # Create error trace
            trace = self.client.trace(
                agent_id=trace_data["agent_id"],
                input_data=trace_data["input_data"],
                output_data={},
                status="error",
                error_message=str(error),
                metadata={
                    "error_type": type(error).__name__,
                    "tool_calls": trace_data["tool_calls"],
                    "coordination": trace_data["coordination"],
                },
                duration_ms=duration_ms
            )
            print(f"❌ Error trace captured: {trace.id} ({agent.role})")
        except Exception as e:
            print(f"⚠️ Failed to create error trace: {e}")
        finally:
            # Clean up
            del self.active_traces[trace_key]
    
    def close(self):
        """Close the AgentGuard client."""
        self.client.close()


def monkey_patch_crewai(observer: AgentGuardObserver):
    """
    Monkey-patch CrewAI to automatically call observer methods.
    
    This is an alternative to manually adding observer to Crew.
    
    Usage:
        observer = AgentGuardObserver(api_key="...")
        monkey_patch_crewai(observer)
        
        # Now all Crew executions are automatically traced
        crew = Crew(agents=[...], tasks=[...])
        crew.kickoff()
    """
    original_kickoff = Crew.kickoff
    
    def traced_kickoff(self, *args, **kwargs):
        # Register agents
        observer.register_crew_agents(self)
        
        # TODO: Hook into task execution lifecycle
        # This requires deeper CrewAI integration
        
        # Call original method
        return original_kickoff(self, *args, **kwargs)
    
    Crew.kickoff = traced_kickoff


__all__ = ["AgentGuardObserver", "monkey_patch_crewai"]
