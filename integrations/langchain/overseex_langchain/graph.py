"""
OverseeX LangGraph Integration

Support for LangGraph multi-agent workflows with automatic handoff tracking.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
import time
import logging
import functools
import requests

logger = logging.getLogger("overseex.langchain.graph")


@dataclass
class GraphNode:
    """Represents a node in a LangGraph."""
    name: str
    node_type: str = "agent"
    description: Optional[str] = None


@dataclass
class GraphEdge:
    """Represents an edge (transition) in a LangGraph."""
    source: str
    target: str
    condition: Optional[str] = None
    count: int = 0


@dataclass
class GraphExecution:
    """Tracks a single graph execution."""
    execution_id: str
    start_time: float
    nodes_visited: List[str] = field(default_factory=list)
    edges_traversed: List[GraphEdge] = field(default_factory=list)
    node_outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    current_node: Optional[str] = None


class LangGraphMonitor:
    """
    Monitor for LangGraph multi-agent workflows.

    Tracks node executions, edge transitions, and agent handoffs
    in LangGraph state machines.

    Usage:
        from overseex_langchain import LangGraphMonitor
        from langgraph.graph import StateGraph

        monitor = LangGraphMonitor(api_key="ox_live_xxx")

        # Create your graph
        graph = StateGraph(AgentState)
        graph.add_node("researcher", researcher_agent)
        graph.add_node("writer", writer_agent)
        graph.add_edge("researcher", "writer")

        # Compile with monitoring
        app = monitor.wrap_graph(graph.compile())

        # Run - automatically tracked!
        result = app.invoke({"messages": [...]})
    """

    def __init__(
        self,
        api_key: str,
        agent_id: Optional[str] = None,
        base_url: str = "https://api.overseex.com",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize LangGraph monitor.

        Args:
            api_key: OverseeX API key
            agent_id: Agent ID for traces
            base_url: OverseeX API base URL
            tags: Tags for traces
            metadata: Additional metadata
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.agent_id = agent_id or "langgraph-default"
        self.tags = tags or []
        self.extra_metadata = metadata or {}

        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

        # Graph structure
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}

        # Active executions
        self._active_execution: Optional[GraphExecution] = None

    def register_node(self, name: str, node_type: str = "agent", description: Optional[str] = None):
        """
        Register a node in the graph.

        Args:
            name: Node name
            node_type: Type of node (agent, tool, router, etc.)
            description: Description of what this node does
        """
        self._nodes[name] = GraphNode(
            name=name,
            node_type=node_type,
            description=description,
        )

    def register_edge(self, source: str, target: str, condition: Optional[str] = None):
        """
        Register an edge in the graph.

        Args:
            source: Source node name
            target: Target node name
            condition: Condition for this edge (for conditional edges)
        """
        key = f"{source}->{target}"
        self._edges[key] = GraphEdge(
            source=source,
            target=target,
            condition=condition,
        )

    def wrap_graph(self, compiled_graph):
        """
        Wrap a compiled LangGraph to add monitoring.

        Args:
            compiled_graph: A compiled LangGraph (result of graph.compile())

        Returns:
            Wrapped graph with monitoring
        """
        original_invoke = compiled_graph.invoke
        original_stream = getattr(compiled_graph, "stream", None)

        @functools.wraps(original_invoke)
        def monitored_invoke(input_data, config=None, **kwargs):
            import uuid
            self._start_execution(str(uuid.uuid4()), input_data)

            try:
                result = original_invoke(input_data, config=config, **kwargs)
                self._end_execution(result, status="success")
                return result
            except Exception as e:
                self._end_execution({}, status="error", error=str(e))
                raise

        compiled_graph.invoke = monitored_invoke

        if original_stream:
            @functools.wraps(original_stream)
            def monitored_stream(input_data, config=None, **kwargs):
                import uuid
                self._start_execution(str(uuid.uuid4()), input_data)

                try:
                    for chunk in original_stream(input_data, config=config, **kwargs):
                        # Track node transitions from stream
                        if isinstance(chunk, dict):
                            for node_name in chunk.keys():
                                self._record_node_visit(node_name, chunk.get(node_name))
                        yield chunk

                    self._end_execution({}, status="success")
                except Exception as e:
                    self._end_execution({}, status="error", error=str(e))
                    raise

            compiled_graph.stream = monitored_stream

        return compiled_graph

    def wrap_node(self, name: str, node_fn: Callable, node_type: str = "agent") -> Callable:
        """
        Wrap a node function to add monitoring.

        Args:
            name: Node name
            node_fn: The node function
            node_type: Type of node

        Returns:
            Wrapped node function
        """
        self.register_node(name, node_type)

        @functools.wraps(node_fn)
        def wrapped(state, *args, **kwargs):
            self._record_node_visit(name, state)

            try:
                result = node_fn(state, *args, **kwargs)
                self._record_node_output(name, result)
                return result
            except Exception as e:
                self._record_error(name, e)
                raise

        return wrapped

    def _start_execution(self, execution_id: str, input_data: Any):
        """Start tracking a graph execution."""
        self._active_execution = GraphExecution(
            execution_id=execution_id,
            start_time=time.time(),
        )
        logger.debug(f"Started graph execution: {execution_id}")

    def _end_execution(self, output_data: Any, status: str = "success", error: Optional[str] = None):
        """End tracking and send trace."""
        if not self._active_execution:
            return

        execution = self._active_execution
        duration_ms = int((time.time() - execution.start_time) * 1000)

        # Build agent flow from visited nodes
        agent_flow = execution.nodes_visited

        # Build handoffs from consecutive node visits
        handoffs = []
        for i in range(len(agent_flow) - 1):
            handoffs.append({
                "from_agent": agent_flow[i],
                "to_agent": agent_flow[i + 1],
                "timestamp": time.time(),
            })

        trace_payload = {
            "agent_id": self.agent_id,
            "input_data": {},  # Graph input is complex, summarize
            "output_data": output_data if isinstance(output_data, dict) else {},
            "status": status,
            "error_message": error,
            "total_duration_ms": duration_ms,
            "trace_data": {
                "graph_execution": True,
                "execution_id": execution.execution_id,
                "agent_flow": agent_flow,
                "handoffs": handoffs,
                "node_outputs": {
                    k: str(v)[:500] for k, v in execution.node_outputs.items()
                },
                "edges_traversed": [
                    {"source": e.source, "target": e.target, "count": e.count}
                    for e in execution.edges_traversed
                ],
                "errors": execution.errors,
            },
            "metadata": {
                **self.extra_metadata,
                "framework": "langgraph",
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
                logger.info(f"Graph trace sent: {data.get('id')}")
            else:
                logger.warning(f"Failed to send graph trace: {response.text}")
        except Exception as e:
            logger.error(f"Error sending graph trace: {e}")

        self._active_execution = None

    def _record_node_visit(self, node_name: str, state: Any):
        """Record a node visit during execution."""
        if not self._active_execution:
            return

        # Track handoff if there was a previous node
        if self._active_execution.current_node and self._active_execution.current_node != node_name:
            edge_key = f"{self._active_execution.current_node}->{node_name}"
            if edge_key in self._edges:
                self._edges[edge_key].count += 1
                self._active_execution.edges_traversed.append(self._edges[edge_key])

        self._active_execution.nodes_visited.append(node_name)
        self._active_execution.current_node = node_name

    def _record_node_output(self, node_name: str, output: Any):
        """Record a node's output."""
        if not self._active_execution:
            return

        self._active_execution.node_outputs[node_name] = output

    def _record_error(self, node_name: str, error: Exception):
        """Record an error in a node."""
        if not self._active_execution:
            return

        self._active_execution.errors.append({
            "node": node_name,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": time.time(),
        })

    def close(self):
        """Close the monitor and clean up resources."""
        self._session.close()


def monitor_langgraph(
    graph,
    api_key: str,
    agent_id: Optional[str] = None,
    **kwargs
):
    """
    Convenience function to wrap a LangGraph with monitoring.

    Args:
        graph: A compiled LangGraph
        api_key: OverseeX API key
        agent_id: Optional agent ID
        **kwargs: Additional arguments for LangGraphMonitor

    Returns:
        Wrapped graph with monitoring

    Example:
        from overseex_langchain import monitor_langgraph

        app = graph.compile()
        monitored_app = monitor_langgraph(app, api_key="ox_live_xxx")
        result = monitored_app.invoke({"messages": [...]})
    """
    monitor = LangGraphMonitor(api_key=api_key, agent_id=agent_id, **kwargs)
    return monitor.wrap_graph(graph)
