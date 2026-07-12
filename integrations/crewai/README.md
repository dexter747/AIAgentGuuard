# AgentGuard CrewAI Integration

Automatic trace capture for [CrewAI](https://www.crewai.com/) multi-agent workflows.

## Installation

```bash
pip install agentguard-crewai
```

## Quick Start

```python
from crewai import Crew, Agent, Task
from agentguard_crewai import AgentGuardObserver

# Define your agents
researcher = Agent(
    role="Researcher",
    goal="Research and analyze topics",
    backstory="Expert researcher with deep analysis skills"
)

writer = Agent(
    role="Writer",
    goal="Write engaging content",
    backstory="Creative writer with storytelling expertise"
)

# Define tasks
research_task = Task(
    description="Research AI trends in 2026",
    agent=researcher,
    expected_output="Detailed research report"
)

writing_task = Task(
    description="Write article based on research",
    agent=writer,
    context=[research_task],
    expected_output="Published article"
)

# Create crew with AgentGuard observer
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task]
)

observer = AgentGuardObserver(api_key="ag_live_your_key")
observer.register_crew_agents(crew)

# Run crew - traces automatically captured!
result = crew.kickoff()

# View traces in AgentGuard dashboard
print("✅ Execution complete! View traces at http://localhost:3000/dashboard")
```

## Features

- ✅ **Automatic agent registration** - Agents registered in AgentGuard on first use
- ✅ **Task execution tracking** - Capture every task execution with timing
- ✅ **Tool call monitoring** - Track all tool uses by agents
- ✅ **Multi-agent coordination** - Capture delegation and collaboration events
- ✅ **Error tracking** - Automatic error capture and reporting
- ✅ **State drift detection** - Monitor inter-agent state changes
- ✅ **PII redaction** - Sensitive data automatically redacted

## Advanced Usage

### Custom Configuration

```python
observer = AgentGuardObserver(
    api_key="ag_live_your_key",
    base_url="https://api.agentguard.io",  # Production API
    capture_tools=True,  # Capture tool calls
    capture_coordination=True,  # Capture agent coordination
    auto_register_agents=True  # Auto-register agents
)
```

### Manual Event Tracking

```python
# Track task start
observer.on_task_start(task, agent, crew)

# Track tool use
observer.on_tool_use(agent, tool, input_data, output_data)

# Track coordination
observer.on_agent_coordination(source_agent, target_agent, message, crew)

# Track completion
observer.on_task_complete(task, agent, output, crew)

# Track errors
observer.on_task_error(task, agent, error, crew)
```

### Monkey-Patching (Automatic)

For automatic tracing without manual observer setup:

```python
from agentguard_crewai import monkey_patch_crewai, AgentGuardObserver

# Patch CrewAI globally
observer = AgentGuardObserver(api_key="ag_live_...")
monkey_patch_crewai(observer)

# All Crew executions are now automatically traced
crew = Crew(agents=[...], tasks=[...])
crew.kickoff()  # Automatically traced!
```

## What Gets Captured

### Task Execution

```python
{
    "task": "Research AI trends",
    "expected_output": "Research report",
    "context": ["Previous task outputs"],
    "tools": ["WebSearchTool", "ScraperTool"],
    "duration_ms": 12500,
    "status": "success"
}
```

### Multi-Agent Coordination

```python
{
    "coordination": {
        "allow_delegation": True,
        "crew_size": 3,
        "agent_role": "Researcher",
        "events": [
            {
                "from": "Researcher",
                "to": "Writer",
                "message": "Here's the research data",
                "timestamp": 1737645123.45
            }
        ]
    }
}
```

### Tool Calls

```python
{
    "tool_calls": [
        {
            "tool": "WebSearchTool",
            "input": "AI trends 2026",
            "output": "Found 100 articles...",
            "timestamp": 1737645120.12
        }
    ]
}
```

## Dashboard Integration

View all captured traces in AgentGuard dashboard:

- **Timeline view** - See task execution sequence
- **Coordination graph** - Visualize agent interactions
- **Tool usage** - Track which tools are used most
- **Error analysis** - Identify failure patterns
- **Performance metrics** - Optimize slow tasks

## Support

- 📚 Docs: https://docs.agentguard.io/integrations/crewai
- 💬 Discord: https://discord.gg/agentguard
- 🐛 Issues: https://github.com/agentguard/crewai-integration/issues

## License

MIT
