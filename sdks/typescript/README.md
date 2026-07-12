# OverseeX JavaScript/TypeScript SDK

The official JavaScript/TypeScript SDK for OverseeX - the complete monitoring and coordination intelligence platform for AI agents.

## Installation

```bash
npm install overseex
# or
yarn add overseex
# or
pnpm add overseex
```

## Quick Start

```typescript
import { OverseeX } from 'overseex';

// Initialize the client
const client = new OverseeX({
  apiKey: 'ox_live_your_api_key',
});

// Wrap any async function to automatically trace it
const tracedFunction = client.wrap(
  async (query: string) => {
    const result = await myLLM.generate(query);
    return result;
  },
  { name: 'my_agent' }
);

// Call the wrapped function
const result = await tracedFunction('Hello, world!');
```

## Features

### Function Wrapping

The easiest way to add tracing - wrap any async function:

```typescript
// Basic wrapping
const traced = client.wrap(myFunction);

// With options
const traced = client.wrap(myFunction, {
  name: 'custom_name',
  captureInput: true,
  captureOutput: true,
  tags: ['production', 'customer-service'],
});
```

### Manual Spans

For more control, create spans manually:

```typescript
const span = client.createSpan('complex_operation');

try {
  span.setInput({ query: 'user question' });

  // Record LLM calls
  span.recordLLMCall(
    'gpt-4',
    [{ role: 'user', content: 'Hello' }],
    { role: 'assistant', content: 'Hi there!' },
    { tokens: 150, latency: 500 }
  );

  // Record tool usage
  span.recordToolCall('search_web', { query: 'AI news' }, ['result1', 'result2']);

  // Record agent handoffs (for multi-agent systems)
  span.recordHandoff('agent-1', 'agent-2', { task: 'research' }, 'escalation');

  span.setOutput('Final response');
  span.setStatus('success');
} catch (error) {
  span.setError(error.message);
  span.setStatus('error');
} finally {
  await span.end(client);
}
```

### Multi-Agent Coordination Intelligence

Access coordination features to monitor multi-agent systems:

```typescript
// List coordination issues (state drift, handoff failures, etc.)
const issues = await client.coordination.listIssues({
  severity: 'high',
  status: 'open',
});

// Get corrective suggestions
const suggestions = await client.coordination.listSuggestions({
  minConfidence: 0.8,
});

// Approve a suggestion (trains the model)
await client.coordination.approveSuggestion(
  suggestionId,
  'This suggestion fixed our handoff issue'
);

// List learned patterns
const patterns = await client.coordination.listPatterns({
  issueType: 'state_drift',
  isActive: true,
});

// Get coordination metrics
const metrics = await client.coordination.getMetrics({
  days: 7,
});

// Analyze traces for issues
await client.coordination.analyzeTraces(
  ['trace-1', 'trace-2'],
  true // auto-create issues
);
```

### Agent Management

```typescript
// List all agents
const agents = await client.listAgents();

// Create an agent
const agent = await client.createAgent({
  name: 'Customer Support Bot',
  description: 'Handles customer inquiries',
  metadata: { department: 'support' },
});

// Get specific agent
const agent = await client.getAgent('agent-id');
```

### Trace Management

```typescript
// List traces
const traces = await client.listTraces({
  agentId: 'agent-123',
  status: 'error',
  limit: 100,
});

// Get specific trace
const trace = await client.getTrace('trace-id');

// Create a trace manually
const trace = await client.createTrace({
  inputData: { query: 'user question' },
  outputData: { response: 'answer' },
  status: 'success',
  durationMs: 1500,
  tags: ['production'],
});
```

## Coordination Issue Types

OverseeX detects the following coordination issues in multi-agent systems:

| Issue Type | Description |
|------------|-------------|
| `state_drift` | Agents have inconsistent state |
| `handoff_failure` | Failed agent-to-agent handoffs |
| `circular_delegation` | Agents delegating in loops |
| `lost_context` | Context lost during handoffs |
| `conflicting_actions` | Agents taking conflicting actions |
| `resource_contention` | Agents competing for resources |
| `broken_assumption` | Agent assumptions violated |

## Configuration

```typescript
const client = new OverseeX({
  // Required
  apiKey: 'ox_live_xxx',

  // Optional
  baseUrl: 'https://api.overseex.com',  // Custom API endpoint
  agentId: 'existing-agent-id',          // Use existing agent
  timeout: 30000,                        // Request timeout (ms)
  debug: true,                           // Enable debug logging
});
```

## TypeScript Support

Full TypeScript support with complete type definitions:

```typescript
import type {
  OverseeXConfig,
  Agent,
  Trace,
  CoordinationIssue,
  CorrectiveSuggestion,
  LearnedPattern,
  AgentHandoff,
  CoordinationMetrics,
} from 'overseex';
```

## Framework Integrations

### OpenAI

```typescript
import OpenAI from 'openai';
import { OverseeX } from 'overseex';

const client = new OverseeX({ apiKey: 'ox_live_xxx' });
const openai = new OpenAI();

const tracedChat = client.wrap(
  async (messages: OpenAI.Chat.ChatCompletionMessageParam[]) => {
    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages,
    });
    return response.choices[0].message;
  },
  { name: 'openai_chat' }
);
```

### Anthropic

```typescript
import Anthropic from '@anthropic-ai/sdk';
import { OverseeX } from 'overseex';

const client = new OverseeX({ apiKey: 'ox_live_xxx' });
const anthropic = new Anthropic();

const tracedMessage = client.wrap(
  async (prompt: string) => {
    const message = await anthropic.messages.create({
      model: 'claude-3-opus-20240229',
      max_tokens: 1024,
      messages: [{ role: 'user', content: prompt }],
    });
    return message;
  },
  { name: 'anthropic_chat' }
);
```

## Error Handling

```typescript
import { OverseeX } from 'overseex';

const client = new OverseeX({ apiKey: 'ox_live_xxx' });

try {
  const issues = await client.coordination.listIssues();
} catch (error) {
  if (error.response?.status === 401) {
    console.error('Invalid API key');
  } else if (error.response?.status === 429) {
    console.error('Rate limited');
  } else {
    console.error('API error:', error.message);
  }
}
```

## API Reference

### OverseeX Class

| Method | Description |
|--------|-------------|
| `wrap(fn, options?)` | Wrap a function with automatic tracing |
| `createSpan(name, options?)` | Create a manual span |
| `listAgents()` | List all agents |
| `getAgent(id)` | Get agent by ID |
| `createAgent(data)` | Create a new agent |
| `listTraces(params?)` | List traces with filters |
| `getTrace(id)` | Get trace by ID |
| `createTrace(data)` | Create a trace manually |
| `coordination` | Access coordination client |

### CoordinationClient Class

| Method | Description |
|--------|-------------|
| `listIssues(params?)` | List coordination issues |
| `getIssue(id)` | Get issue by ID |
| `resolveIssue(id, notes?)` | Mark issue as resolved |
| `ignoreIssue(id, reason?)` | Mark issue as ignored |
| `listSuggestions(params?)` | List corrective suggestions |
| `getSuggestion(id)` | Get suggestion by ID |
| `approveSuggestion(id, notes?, changes?)` | Approve suggestion |
| `rejectSuggestion(id, notes?)` | Reject suggestion |
| `listPatterns(params?)` | List learned patterns |
| `getPattern(id)` | Get pattern by ID |
| `deactivatePattern(id)` | Deactivate a pattern |
| `listHandoffs(params?)` | List agent handoffs |
| `getHandoffStats(params?)` | Get handoff statistics |
| `getMetrics(params?)` | Get coordination metrics |
| `analyzeTraces(ids, auto?)` | Analyze traces for issues |
| `getGraphData(params?)` | Get visualization data |

## License

MIT

## Support

- Documentation: https://overseex.com/docs
- Issues: https://github.com/overseex/overseex-js/issues
- Email: support@overseex.com
