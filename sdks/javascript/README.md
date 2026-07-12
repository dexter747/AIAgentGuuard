# OverseeX JavaScript/TypeScript SDK

Official JavaScript/TypeScript SDK for [OverseeX](https://overseex.com) - AI Agent Testing & Monitoring Platform.

## Installation

```bash
npm install @overseex/sdk
# or
yarn add @overseex/sdk
```

## Quick Start

```typescript
import { OverseeX } from '@overseex/sdk';

// Initialize the SDK
const overseeX = new OverseeX({
  apiKey: 'your-api-key',
  agentId: 'your-agent-id',
});

// Start a trace
overseeX.startTrace({ query: 'What is the weather?' });

// Record tool calls
overseeX.recordToolCall('weather_api', { location: 'San Francisco' }, { temp: 72 });

// End the trace
await overseeX.endTrace({ response: 'The weather is 72°F' });
```

## Features

- **Automatic Trace Capture** - Record agent executions automatically
- **Tool Call Tracking** - Monitor all external API calls
- **Test Generation** - Generate pytest code from traces
- **Agent Insights** - Get behavioral analysis and recommendations
- **Error Monitoring** - Track failures and performance issues

## Usage

### Basic Tracing

```typescript
const overseeX = new OverseeX({
  apiKey: process.env.OVERSEEX_API_KEY!,
  agentId: 'agent-123',
});

// Manual tracing
overseeX.startTrace({ input: 'User query' });
// ... your agent logic ...
await overseeX.endTrace({ output: 'Agent response' });
```

### Automatic Function Tracing

```typescript
async function myAgentFunction(query: string) {
  // Your agent logic
  return result;
}

// Wrap function for automatic tracing
const tracedFunction = overseeX.traceFunction(myAgentFunction);

// Use as normal - traces automatically captured
const result = await tracedFunction('query');
```

### Recording Tool Calls

```typescript
overseeX.startTrace({ query: 'Send email' });

// Record tool usage
overseeX.recordToolCall(
  'sendgrid_send_email',
  { to: 'user@example.com', subject: 'Hello' },
  { message_id: 'msg_123', status: 'sent' }
);

await overseeX.endTrace({ status: 'success' });
```

### OpenAI Integration

```typescript
import OpenAI from 'openai';
import { OverseeX, traceOpenAI } from '@overseex/sdk';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const overseeX = new OverseeX({ apiKey: process.env.OVERSEEX_API_KEY, agentId: 'agent-123' });

// Wrap OpenAI for automatic tracing
const tracedOpenAI = traceOpenAI(overseeX, openai);

// Use as normal - calls are automatically traced
const completion = await tracedOpenAI.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Hello!' }],
});
```

### Test Generation

```typescript
// Generate test from a trace
const { generated_code } = await overseeX.generateTestFromTrace('trace-id');
console.log(generated_code); // pytest code

// Generate full test suite from recent traces
const { generated_code: suite } = await overseeX.generateTestSuite();
// Save to test_agent.py
```

### Insights & Monitoring

```typescript
// Get behavioral insights
const insights = await overseeX.getInsights();
insights.forEach(insight => {
  console.log(`${insight.type}: ${insight.message}`);
});

// Get traces
const traces = await overseeX.getTraces(50);
console.log(`Total traces: ${traces.length}`);
```

## Configuration

```typescript
interface OverseeXConfig {
  apiKey: string;          // Required: Your OverseeX API key
  agentId?: string;        // Optional: Default agent ID
  baseURL?: string;        // Optional: Custom API endpoint
  autoCapture?: boolean;   // Optional: Auto-capture mode (default: true)
}
```

## API Reference

### `OverseeX`

Main SDK class for interacting with OverseeX.

#### Methods

- `startTrace(input, metadata?)` - Start a new trace
- `endTrace(output, status?)` - End current trace and send to OverseeX
- `recordToolCall(toolName, input, output?, error?)` - Record a tool call
- `recordStep(type, data)` - Record an execution step
- `sendTrace(traceData)` - Send a complete trace
- `traceFunction(fn, name?)` - Wrap function for automatic tracing
- `getTraces(limit?, skip?)` - Get all traces
- `getTrace(traceId)` - Get specific trace
- `getAgent(agentId?)` - Get agent information
- `generateTestFromTrace(traceId, testName?)` - Generate test from trace
- `generateTestSuite(agentId?, limit?)` - Generate test suite
- `getInsights()` - Get agent insights

## Development

```bash
# Install dependencies
npm install

# Build
npm run build

# Test
npm test
```

## License

MIT

## Support

- Documentation: https://docs.overseex.com
- GitHub: https://github.com/overseex/sdk-javascript
- Email: support@overseex.com
