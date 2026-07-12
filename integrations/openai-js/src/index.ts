/**
 * OverseeX OpenAI Integration
 *
 * Automatic tracing for OpenAI API calls with full observability.
 *
 * @example
 * ```typescript
 * import OpenAI from 'openai';
 * import { withOverseeX } from '@overseex/openai';
 *
 * const openai = withOverseeX(new OpenAI(), {
 *   apiKey: 'your-overseex-api-key',
 *   agentId: 'your-agent-id'
 * });
 *
 * // All calls are automatically traced
 * const response = await openai.chat.completions.create({
 *   model: 'gpt-4',
 *   messages: [{ role: 'user', content: 'Hello!' }]
 * });
 * ```
 */

import type OpenAI from 'openai';

export interface OverseeXConfig {
  apiKey: string;
  agentId?: string;
  baseUrl?: string;
  capturePrompts?: boolean;
  captureResponses?: boolean;
  captureFunctionCalls?: boolean;
  debug?: boolean;
}

interface TraceData {
  model: string;
  prompt?: string;
  response?: string;
  tokens?: {
    prompt: number;
    completion: number;
    total: number;
  };
  durationMs: number;
  functionCalls?: Array<{
    name: string;
    arguments: string;
  }>;
  error?: string;
}

class OverseeXOpenAITracer {
  private config: Required<OverseeXConfig>;
  private baseUrl: string;

  constructor(config: OverseeXConfig) {
    this.config = {
      apiKey: config.apiKey,
      agentId: config.agentId || 'openai-agent',
      baseUrl: config.baseUrl || 'https://api.overseex.com',
      capturePrompts: config.capturePrompts ?? true,
      captureResponses: config.captureResponses ?? true,
      captureFunctionCalls: config.captureFunctionCalls ?? true,
      debug: config.debug ?? false,
    };
    this.baseUrl = this.config.baseUrl.replace(/\/$/, '');
  }

  private log(...args: any[]) {
    if (this.config.debug) {
      console.log('[OverseeX]', ...args);
    }
  }

  async sendTrace(traceData: TraceData): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/traces`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: this.config.agentId,
          input_data: this.config.capturePrompts ? { prompt: traceData.prompt } : { redacted: true },
          output_data: this.config.captureResponses ? { response: traceData.response } : { redacted: true },
          trace_data: {
            llmCalls: [{
              model: traceData.model,
              prompt: this.config.capturePrompts ? traceData.prompt?.slice(0, 1000) : '[REDACTED]',
              response: this.config.captureResponses ? traceData.response?.slice(0, 1000) : '[REDACTED]',
              tokens: traceData.tokens?.total || 0,
              durationMs: traceData.durationMs,
              timestamp: Date.now(),
            }],
            toolCalls: traceData.functionCalls?.map(fc => ({
              tool: fc.name,
              input: this.config.captureFunctionCalls ? fc.arguments : '[REDACTED]',
              output: '',
              durationMs: 0,
              timestamp: Date.now(),
            })) || [],
          },
          status: traceData.error ? 'error' : 'success',
          error_message: traceData.error,
          total_duration_ms: traceData.durationMs,
          metadata: {
            model: traceData.model,
            tokens: traceData.tokens,
            framework: 'openai',
          },
          tags: ['openai', traceData.model],
        }),
      });

      if (!response.ok) {
        this.log('Failed to send trace:', response.status);
      } else {
        this.log('Trace sent successfully');
      }
    } catch (error) {
      this.log('Error sending trace:', error);
    }
  }

  wrapChatCompletions(original: OpenAI['chat']['completions']): any {
    const tracer = this;

    const wrappedCreate = async function(
      body: OpenAI.Chat.ChatCompletionCreateParams,
      options?: OpenAI.RequestOptions
    ): Promise<OpenAI.Chat.ChatCompletion | AsyncIterable<OpenAI.Chat.ChatCompletionChunk>> {
      const startTime = Date.now();
      const prompt = body.messages.map(m => `${m.role}: ${typeof m.content === 'string' ? m.content : JSON.stringify(m.content)}`).join('\n');

      try {
        // @ts-ignore - accessing original create method
        const result = await original.create.call(this, body, options);

        // Handle streaming responses
        if (body.stream) {
          // For streaming, we can't easily capture the full response
          // We'll send a partial trace
          tracer.sendTrace({
            model: body.model,
            prompt,
            response: '[STREAMING]',
            durationMs: Date.now() - startTime,
          });
          return result;
        }

        // Non-streaming response
        const completion = result as OpenAI.Chat.ChatCompletion;
        const responseText = completion.choices[0]?.message?.content || '';
        const functionCalls = completion.choices[0]?.message?.tool_calls?.map(tc => ({
          name: tc.function.name,
          arguments: tc.function.arguments,
        }));

        tracer.sendTrace({
          model: body.model,
          prompt,
          response: responseText,
          tokens: completion.usage ? {
            prompt: completion.usage.prompt_tokens,
            completion: completion.usage.completion_tokens,
            total: completion.usage.total_tokens,
          } : undefined,
          durationMs: Date.now() - startTime,
          functionCalls,
        });

        return result;
      } catch (error) {
        tracer.sendTrace({
          model: body.model,
          prompt,
          durationMs: Date.now() - startTime,
          error: String(error),
        });
        throw error;
      }
    }

    return {
      ...original,
      create: wrappedCreate.bind(original) as typeof original.create,
    };
  }
}

/**
 * Wrap an OpenAI client instance with OverseeX tracing.
 *
 * @param openai - OpenAI client instance
 * @param config - OverseeX configuration
 * @returns Wrapped OpenAI client with automatic tracing
 */
export function withOverseeX<T extends OpenAI>(openai: T, config: OverseeXConfig): T {
  const tracer = new OverseeXOpenAITracer(config);

  // Wrap chat completions
  if (openai.chat?.completions) {
    (openai.chat as any).completions = tracer.wrapChatCompletions(openai.chat.completions);
  }

  return openai;
}

/**
 * Create a traced OpenAI client.
 *
 * @param openaiConfig - OpenAI client configuration
 * @param overseeXConfig - OverseeX configuration
 * @returns Traced OpenAI client
 */
export function createTracedOpenAI(
  openaiConfig: ConstructorParameters<typeof OpenAI>[0],
  overseeXConfig: OverseeXConfig
): OpenAI {
  // Dynamic import to avoid bundling OpenAI if not used
  const OpenAIClass = require('openai').default;
  const client = new OpenAIClass(openaiConfig);
  return withOverseeX(client, overseeXConfig);
}

export { OverseeXOpenAITracer };
export default withOverseeX;
