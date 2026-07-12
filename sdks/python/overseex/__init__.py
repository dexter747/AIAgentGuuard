"""
OverseeX Python SDK

The complete testing & monitoring platform for AI agents.

Usage:
    from overseex import OverseeX

    # Initialize client
    client = OverseeX(api_key="ox_live_your_api_key")

    # Trace your agent
    @client.trace
    def my_agent(query: str) -> str:
        return llm.generate(query)

    # Or use the context manager
    with client.span("operation_name"):
        # Your code here
        pass

    # Access coordination intelligence
    issues = client.coordination.list_issues()
    suggestions = client.coordination.list_suggestions()
"""

from .client import OverseeX
from .tracing import Span, trace
from .coordination import CoordinationClient
from .models import (
    Agent,
    Trace,
    CoordinationIssue,
    CorrectiveSuggestion,
    LearnedPattern,
    AgentHandoff,
)

__version__ = "0.2.4"

__all__ = [
    "OverseeX",
    "Span",
    "trace",
    "CoordinationClient",
    "Agent",
    "Trace",
    "CoordinationIssue",
    "CorrectiveSuggestion",
    "LearnedPattern",
    "AgentHandoff",
]
