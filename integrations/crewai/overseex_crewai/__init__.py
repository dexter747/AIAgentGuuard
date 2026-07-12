"""
OverseeX CrewAI Integration

Zero-config auto-instrumentation for CrewAI multi-agent workflows.

Install:
    pip install overseex-crewai

Usage:
    from overseex_crewai import monitor_crew
    from crewai import Crew, Agent, Task

    crew = Crew(agents=[...], tasks=[...])
    monitor_crew(crew, api_key="ag_live_...")  # Auto-capture all traces

    result = crew.kickoff()

Alternative context manager usage:
    from overseex_crewai import CrewMonitor

    with CrewMonitor(api_key="ag_live_...") as monitor:
        crew = Crew(agents=[...], tasks=[...])
        result = crew.kickoff()
"""

from .monitor import (
    CrewMonitor,
    monitor_crew,
    OverseeXCrewAICallback,
)
from .hooks import (
    install_hooks,
    uninstall_hooks,
)

__version__ = "0.1.0"
__all__ = [
    "CrewMonitor",
    "monitor_crew",
    "OverseeXCrewAICallback",
    "install_hooks",
    "uninstall_hooks",
]
