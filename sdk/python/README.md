# OverseeX Python SDK

Official Python client for [OverseeX](https://overseex.com) - AI Agent Testing & Monitoring Platform.

## Installation

```bash
pip install overseex
```

## Quick Start

### Option 1: Auto-Instrumentation (Recommended)

```python
from overseex import OverseeX, instrument_framework

# Initialize client
client = OverseeX(api_key="ag_live_your_key_here")

# Auto-instrument ALL OpenAI/Anthropic calls - zero code changes needed!
instrument_framework(client, "auto")

# Now every AI call is traced automatically
import openai
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
# ✅ Trace automatically created!
```

### Option 2: Decorator-Based Tracing

```python
from overseex import OverseeX, auto_trace

client = OverseeX(api_key="ag_live_...")

@auto_trace(client, agent_name="CustomerSupport")
def handle_query(user_message):
    # Your AI logic here
    response = call_ai(user_message)
    return response

# Every call to handle_query() is now traced automatically
result = handle_query("What's your refund policy?")
```

### Option 3: Manual Tracing

```python
from overseex import OverseeX

client = OverseeX(api_key="ag_live_your_key_here")

# Create a trace manually
trace = client.trace(
    agent_id="agent-123",
    input_data={"query": "What is the weather?"},
    output_data={"response": "It's sunny!"},
    status="success",
    duration_ms=1250,
    token_count=45,
    cost=0.001
)

print(f"✅ Trace created: {trace.id}")
```

## Features

- 🤖 **Auto-Instrumentation** - Automatic tracing for OpenAI, Anthropic, LangChain, CrewAI
- 🎯 **Framework Detection** - Automatically detects which AI frameworks you're using
- 🧪 **Zero-Code Tracing** - Instrument entire applications with one line
- 🚀 **Decorators** - Simple `@auto_trace` for any function
- 📊 **Token & Cost Tracking** - Automatic token counting and cost calculation
- 🛡️ **Error Capture** - Exceptions are traced with full stack traces
- 💰 **Smart Mocking** - Generate mocks from real traces

## Supported Frameworks

| Framework | Auto-Instrument | Notes |
|-----------|----------------|-------|
| OpenAI | ✅ `instrument_framework(client, "openai")` | All chat/completion calls |
| Anthropic | ✅ `instrument_framework(client, "anthropic")` | Claude API calls |
| LangChain | ✅ Use `AgentGuardCallbackHandler` | All chains and agents |
| CrewAI | ✅ Use `AgentGuardObserver` | Multi-agent workflows |
| Custom | ✅ Use `@auto_trace` decorator | Any Python function |

## Usage Examples

### Auto-Instrument Everything

```python
from overseex import OverseeX, instrument_framework

client = OverseeX(api_key="ag_live_...")

# Detect and instrument ALL supported frameworks
instrumented = instrument_framework(client, "auto")
print(f"Instrumented: {instrumented}")  # ['openai', 'anthropic']

# Your existing code works unchanged!
import openai
response = openai.chat.completions.create(...)  # Automatically traced
```

### LangChain Integration

```python
from overseex import OverseeX
from overseex_langchain import AgentGuardCallbackHandler
from langchain.chains import LLMChain

client = OverseeX(api_key="ag_live_...")
handler = AgentGuardCallbackHandler(client=client, agent_name="LangChainBot")

chain = LLMChain(llm=..., callbacks=[handler])
result = chain.run("Hello!")  # Automatically traced with all LLM calls
```

### CrewAI Integration

```python
from overseex import OverseeX
from overseex_crewai import AgentGuardObserver
from crewai import Crew, Agent, Task

client = OverseeX(api_key="ag_live_...")
observer = AgentGuardObserver(client=client)

crew = Crew(agents=[...], tasks=[...])
observer.register_crew_agents(crew)
crew.kickoff()  # All agent interactions traced
```

### Context Manager (Recommended)

```python
from overseex import OverseeX

with OverseeX(api_key="ag_live_...") as client:
    # Create agent
    agent = client.create_agent(
        name="Customer Support Bot",
        endpoint_url="https://api.example.com/agent",
        description="Handles customer queries"
    )
    
    # Create trace
    trace = client.trace(
        agent_id=agent.id,
        input_data={"message": "Hello"},
        output_data={"reply": "Hi there!"},
        status="success"
    )
    
    # Get dashboard stats
    stats = client.get_dashboard_stats()
    print(f"Total traces: {stats['total_traces']}")
```

### Error Handling

```python
from overseex import OverseeX, AuthenticationError, RateLimitError

client = OverseeX(api_key="ag_live_...")

try:
    trace = client.trace(
        agent_id="agent-123",
        input_data={"query": "Test"},
        output_data={"result": "Success"}
    )
except AuthenticationError:
    print("❌ Invalid API key")
except RateLimitError as e:
    print(f"⚠️ Rate limit exceeded: {e}")
except Exception as e:
    print(f"Error: {e}")
```

### Filtering Traces

```python
# Get only successful traces for a specific agent
traces = ag.list_traces(
    agent_id="agent-123",
    status="success",
    limit=10
)

for trace in traces:
    print(f"{trace.id}: {trace.status} - {trace.duration_ms}ms")
```

### Analytics

```python
# Get dashboard statistics
stats = ag.get_dashboard_stats()
print(f"Total Traces: {stats['total_traces']}")
print(f"Success Rate: {stats['success_rate']}%")
print(f"Total Cost: ${stats['total_cost']}")

# Get timeline data
timeline = ag.get_traces_timeline(days=7)
for day in timeline:
    print(f"{day['date']}: {day['count']} traces")
```

## API Reference

### AgentGuard Client

#### `__init__(api_key, base_url="http://localhost:8000", timeout=30)`
Initialize the AgentGuard client.

**Parameters:**
- `api_key` (str): Your AgentGuard API key (required)
- `base_url` (str): API base URL (default: localhost for dev)
- `timeout` (int): Request timeout in seconds (default: 30)

#### `trace(...)`
Create a new trace for agent execution.

**Parameters:**
- `agent_id` (str): Agent ID (required)
- `input_data` (dict): Input data sent to agent (required)
- `output_data` (dict): Output data from agent
- `status` (str): Execution status (success, error, timeout)
- `error_message` (str): Error message if failed
- `metadata` (dict): Additional metadata
- `duration_ms` (int): Execution duration in milliseconds
- `token_count` (int): Number of tokens used
- `cost` (float): Execution cost in USD

**Returns:** `Trace` object

#### `create_agent(name, endpoint_url, description=None, config=None)`
Register a new agent.

**Returns:** `Agent` object

#### `list_agents()`
Get all registered agents.

**Returns:** List of `Agent` objects

#### `get_dashboard_stats()`
Get dashboard statistics.

**Returns:** Dictionary with metrics

## Models

### Trace
Represents an agent execution trace.

**Attributes:**
- `id` (str): Unique trace ID
- `agent_id` (str): Associated agent ID
- `input_data` (dict): Input data
- `output_data` (dict): Output data
- `status` (str): Execution status
- `error_message` (str): Error message (if any)
- `duration_ms` (int): Duration in milliseconds
- `token_count` (int): Tokens used
- `cost` (float): Execution cost
- `created_at` (datetime): Creation timestamp

**Methods:**
- `is_success()`: Returns True if status is "success"
- `is_error()`: Returns True if status is "error"

### Agent
Represents a registered AI agent.

**Attributes:**
- `id` (str): Unique agent ID
- `name` (str): Agent name
- `endpoint_url` (str): Agent API endpoint
- `description` (str): Agent description
- `config` (dict): Agent configuration
- `is_active` (bool): Whether agent is active
- `created_at` (datetime): Registration timestamp

## Exceptions

- `AgentGuardError`: Base exception
- `AuthenticationError`: Invalid API key
- `RateLimitError`: Rate limit exceeded
- `ValidationError`: Invalid request data
- `NetworkError`: Network request failed

## Configuration

### Environment Variables

```bash
export AGENTGUARD_API_KEY="ag_live_your_key"
export AGENTGUARD_BASE_URL="https://api.agentguard.io"
```

```python
import os
from agentguard import AgentGuard

ag = AgentGuard(
    api_key=os.getenv("AGENTGUARD_API_KEY"),
    base_url=os.getenv("AGENTGUARD_BASE_URL", "http://localhost:8000")
)
```

## Development

```bash
# Clone repository
git clone https://github.com/agentguard/python-sdk
cd python-sdk

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black agentguard/

# Type checking
mypy agentguard/
```

## Support

- 📧 Email: support@agentguard.io
- 📚 Documentation: https://docs.agentguard.io
- 💬 Discord: https://discord.gg/agentguard
- 🐛 Issues: https://github.com/agentguard/python-sdk/issues

## License

MIT License - see [LICENSE](LICENSE) file for details.
