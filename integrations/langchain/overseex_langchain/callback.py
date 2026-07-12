"""
OverseeX LangChain Callback Handler

Enhanced callback handler for LangChain with multi-agent handoff tracking.
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass, field
import time
import logging
import requests
import json

logger = logging.getLogger("overseex.langchain.callback")

# Try importing LangChain components
try:
    from langchain.callbacks.base import BaseCallbackHandler
    from langchain.schema import AgentAction, AgentFinish, LLMResult
    from langchain.schema.document import Document
except ImportError:
    try:
        from langchain_core.callbacks import BaseCallbackHandler
        from langchain_core.agents import AgentAction, AgentFinish
        from langchain_core.outputs import LLMResult
        from langchain_core.documents import Document
    except ImportError:
        raise ImportError(
            "LangChain is not installed. Install with: pip install langchain-core"
        )


@dataclass
class AgentInfo:
    """Information about an agent in a multi-agent system."""
    id: str
    name: str
    role: Optional[str] = None
    tools: List[str] = field(default_factory=list)


@dataclass
class Handoff:
    """Represents a handoff between agents."""
    from_agent: str
    to_agent: str
    timestamp: float
    context: Dict[str, Any] = field(default_factory=dict)
    reason: Optional[str] = None


@dataclass
class TraceData:
    """Accumulated trace data for a chain execution."""
    trace_id: str
    start_time: float
    agents: List[AgentInfo] = field(default_factory=list)
    handoffs: List[Handoff] = field(default_factory=list)
    llm_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    retrieval_queries: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    current_agent: Optional[str] = None
    total_tokens: int = 0
    total_cost: float = 0.0


class OverseeXCallbackHandler(BaseCallbackHandler):
    """
    LangChain callback handler with multi-agent coordination tracking.

    Features:
    - LLM call tracing with token counting
    - Tool execution tracking
    - Agent handoff detection
    - Retrieval/RAG monitoring
    - Error capture and reporting
    - Multi-agent flow visualization

    Usage:
        from overseex_langchain import OverseeXCallbackHandler

        handler = OverseeXCallbackHandler(
            api_key="ox_live_your_key",
            agent_name="my-langchain-agent"
        )

        chain = LLMChain(llm=llm, callbacks=[handler])
        result = chain.run("Hello world")
    """

    def __init__(
        self,
        api_key: str,
        agent_id: Optional[str] = None,
        agent_name: str = "LangChain Agent",
        base_url: str = "https://api.overseex.com",
        capture_llm_calls: bool = True,
        capture_tool_calls: bool = True,
        capture_retrieval: bool = True,
        capture_handoffs: bool = True,
        auto_register_agent: bool = True,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize OverseeX callback handler.

        Args:
            api_key: OverseeX API key
            agent_id: Existing agent ID (optional)
            agent_name: Name for auto-registered agent
            base_url: OverseeX API base URL
            capture_llm_calls: Capture LLM requests/responses
            capture_tool_calls: Capture tool executions
            capture_retrieval: Capture retrieval/RAG queries
            capture_handoffs: Detect and track agent handoffs
            auto_register_agent: Auto-register agent if agent_id not provided
            tags: Tags for traces
            metadata: Additional metadata for traces
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.agent_name = agent_name
        self.capture_llm_calls = capture_llm_calls
        self.capture_tool_calls = capture_tool_calls
        self.capture_retrieval = capture_retrieval
        self.capture_handoffs = capture_handoffs
        self.tags = tags or []
        self.extra_metadata = metadata or {}

        # Session for HTTP requests
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

        # Auto-register or use provided agent ID
        if agent_id:
            self.agent_id = agent_id
        elif auto_register_agent:
            self.agent_id = self._register_agent(agent_name)
        else:
            self.agent_id = "langchain-default"

        # Active runs and traces
        self.runs: Dict[UUID, Dict[str, Any]] = {}
        self.active_trace: Optional[TraceData] = None
        self._run_to_trace: Dict[UUID, str] = {}

        # Multi-agent tracking
        self._known_agents: Dict[str, AgentInfo] = {}

    def _register_agent(self, name: str) -> str:
        """Register agent with OverseeX and return agent ID."""
        try:
            response = self._session.post(
                f"{self.base_url}/api/v1/agents",
                json={
                    "name": name,
                    "endpoint_url": "langchain://local",
                    "description": "LangChain agent with OverseeX tracing",
                    "metadata": {"framework": "langchain"},
                }
            )
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Registered agent: {name} ({data['id']})")
                return data["id"]
            else:
                logger.warning(f"Failed to register agent: {response.text}")
                return "langchain-default"
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return "langchain-default"

    def _create_trace(self) -> TraceData:
        """Create a new trace data container."""
        import uuid
        return TraceData(
            trace_id=str(uuid.uuid4()),
            start_time=time.time(),
        )

    def _send_trace(self, trace: TraceData, outputs: Dict[str, Any], status: str = "success", error: Optional[str] = None):
        """Send trace data to OverseeX."""
        duration_ms = int((time.time() - trace.start_time) * 1000)

        # Build agent flow from handoffs
        agent_flow = []
        if trace.handoffs:
            agent_flow.append(trace.handoffs[0].from_agent)
            for handoff in trace.handoffs:
                agent_flow.append(handoff.to_agent)
        elif trace.current_agent:
            agent_flow = [trace.current_agent]

        trace_payload = {
            "agent_id": self.agent_id,
            "input_data": self.runs.get(list(self.runs.keys())[0] if self.runs else None, {}).get("inputs", {}),
            "output_data": outputs,
            "status": status,
            "error_message": error,
            "total_duration_ms": duration_ms,
            "token_count": trace.total_tokens,
            "cost": trace.total_cost,
            "trace_data": {
                "llm_calls": trace.llm_calls,
                "tool_calls": trace.tool_calls,
                "retrieval_queries": trace.retrieval_queries,
                "agent_flow": agent_flow,
                "handoffs": [
                    {
                        "from_agent": h.from_agent,
                        "to_agent": h.to_agent,
                        "timestamp": h.timestamp,
                        "context": h.context,
                        "reason": h.reason,
                    }
                    for h in trace.handoffs
                ],
                "agents": [
                    {
                        "id": a.id,
                        "name": a.name,
                        "role": a.role,
                        "tools": a.tools,
                    }
                    for a in trace.agents
                ],
            },
            "metadata": {
                **self.extra_metadata,
                "framework": "langchain",
                "errors": trace.errors,
            },
            "tags": self.tags,
        }

        try:
            response = self._session.post(
                f"{self.base_url}/api/v1/traces",
                json=trace_payload,
            )
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Trace sent: {data.get('id')}")
            else:
                logger.warning(f"Failed to send trace: {response.text}")
        except Exception as e:
            logger.error(f"Error sending trace: {e}")

    def _detect_handoff(self, new_agent: str):
        """Detect and record agent handoff."""
        if not self.capture_handoffs or not self.active_trace:
            return

        if self.active_trace.current_agent and self.active_trace.current_agent != new_agent:
            handoff = Handoff(
                from_agent=self.active_trace.current_agent,
                to_agent=new_agent,
                timestamp=time.time(),
            )
            self.active_trace.handoffs.append(handoff)
            logger.debug(f"Detected handoff: {handoff.from_agent} -> {handoff.to_agent}")

        self.active_trace.current_agent = new_agent

    def register_agent(self, agent_id: str, name: str, role: Optional[str] = None, tools: Optional[List[str]] = None):
        """
        Register an agent in the multi-agent system.

        Call this to provide metadata about agents in your system for
        better handoff tracking and visualization.

        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable agent name
            role: Agent's role (e.g., "researcher", "writer", "reviewer")
            tools: List of tool names available to this agent
        """
        agent_info = AgentInfo(
            id=agent_id,
            name=name,
            role=role,
            tools=tools or [],
        )
        self._known_agents[agent_id] = agent_info

        if self.active_trace:
            self.active_trace.agents.append(agent_info)

    def record_handoff(self, from_agent: str, to_agent: str, reason: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Manually record an agent handoff.

        Use this when you want to explicitly track handoffs in custom
        multi-agent orchestration code.

        Args:
            from_agent: ID of the agent handing off
            to_agent: ID of the agent receiving control
            reason: Why the handoff occurred
            context: Additional context for the handoff
        """
        if not self.active_trace:
            self.active_trace = self._create_trace()

        handoff = Handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            timestamp=time.time(),
            reason=reason,
            context=context or {},
        )
        self.active_trace.handoffs.append(handoff)
        self.active_trace.current_agent = to_agent

    # ===================
    # LLM Callbacks
    # ===================

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        """Called when LLM starts running."""
        if not self.capture_llm_calls:
            return

        run_id = kwargs.get("run_id")
        if run_id is None:
            return

        # Ensure we have an active trace
        if not self.active_trace:
            self.active_trace = self._create_trace()

        self.runs[run_id] = {
            "type": "llm",
            "prompts": prompts,
            "start_time": time.time(),
            "model": serialized.get("name", serialized.get("id", ["unknown"])[-1] if isinstance(serialized.get("id"), list) else "unknown"),
        }

    def on_llm_end(
        self,
        response: LLMResult,
        **kwargs: Any,
    ) -> None:
        """Called when LLM ends running."""
        if not self.capture_llm_calls:
            return

        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return

        run_data = self.runs[run_id]
        duration_ms = int((time.time() - run_data["start_time"]) * 1000)

        # Extract token counts
        llm_output = response.llm_output or {}
        token_usage = llm_output.get("token_usage", {})
        total_tokens = token_usage.get("total_tokens", 0)

        # Calculate cost estimate
        cost = self._estimate_cost(run_data["model"], total_tokens)

        # Extract generated text
        generations = []
        for gen_list in response.generations:
            for gen in gen_list:
                generations.append(gen.text if hasattr(gen, "text") else str(gen))

        llm_call = {
            "model": run_data["model"],
            "prompts": run_data["prompts"][:3],  # Limit to first 3 prompts
            "responses": generations[:3],  # Limit to first 3 responses
            "duration_ms": duration_ms,
            "token_count": total_tokens,
            "cost": cost,
            "timestamp": time.time(),
        }

        if self.active_trace:
            self.active_trace.llm_calls.append(llm_call)
            self.active_trace.total_tokens += total_tokens
            self.active_trace.total_cost += cost

        del self.runs[run_id]

    def on_llm_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any,
    ) -> None:
        """Called when LLM errors."""
        run_id = kwargs.get("run_id")

        error_data = {
            "type": "llm_error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": time.time(),
        }

        if self.active_trace:
            self.active_trace.errors.append(error_data)

        if run_id in self.runs:
            del self.runs[run_id]

    # ===================
    # Chain Callbacks
    # ===================

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Called when chain starts running."""
        run_id = kwargs.get("run_id")
        if run_id is None:
            return

        # Create new trace for top-level chain
        if not self.active_trace:
            self.active_trace = self._create_trace()

        chain_type = serialized.get("name", "unknown")

        self.runs[run_id] = {
            "type": "chain",
            "inputs": inputs,
            "start_time": time.time(),
            "chain_type": chain_type,
        }

        # Detect agent from chain type
        if "agent" in chain_type.lower():
            self._detect_handoff(chain_type)

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Called when chain ends running."""
        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return

        run_data = self.runs[run_id]

        # Only send trace for top-level chain
        parent_run_id = kwargs.get("parent_run_id")
        if parent_run_id is None and self.active_trace:
            self._send_trace(self.active_trace, outputs, status="success")
            self.active_trace = None

        del self.runs[run_id]

    def on_chain_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any,
    ) -> None:
        """Called when chain errors."""
        run_id = kwargs.get("run_id")

        error_data = {
            "type": "chain_error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": time.time(),
        }

        if self.active_trace:
            self.active_trace.errors.append(error_data)

        # Send error trace for top-level chain
        parent_run_id = kwargs.get("parent_run_id")
        if parent_run_id is None and self.active_trace:
            self._send_trace(self.active_trace, {}, status="error", error=str(error))
            self.active_trace = None

        if run_id in self.runs:
            del self.runs[run_id]

    # ===================
    # Tool Callbacks
    # ===================

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Called when tool starts running."""
        if not self.capture_tool_calls:
            return

        run_id = kwargs.get("run_id")
        if run_id is None:
            return

        self.runs[run_id] = {
            "type": "tool",
            "tool_name": serialized.get("name", "unknown"),
            "input": input_str,
            "start_time": time.time(),
        }

    def on_tool_end(
        self,
        output: str,
        **kwargs: Any,
    ) -> None:
        """Called when tool ends running."""
        if not self.capture_tool_calls:
            return

        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return

        run_data = self.runs[run_id]
        duration_ms = int((time.time() - run_data["start_time"]) * 1000)

        tool_call = {
            "tool": run_data["tool_name"],
            "input": run_data["input"][:500],
            "output": output[:500] if output else "",
            "duration_ms": duration_ms,
            "timestamp": time.time(),
        }

        if self.active_trace:
            self.active_trace.tool_calls.append(tool_call)

        del self.runs[run_id]

    def on_tool_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        **kwargs: Any,
    ) -> None:
        """Called when tool errors."""
        run_id = kwargs.get("run_id")

        error_data = {
            "type": "tool_error",
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": time.time(),
        }

        if self.active_trace:
            self.active_trace.errors.append(error_data)

        if run_id in self.runs:
            del self.runs[run_id]

    # ===================
    # Agent Callbacks
    # ===================

    def on_agent_action(
        self,
        action: AgentAction,
        **kwargs: Any,
    ) -> None:
        """Called when agent takes an action."""
        if self.capture_tool_calls and self.active_trace:
            self.active_trace.tool_calls.append({
                "tool": action.tool,
                "input": str(action.tool_input)[:500],
                "log": action.log[:500] if action.log else "",
                "timestamp": time.time(),
                "type": "agent_action",
            })

    def on_agent_finish(
        self,
        finish: AgentFinish,
        **kwargs: Any,
    ) -> None:
        """Called when agent finishes."""
        pass

    # ===================
    # Retrieval Callbacks
    # ===================

    def on_retriever_start(
        self,
        serialized: Dict[str, Any],
        query: str,
        **kwargs: Any,
    ) -> None:
        """Called when retriever starts."""
        if not self.capture_retrieval:
            return

        run_id = kwargs.get("run_id")
        if run_id is None:
            return

        self.runs[run_id] = {
            "type": "retrieval",
            "query": query,
            "start_time": time.time(),
        }

    def on_retriever_end(
        self,
        documents: List[Document],
        **kwargs: Any,
    ) -> None:
        """Called when retriever ends."""
        if not self.capture_retrieval:
            return

        run_id = kwargs.get("run_id")
        if run_id not in self.runs:
            return

        run_data = self.runs[run_id]
        duration_ms = int((time.time() - run_data["start_time"]) * 1000)

        retrieval_query = {
            "query": run_data["query"][:500],
            "num_documents": len(documents),
            "documents": [
                {
                    "content": doc.page_content[:200] if hasattr(doc, "page_content") else str(doc)[:200],
                    "metadata": doc.metadata if hasattr(doc, "metadata") else {},
                }
                for doc in documents[:3]
            ],
            "duration_ms": duration_ms,
            "timestamp": time.time(),
        }

        if self.active_trace:
            self.active_trace.retrieval_queries.append(retrieval_query)

        del self.runs[run_id]

    # ===================
    # Helpers
    # ===================

    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost based on model and tokens."""
        # Rough cost estimates per 1K tokens
        cost_per_1k = {
            "gpt-4": 0.06,
            "gpt-4-turbo": 0.03,
            "gpt-3.5-turbo": 0.002,
            "claude-3-opus": 0.075,
            "claude-3-sonnet": 0.015,
            "claude-3-haiku": 0.00125,
        }

        model_lower = model.lower()
        for model_name, cost in cost_per_1k.items():
            if model_name in model_lower:
                return (tokens / 1000) * cost

        # Default estimate
        return (tokens / 1000) * 0.01

    def close(self):
        """Close the callback handler and clean up resources."""
        if self.active_trace:
            self._send_trace(self.active_trace, {}, status="incomplete")
            self.active_trace = None
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
