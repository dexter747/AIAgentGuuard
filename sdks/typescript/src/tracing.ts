/**
 * OverseeX Tracing Module
 */

import type { SpanOptions, SpanData, TraceData } from './types';

/**
 * Generate a UUID v4
 */
function uuid(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Represents a traced span of execution
 */
export class Span {
  readonly spanId: string;
  readonly name: string;
  readonly agentId?: string;
  readonly startTime: number;

  parentSpanId?: string;
  endTime?: number;
  status: string = 'pending';
  error?: string;
  inputData: any = null;
  outputData: any = null;
  metadata: Record<string, any>;
  tags: string[];
  traceData: TraceData;

  constructor(options: SpanOptions) {
    this.spanId = uuid();
    this.name = options.name;
    this.agentId = options.agentId;
    this.startTime = Date.now();
    this.metadata = options.metadata || {};
    this.tags = options.tags || [];
    this.traceData = {
      llmCalls: [],
      toolCalls: [],
      handoffs: [],
      agentFlow: [],
    };
  }

  /**
   * Set the input data for this span
   */
  setInput(data: any): this {
    this.inputData = data;
    return this;
  }

  /**
   * Set the output data for this span
   */
  setOutput(data: any): this {
    this.outputData = data;
    return this;
  }

  /**
   * Set the status (success, error, pending)
   */
  setStatus(status: string): this {
    this.status = status;
    return this;
  }

  /**
   * Set error message
   */
  setError(error: string): this {
    this.error = error;
    this.status = 'error';
    return this;
  }

  /**
   * Set a custom attribute in metadata
   */
  setAttribute(key: string, value: any): this {
    this.metadata[key] = value;
    return this;
  }

  /**
   * Add a tag to the span
   */
  addTag(tag: string): this {
    if (!this.tags.includes(tag)) {
      this.tags.push(tag);
    }
    return this;
  }

  /**
   * Record an LLM call within this span
   */
  recordLLMCall(params: {
    model: string;
    prompt: string;
    response: string;
    tokens?: number;
    durationMs?: number;
    cost?: number;
  }): this {
    this.traceData.llmCalls = this.traceData.llmCalls || [];
    this.traceData.llmCalls.push({
      model: params.model,
      prompt: params.prompt.slice(0, 1000),
      response: params.response.slice(0, 1000),
      tokens: params.tokens || 0,
      durationMs: params.durationMs || 0,
      cost: params.cost || 0,
      timestamp: Date.now(),
    });
    return this;
  }

  /**
   * Record a tool call within this span
   */
  recordToolCall(params: {
    tool: string;
    input: any;
    output: any;
    durationMs?: number;
  }): this {
    this.traceData.toolCalls = this.traceData.toolCalls || [];
    this.traceData.toolCalls.push({
      tool: params.tool,
      input: String(params.input).slice(0, 500),
      output: String(params.output).slice(0, 500),
      durationMs: params.durationMs || 0,
      timestamp: Date.now(),
    });
    return this;
  }

  /**
   * Record an agent handoff within this span
   */
  recordHandoff(params: {
    fromAgent: string;
    toAgent: string;
    reason?: string;
    context?: Record<string, any>;
  }): this {
    this.traceData.handoffs = this.traceData.handoffs || [];
    this.traceData.handoffs.push({
      fromAgent: params.fromAgent,
      toAgent: params.toAgent,
      reason: params.reason,
      context: params.context || {},
      timestamp: Date.now(),
    });
    return this;
  }

  /**
   * End the span and calculate duration
   */
  end(): this {
    this.endTime = Date.now();
    return this;
  }

  /**
   * Get duration in milliseconds
   */
  get durationMs(): number {
    const end = this.endTime || Date.now();
    return end - this.startTime;
  }

  /**
   * Convert span to JSON
   */
  toJSON(): SpanData {
    return {
      spanId: this.spanId,
      parentSpanId: this.parentSpanId,
      name: this.name,
      agentId: this.agentId,
      startTime: this.startTime,
      endTime: this.endTime,
      durationMs: this.durationMs,
      status: this.status,
      error: this.error,
      inputData: this.inputData,
      outputData: this.outputData,
      traceData: this.traceData,
      metadata: this.metadata,
      tags: this.tags,
    };
  }
}

/**
 * Create a span (convenience function)
 */
export function createSpan(name: string, options?: Omit<SpanOptions, 'name'>): Span {
  return new Span({ name, ...options });
}
