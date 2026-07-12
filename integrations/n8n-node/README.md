# n8n-nodes-overseex

n8n community node for [OverseeX](https://overseex.com) - AI Agent Monitoring & Testing Platform.

## Installation

### Community Node (Recommended)

1. Go to **Settings > Community Nodes**
2. Click **Install a community node**
3. Enter: `n8n-nodes-overseex`
4. Click **Install**

### Manual Installation

```bash
npm install n8n-nodes-overseex
```

## Features

- **Create Agents** - Register AI agents for monitoring
- **Send Traces** - Record agent executions and outputs
- **Get Insights** - Retrieve agent performance data
- **Coordination Analysis** - Detect multi-agent coordination issues
- **ML Suggestions** - Get AI-powered fix suggestions

## Credentials

1. Get your API key from [OverseeX Dashboard](https://app.overseex.com/settings/api-keys)
2. In n8n, go to **Credentials > Add Credential**
3. Select **OverseeX API**
4. Enter your API key

## Operations

### Agent

| Operation | Description |
|-----------|-------------|
| Create | Create a new agent |
| Get | Get an agent by ID |
| List | List all agents |

### Trace

| Operation | Description |
|-----------|-------------|
| Create | Send a trace (agent execution record) |
| Get | Get a trace by ID |
| List | List traces with optional filters |

### Coordination

| Operation | Description |
|-----------|-------------|
| Analyze | Analyze traces for coordination issues |
| Get Issues | Get detected coordination issues |
| Get Suggestions | Get ML-powered fix suggestions |

## Example Workflows

### 1. Monitor OpenAI Calls

```
[HTTP Request: OpenAI] → [OverseeX: Create Trace]
```

### 2. Multi-Agent Pipeline with Analysis

```
[Agent 1] → [Agent 2] → [Agent 3] → [OverseeX: Analyze Coordination]
```

### 3. Webhook-triggered Trace Collection

```
[Webhook] → [OverseeX: Create Trace] → [Respond to Webhook]
```

## Resources

- [OverseeX Documentation](https://docs.overseex.com)
- [n8n Community](https://community.n8n.io)
- [Support](mailto:support@overseex.com)

## License

MIT
