"""
OverseeX Python SDK (formerly AgentGuard)

Official Python client for OverseeX - AI Agent Testing & Monitoring Platform

Features:
- Automatic framework instrumentation (OpenAI, Anthropic, LangChain, CrewAI)
- Zero-code trace capture with decorators
- Smart mocking for external APIs
- Test generation from production traces
"""

from .client import AgentGuard
from .trace import Trace, TraceStatus
from .agent import Agent
from .exceptions import AgentGuardError, AuthenticationError, RateLimitError

# Auto-instrumentation features
from .auto_instrument import (
    auto_trace,
    trace_block,
    instrument_framework,
    uninstrument_framework,
    get_instrumented_frameworks,
    FrameworkDetector,
)

# Convenience alias
OverseeX = AgentGuard

__version__ = "0.2.0"
__all__ = [
    # Core
    "AgentGuard",
    "OverseeX",  # Alias
    "Trace",
    "TraceStatus", 
    "Agent",
    
    # Exceptions
    "AgentGuardError",
    "AuthenticationError",
    "RateLimitError",
    
    # Auto-instrumentation
    "auto_trace",
    "trace_block",
    "instrument_framework",
    "uninstrument_framework",
    "get_instrumented_frameworks",
    "FrameworkDetector",
]
