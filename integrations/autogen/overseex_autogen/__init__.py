"""
OverseeX AutoGen Integration

Auto-instrumentation for Microsoft AutoGen multi-agent conversations.
Captures agent interactions, function calls, and coordination patterns.
"""

from .monitor import (
    AutoGenMonitor,
    OverseeXAutoGenCallback,
    monitor_autogen,
)

__version__ = "0.1.0"
__all__ = [
    "AutoGenMonitor",
    "OverseeXAutoGenCallback",
    "monitor_autogen",
]
