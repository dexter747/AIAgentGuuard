/**
 * Basic Tracing Example
 *
 * Shows how to use OverseeX for basic function tracing.
 */

import { OverseeX } from '../src';

async function main() {
  // Initialize the client
  const client = new OverseeX({
    apiKey: process.env.OVERSEEX_API_KEY || 'ox_test_xxx',
    debug: true,
  });

  // Example 1: Wrap a simple function
  const processQuery = client.wrap(
    async (query: string): Promise<string> => {
      // Simulate LLM processing
      await new Promise((resolve) => setTimeout(resolve, 100));
      return `Processed: ${query}`;
    },
    { name: 'process_query', tags: ['example'] }
  );

  const result = await processQuery('What is the weather today?');
  console.log('Result:', result);

  // Example 2: Manual span with more control
  const span = client.createSpan('complex_operation', {
    tags: ['manual', 'example'],
  });

  try {
    span.setInput({ task: 'analyze data' });

    // Simulate work
    await new Promise((resolve) => setTimeout(resolve, 50));

    // Record an LLM call
    span.recordLLMCall(
      'gpt-4',
      [{ role: 'user', content: 'Analyze this data' }],
      { role: 'assistant', content: 'Analysis complete' },
      { tokens: 150, latency: 500 }
    );

    // Record a tool call
    span.recordToolCall(
      'data_lookup',
      { id: '123' },
      { name: 'Test', value: 42 }
    );

    span.setOutput({ success: true, insights: ['insight1', 'insight2'] });
    span.setStatus('success');
  } catch (error: any) {
    span.setError(error.message);
    span.setStatus('error');
  } finally {
    await span.end(client);
  }

  console.log('Tracing complete!');
}

main().catch(console.error);
