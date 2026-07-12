/**
 * OverseeX Vercel AI SDK Integration
 *
 * Telemetry provider for Vercel AI SDK with automatic tracing.
 *
 * @example
 * ```typescript
 * import { generateText } from 'ai';
 * import { openai } from '@ai-sdk/openai';
 * import { OverseeXTelemetry } from '@overseex/vercel-ai';
 *
 * const telemetry = new OverseeXTelemetry({
 *   apiKey: 'your-overseex-api-key',
 *   agentId: 'your-agent-id'
 * });
 *
 * const result = await generateText({
 *   model: openai('gpt-4'),
 *   prompt: 'Hello!',
 *   experimental_telemetry: telemetry.getConfig()
 * });
 * ```
 */

export interface OverseeXConfig {
  apiKey: string;
  agentId?: string;
  baseUrl?: string;
  capturePrompts?: boolean;
  captureResponses?: boolean;
  captureToolCalls?: boolean;
  debug?: boolean;
}

interface TelemetrySpan {
  name: string;
  startTime: number;
  endTime?: number;
  attributes: Record<string, any>;
  events: Array<{ name: string; time: number; attributes?: Record<string, any> }>;
  status?: 'ok' | 'error';
  error?: string;
}

/**
 * OverseeX telemetry provider for Vercel AI SDK
 */
export class OverseeXTelemetry {
  private config: Required<OverseeXConfig>;
  private baseUrl: string;
  private spans: Map<string, TelemetrySpan> = new Map();
  private currentSpanId: string | null = null;

  constructor(config: OverseeXConfig) {
    this.config = {
      apiKey: config.apiKey,
      agentId: config.agentId || 'vercel-ai-agent',
      baseUrl: config.baseUrl || 'https://api.overseex.com',
      capturePrompts: config.capturePrompts ?? true,
      captureResponses: config.captureResponses ?? true,
      captureToolCalls: config.captureToolCalls ?? true,
      debug: config.debug ?? false,
    };
    this.baseUrl = this.config.baseUrl.replace(/\/$/, '');
  }

  private log(...args: any[]) {
    if (this.config.debug) {
      console.log('[OverseeX]', ...args);
    }
  }

  private truncate(text: string, maxLength: number = 1000): string {
    if (!text || text.length <= maxLength) return text || '';
    return text.slice(0, maxLength - 3) + '...';
  }

  private generateSpanId(): string {
    return `span_${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
  }

  /**
   * Get telemetry configuration for Vercel AI SDK
   */
  getConfig() {
    const self = this;

    return {
      isEnabled: true,
      functionId: this.config.agentId,
      metadata: {
        framework: 'vercel-ai',
        overseeX: true,
      },
      tracer: {
        startSpan(name: string, attributes?: Record<string, any>) {
          const spanId = self.generateSpanId();
          self.log('Start span:', name, spanId);

          const span: TelemetrySpan = {
            name,
            startTime: Date.now(),
            attributes: attributes || {},
            events: [],
          };

          self.spans.set(spanId, span);
          self.currentSpanId = spanId;

          return {
            spanId,
            setAttribute(key: string, value: any) {
              const s = self.spans.get(spanId);
              if (s) s.attributes[key] = value;
            },
            addEvent(name: string, attributes?: Record<string, any>) {
              const s = self.spans.get(spanId);
              if (s) {
                s.events.push({ name, time: Date.now(), attributes });
              }
            },
            setStatus(status: { code: number; message?: string }) {
              const s = self.spans.get(spanId);
              if (s) {
                s.status = status.code === 0 ? 'ok' : 'error';
                if (status.message) s.error = status.message;
              }
            },
            end() {
              const s = self.spans.get(spanId);
              if (s) {
                s.endTime = Date.now();
                self.log('End span:', name, spanId);

                // If this is a top-level span, send the trace
                if (name.includes('generateText') || name.includes('streamText') || name.includes('generateObject')) {
                  self.sendTrace(spanId);
                }
              }
            },
          };
        },
      },
    };
  }

  private async sendTrace(rootSpanId: string): Promise<void> {
    const rootSpan = this.spans.get(rootSpanId);
    if (!rootSpan) return;

    const llmCalls: any[] = [];
    const toolCalls: any[] = [];

    // Collect all spans
    this.spans.forEach((span, spanId) => {
      if (span.name.includes('llm') || span.name.includes('model')) {
        llmCalls.push({
          model: span.attributes['ai.model.id'] || span.attributes['model'] || 'unknown',
          prompt: this.config.capturePrompts
            ? this.truncate(JSON.stringify(span.attributes['ai.prompt'] || span.attributes['prompt']))
            : '[REDACTED]',
          response: this.config.captureResponses
            ? this.truncate(JSON.stringify(span.attributes['ai.response'] || span.attributes['response']))
            : '[REDACTED]',
          tokens: span.attributes['ai.usage.totalTokens'] || 0,
          durationMs: (span.endTime || Date.now()) - span.startTime,
          timestamp: span.startTime,
        });
      }

      if (span.name.includes('tool') || span.attributes['ai.toolCall']) {
        toolCalls.push({
          tool: span.attributes['ai.toolCall.name'] || span.name,
          input: this.config.captureToolCalls
            ? this.truncate(JSON.stringify(span.attributes['ai.toolCall.args']))
            : '[REDACTED]',
          output: this.config.captureToolCalls
            ? this.truncate(JSON.stringify(span.attributes['ai.toolCall.result']))
            : '[REDACTED]',
          durationMs: (span.endTime || Date.now()) - span.startTime,
          timestamp: span.startTime,
        });
      }
    });

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/traces`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: this.config.agentId,
          input_data: this.config.capturePrompts
            ? { prompt: rootSpan.attributes['ai.prompt'] || rootSpan.attributes['prompt'] }
            : { redacted: true },
          output_data: this.config.captureResponses
            ? { response: rootSpan.attributes['ai.response'] || rootSpan.attributes['response'] }
            : { redacted: true },
          trace_data: {
            llmCalls,
            toolCalls,
            handoffs: [],
            agentFlow: [],
          },
          status: rootSpan.status === 'error' ? 'error' : 'success',
          error_message: rootSpan.error,
          total_duration_ms: (rootSpan.endTime || Date.now()) - rootSpan.startTime,
          metadata: {
            framework: 'vercel-ai',
            model: rootSpan.attributes['ai.model.id'],
            promptTokens: rootSpan.attributes['ai.usage.promptTokens'],
            completionTokens: rootSpan.attributes['ai.usage.completionTokens'],
            totalTokens: rootSpan.attributes['ai.usage.totalTokens'],
          },
          tags: ['vercel-ai', rootSpan.attributes['ai.model.provider'] || 'unknown'],
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

    // Cleanup
    this.spans.clear();
    this.currentSpanId = null;
  }

  /**
   * Manually record a trace
   */
  async recordTrace(data: {
    model: string;
    prompt: string;
    response: string;
    tokens?: { prompt: number; completion: number; total: number };
    durationMs: number;
    toolCalls?: Array<{ name: string; input: any; output: any }>;
    error?: string;
  }): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/traces`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: this.config.agentId,
          input_data: this.config.capturePrompts ? { prompt: data.prompt } : { redacted: true },
          output_data: this.config.captureResponses ? { response: data.response } : { redacted: true },
          trace_data: {
            llmCalls: [{
              model: data.model,
              prompt: this.config.capturePrompts ? this.truncate(data.prompt) : '[REDACTED]',
              response: this.config.captureResponses ? this.truncate(data.response) : '[REDACTED]',
              tokens: data.tokens?.total || 0,
              durationMs: data.durationMs,
              timestamp: Date.now(),
            }],
            toolCalls: data.toolCalls?.map(tc => ({
              tool: tc.name,
              input: this.config.captureToolCalls ? this.truncate(JSON.stringify(tc.input)) : '[REDACTED]',
              output: this.config.captureToolCalls ? this.truncate(JSON.stringify(tc.output)) : '[REDACTED]',
              durationMs: 0,
              timestamp: Date.now(),
            })) || [],
          },
          status: data.error ? 'error' : 'success',
          error_message: data.error,
          total_duration_ms: data.durationMs,
          metadata: {
            framework: 'vercel-ai',
            model: data.model,
            tokens: data.tokens,
          },
          tags: ['vercel-ai', data.model.split('/')[0]],
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
}

/**
 * Create an OverseeX telemetry provider for Vercel AI SDK
 */
export function createOverseeXTelemetry(config: OverseeXConfig): OverseeXTelemetry {
  return new OverseeXTelemetry(config);
}

export default OverseeXTelemetry;
