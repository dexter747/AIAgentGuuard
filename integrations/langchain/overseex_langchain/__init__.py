"""
OverseeX LangChain Integration

Auto-instrumentation for LangChain and LangGraph applications.
Captures traces, agent handoffs, and tool executions automatically.
"""

from .callback import OverseeXCallbackHandler
from .hooks import install_hooks, uninstall_hooks
from .tracer import OverseeXTracer
from .graph import monitor_langgraph, LangGraphMonitor

__version__ = "0.1.0"

__all__ = [
    "OverseeXCallbackHandler",
    "OverseeXTracer",
    "install_hooks",
    "uninstall_hooks",
    "monitor_langgraph",
    "LangGraphMonitor",
]
