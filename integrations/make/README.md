# OverseeX Make (Integromat) Integration

Integrate OverseeX with Make (formerly Integromat) to monitor AI agent workflows and automate observability.

## Setup

### 1. Get Your API Key

1. Log in to [OverseeX Dashboard](https://app.overseex.com)
2. Go to **Settings > API Keys**
3. Create or copy your API key (starts with `ag_live_` or `ag_test_`)

### 2. Add OverseeX to Make

OverseeX integrates via Make's HTTP module. No custom app installation needed.

## Quick Start: Send a Trace

1. Add an **HTTP > Make a request** module
2. Configure:

| Field | Value |
|-------|-------|
| URL | `https://api.overseex.com/api/v1/traces` |
| Method | POST |
| Headers | `Authorization: Bearer YOUR_API_KEY` |
| Headers | `Content-Type: application/json` |
| Body type | Raw |
| Content type | JSON (application/json) |

3. Body:
```json
{
  "agent_id": "{{your_agent_id}}",
  "input_data": {
    "prompt": "{{input_from_previous_module}}"
  },
  "output_data": {
    "response": "{{output_from_ai}}"
  },
  "status": "success",
  "total_duration_ms": {{duration}},
  "metadata": {
    "source": "make",
    "scenario": "{{scenario_name}}"
  },
  "tags": ["make", "automation"]
}
```

## API Endpoints

### Create Agent
```
POST https://api.overseex.com/api/v1/agents
```
```json
{
  "name": "My Make Agent",
  "description": "Agent managed by Make automation"
}
```

### List Agents
```
GET https://api.overseex.com/api/v1/agents
```

### Create Trace
```
POST https://api.overseex.com/api/v1/traces
```
```json
{
  "agent_id": "agent-uuid",
  "input_data": {"prompt": "user input"},
  "output_data": {"response": "ai response"},
  "status": "success",
  "total_duration_ms": 1500,
  "trace_data": {
    "llmCalls": [{
      "model": "gpt-4",
      "prompt": "...",
      "response": "...",
      "tokens": 150,
      "durationMs": 1200
    }],
    "toolCalls": [{
      "tool": "web_search",
      "input": "query",
      "output": "results"
    }]
  }
}
```

### List Traces
```
GET https://api.overseex.com/api/v1/traces?limit=50&agent_id=optional
```

### Analyze Coordination
```
POST https://api.overseex.com/api/v1/coordination/analyze
```
```json
{
  "trace_ids": ["trace-1", "trace-2"],
  "auto_create_issues": true
}
```

### Get Coordination Issues
```
GET https://api.overseex.com/api/v1/coordination/issues?limit=20
```

### Get ML Suggestions
```
GET https://api.overseex.com/api/v1/coordination/suggestions?status=pending
```

## Example Scenarios

### 1. Monitor OpenAI GPT Calls

```
[Webhook Trigger]
    ↓
[OpenAI - Create Chat Completion]
    ↓
[HTTP - Send to OverseeX]
    ↓
[Webhook Response]
```

**OverseeX HTTP Module Config:**
```json
{
  "agent_id": "gpt-assistant",
  "input_data": {
    "messages": "{{1.body.messages}}"
  },
  "output_data": {
    "response": "{{2.choices[0].message.content}}",
    "model": "{{2.model}}"
  },
  "status": "success",
  "total_duration_ms": "{{2.usage.total_tokens * 10}}",
  "metadata": {
    "tokens": "{{2.usage.total_tokens}}",
    "model": "{{2.model}}"
  }
}
```

### 2. Multi-Agent Workflow Monitoring

```
[Schedule Trigger]
    ↓
[Research Agent (Claude)]
    ↓
[HTTP - Trace Research]
    ↓
[Writer Agent (GPT-4)]
    ↓
[HTTP - Trace Writer]
    ↓
[HTTP - Analyze Coordination]
    ↓
[Slack - Send Results]
```

### 3. Error Alerting

```
[Webhook from AI App]
    ↓
[Router]
    ├── [status = error] → [HTTP - Send Error Trace] → [Email Alert]
    └── [status = success] → [HTTP - Send Success Trace]
```

## Webhooks (Receive from OverseeX)

OverseeX can send webhooks to Make when events occur.

### Setup Webhook Receiver

1. Add **Webhooks > Custom webhook** module
2. Copy the webhook URL
3. In OverseeX Dashboard, go to **Settings > Webhooks**
4. Add your Make webhook URL
5. Select events to receive

### Webhook Events

| Event | Description |
|-------|-------------|
| `trace.created` | New trace recorded |
| `trace.error` | Trace with error status |
| `issue.detected` | Coordination issue found |
| `suggestion.created` | New ML suggestion |

### Example: Alert on High-Severity Issues

```
[OverseeX Webhook]
    ↓
[Filter: severity = "high"]
    ↓
[Slack - Post Message]
```

## Best Practices

1. **Store API Key Securely**: Use Make's Data Store or connection system
2. **Handle Errors**: Add error handlers to HTTP modules
3. **Use Variables**: Store agent IDs in scenario variables
4. **Batch Traces**: For high-volume, batch multiple events before sending
5. **Set Timeouts**: Configure appropriate timeouts for HTTP requests

## Rate Limits

| Plan | Requests/min |
|------|-------------|
| Free | 30 |
| Starter | 60 |
| Pro | 300 |
| Team | 600 |

## Support

- [OverseeX Documentation](https://docs.overseex.com)
- [Make Community](https://community.make.com)
- [Email Support](mailto:support@overseex.com)
