# OverseeX Python SDK

The complete testing & monitoring platform for AI agents. OverseeX helps you trace, test, and debug multi-agent AI systems with confidence.

## Installation

```bash
pip install overseex

# With framework integrations
pip install overseex[crewai]      # For CrewAI support
pip install overseex[langchain]   # For LangChain support
pip install overseex[all]         # All integrations
```

## Quick Start

### Basic Tracing

```python
from overseex import OverseeX

# Initialize client
client = OverseeX(api_key="ox_live_your_api_key")

# Trace a function with decorator
@client.trace
def my_agent(query: str) -> str:
    # Your agent logic here
    return llm.generate(query)

# Run your agent - traces are automatically captured!
result = my_agent("What is the weather today?")
```

### Using Spans for Fine-Grained Tracing

```python
from overseex import OverseeX

client = OverseeX(api_key="ox_live_xxx")

def complex_agent(query: str):
    with client.span("research_phase") as span:
        span.set_attribute("query", query)
        research = do_research(query)
        span.record_tool_call("web_search", query, research)

    with client.span("synthesis_phase") as span:
        result = synthesize(research)
        span.record_llm_call(
            model="gpt-4",
            prompt=f"Synthesize: {research}",
            response=result,
            tokens=150
        )
        return result
```

### Recording Agent Handoffs

```python
with client.span("multi_agent_workflow") as span:
    # First agent processes
    research = researcher_agent.run(query)

    # Record handoff
    span.record_handoff(
        from_agent="researcher",
        to_agent="writer",
        reason="Research complete",
        context={"topics": research.topics}
    )

    # Second agent continues
    article = writer_agent.run(research)
```

## Coordination Intelligence

OverseeX automatically detects coordination issues in multi-agent systems:

```python
# Access coordination features
coordination = client.coordination

# List detected issues
issues = coordination.list_issues(
    severity="high",
    issue_type="state_drift"
)

for issue in issues:
    print(f"Issue: {issue.title}")
    print(f"Severity: {issue.severity}")
    print(f"Affected Agents: {issue.affected_agents}")

# Get corrective suggestions
suggestions = coordination.list_suggestions(min_confidence=0.8)

for suggestion in suggestions:
    print(f"Suggestion: {suggestion.title}")
    print(f"Confidence: {suggestion.confidence_score}")

    if suggestion.is_high_confidence:
        # Approve good suggestions to train the system
        coordination.approve_suggestion(
            suggestion.id,
            feedback_notes="Applied successfully"
        )

# View learned patterns
patterns = coordination.list_patterns()
for pattern in patterns:
    print(f"Pattern: {pattern.strategy}")
    print(f"Success Rate: {pattern.success_rate:.1%}")
```

### Coordination Metrics

```python
# Get coordination metrics
metrics = coordination.get_metrics(days=7)

print(f"Total Traces: {metrics.total_traces}")
print(f"Handoff Success Rate: {metrics.handoff_success_rate:.1%}")
print(f"Critical Issues: {metrics.critical_issues}")
print(f"Suggestion Approval Rate: {metrics.approval_rate:.1%}")
```

### Analyze Traces for Issues

```python
# Analyze specific traces
results = coordination.analyze_traces(
    trace_ids=["trace-id-1", "trace-id-2"],
    auto_create_issues=True
)

print(f"Detected {len(results['issues'])} issues")
```

## Framework Integrations

### CrewAI

```python
from crewai import Crew, Agent, Task
from overseex_crewai import monitor_crew

# Create your crew
crew = Crew(agents=[...], tasks=[...])

# Add monitoring - that's it!
callback = monitor_crew(crew, api_key="ox_live_xxx")

# Run crew - automatically traced with handoff detection
result = crew.kickoff()
```

### LangChain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from overseex_langchain import OverseeXCallbackHandler

# Create callback handler
handler = OverseeXCallbackHandler(api_key="ox_live_xxx")

# Use with any LangChain component
chain = prompt | llm | parser
result = chain.invoke(
    {"topic": "AI"},
    config={"callbacks": [handler]}
)
```

### LangGraph

```python
from langgraph.graph import StateGraph
from overseex_langchain import LangGraphMonitor

# Create monitor
monitor = LangGraphMonitor(api_key="ox_live_xxx")

# Wrap your compiled graph
app = graph.compile()
monitored_app = monitor.wrap_graph(app)

# Run - handoffs automatically tracked!
result = monitored_app.invoke({"messages": [...]})
```

## API Reference

### OverseeX Client

```python
client = OverseeX(
    api_key="ox_live_xxx",          # Required: Your API key
    base_url="https://api.overseex.com",  # Optional: API URL
    agent_id="agent-123",            # Optional: Use existing agent
    auto_register_agent=True,        # Optional: Auto-create agent
    agent_name="My Agent",           # Optional: Name for new agent
    timeout=30,                      # Optional: Request timeout
    debug=False,                     # Optional: Enable debug logging
)
```

### Tracing Methods

```python
# Decorator
@client.trace
@client.trace(name="custom_name", tags=["prod"])

# Context manager
with client.span("operation") as span:
    span.set_input(data)
    span.set_output(result)
    span.set_attribute("key", "value")
    span.record_llm_call(...)
    span.record_tool_call(...)
    span.record_handoff(...)
```

### Coordination Methods

```python
# Issues
client.coordination.list_issues(issue_type=..., severity=...)
client.coordination.get_issue(issue_id)
client.coordination.resolve_issue(issue_id)

# Suggestions
client.coordination.list_suggestions(min_confidence=0.8)
client.coordination.approve_suggestion(suggestion_id)
client.coordination.reject_suggestion(suggestion_id)

# Patterns
client.coordination.list_patterns()
client.coordination.deactivate_pattern(pattern_id)

# Handoffs
client.coordination.list_handoffs(trace_id=...)
client.coordination.get_handoff_stats(days=7)

# Metrics & Analysis
client.coordination.get_metrics(days=7)
client.coordination.analyze_traces(trace_ids=[...])
client.coordination.get_graph_data()
```

## Issue Types

OverseeX detects these coordination issues:

| Issue Type | Description |
|------------|-------------|
| `state_drift` | Agents have inconsistent state views |
| `handoff_failure` | Agent handoff failed or timed out |
| `broken_assumption` | Agent assumed data that doesn't exist |
| `duplicate_work` | Multiple agents did the same work |
| `circular_dependency` | Agents waiting on each other |

## Support

- Documentation: https://docs.overseex.com
- GitHub Issues: https://github.com/overseex/overseex-python/issues
- Email: support@overseex.com

## License

MIT
