# OverseeX AutoGen Integration

Auto-instrumentation for Microsoft AutoGen multi-agent conversations.

## Installation

```bash
pip install overseex-autogen
```

## Quick Start

```python
from autogen import AssistantAgent, UserProxyAgent
from overseex_autogen import monitor_autogen

# Create your AutoGen agents
assistant = AssistantAgent("assistant", llm_config=llm_config)
user_proxy = UserProxyAgent("user_proxy")

# Monitor the conversation
with monitor_autogen(api_key="ag_live_...", agents=[assistant, user_proxy]) as monitor:
    user_proxy.initiate_chat(assistant, message="What is the capital of France?")

# All interactions are automatically traced to OverseeX!
```

## Features

- **Zero-config Auto-instrumentation**: Just wrap your code and traces are captured
- **Multi-turn Conversation Tracking**: Every message between agents is recorded
- **Function Call Monitoring**: Track all function/tool executions
- **Agent Role Analysis**: Monitor agent behaviors and coordination
- **Coordination Intelligence**: Detect handoff patterns and issues

## Usage

### Context Manager

```python
from overseex_autogen import AutoGenMonitor

with AutoGenMonitor(api_key="your-api-key") as monitor:
    # Start tracking
    monitor.start_chat([assistant, user_proxy])

    # Your AutoGen code
    result = user_proxy.initiate_chat(assistant, message="Hello!")

    # End tracking
    monitor.end_chat()
```

### Manual Callback

```python
from overseex_autogen import OverseeXAutoGenCallback

callback = OverseeXAutoGenCallback(
    api_key="your-api-key",
    capture_functions=True,
    capture_messages=True,
    verbose=True
)

# Register agents
callback.register_agent(assistant)
callback.register_agent(user_proxy)

# Start conversation tracking
callback.start_conversation([assistant, user_proxy])

# ... run your AutoGen code ...

# End and send traces
callback.end_conversation()
```

## What Gets Captured

- **Messages**: All inter-agent communication
- **Function Calls**: Tool usage with inputs/outputs
- **Agent Roles**: AssistantAgent, UserProxyAgent, GroupChat, etc.
- **Conversation Flow**: Turn-by-turn execution
- **Token Usage**: LLM token consumption
- **Coordination Events**: Handoffs between agents

## Configuration

```python
OverseeXAutoGenCallback(
    api_key="your-api-key",           # Required
    base_url="https://api.overseex.com",  # Optional
    capture_functions=True,           # Capture function calls
    capture_messages=True,            # Capture message content
    capture_system_prompts=False,     # Capture system prompts (may contain sensitive data)
    auto_register_agents=True,        # Auto-register agents in OverseeX
    max_message_length=2000,          # Truncate long messages
    verbose=False,                    # Enable debug logging
)
```

## License

MIT
