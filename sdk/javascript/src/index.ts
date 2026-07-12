/**
 * OverseeX JavaScript/TypeScript SDK
 * 
 * Provides trace capture, agent monitoring, and test generation for JavaScript-based AI agents
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

export interface OverseeXConfig {
  apiKey: string;
  baseURL?: string;
  agentId?: string;
  autoCapture?: boolean;
}

export interface TraceData {
  input: any;
  output?: any;
  status?: 'success' | 'error' | 'failed';
  start_time?: Date;
  end_time?: Date;
  total_duration_ms?: number;
  token_count?: number;
  cost_usd?: string;
  metadata?: Record<string, any>;
  tool_calls?: ToolCall[];
  steps?: Step[];
}

export interface ToolCall {
  tool: string;
  input: any;
  output?: any;
  error?: string;
  timestamp?: Date;
}

export interface Step {
  type: string;
  tool_name?: string;
  input?: any;
  output?: any;
  error?: string;
  timestamp?: Date;
}

export interface Agent {
  id: string;
  name: string;
  description?: string;
  org_id: string;
  created_at: string;
}

export interface Trace {
  id: string;
  agent_id: string;
  trace_data: TraceData;
  status?: string;
  created_at: string;
}

export class OverseeX {
  private client: AxiosInstance;
  private config: OverseeXConfig;
  private currentTrace: Partial<TraceData> | null = null;

  constructor(config: OverseeXConfig) {
    this.config = {
      baseURL: 'https://api.overseex.com/api/v1',
      autoCapture: true,
      ...config,
    };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Start a new trace
   */
  startTrace(input: any, metadata?: Record<string, any>): string {
    const traceId = this.generateTraceId();
    
    this.currentTrace = {
      input,
      metadata: metadata || {},
      start_time: new Date(),
      tool_calls: [],
      steps: [],
      status: 'success',
    };

    return traceId;
  }

  /**
   * End the current trace and send to AgentGuard
   */
  async endTrace(output: any, status: 'success' | 'error' | 'failed' = 'success'): Promise<void> {
    if (!this.currentTrace) {
      console.warn('No active trace to end');
      return;
    }

    const endTime = new Date();
    const startTime = this.currentTrace.start_time || endTime;
    const durationMs = endTime.getTime() - startTime.getTime();

    const completeTrace: TraceData = {
      ...this.currentTrace as TraceData,
      output,
      status,
      end_time: endTime,
      total_duration_ms: durationMs,
    };

    try {
      await this.sendTrace(completeTrace);
    } catch (error) {
      console.error('Failed to send trace to AgentGuard:', error);
    } finally {
      this.currentTrace = null;
    }
  }

  /**
   * Record a tool call within the current trace
   */
  recordToolCall(toolName: string, input: any, output?: any, error?: string): void {
    if (!this.currentTrace) {
      console.warn('No active trace to record tool call');
      return;
    }

    const toolCall: ToolCall = {
      tool: toolName,
      input,
      output,
      error,
      timestamp: new Date(),
    };

    this.currentTrace.tool_calls = this.currentTrace.tool_calls || [];
    this.currentTrace.tool_calls.push(toolCall);
  }

  /**
   * Record a step within the current trace
   */
  recordStep(type: string, data: Partial<Step>): void {
    if (!this.currentTrace) {
      console.warn('No active trace to record step');
      return;
    }

    const step: Step = {
      type,
      ...data,
      timestamp: new Date(),
    };

    this.currentTrace.steps = this.currentTrace.steps || [];
    this.currentTrace.steps.push(step);
  }

  /**
   * Send a complete trace to AgentGuard
   */
  async sendTrace(traceData: TraceData): Promise<Trace> {
    if (!this.config.agentId) {
      throw new Error('Agent ID not configured');
    }

    const response = await this.client.post('/traces', {
      agent_id: this.config.agentId,
      trace_data: traceData,
      status: traceData.status || 'success',
      total_duration_ms: traceData.total_duration_ms,
      token_count: traceData.token_count,
      cost_usd: traceData.cost_usd,
    });

    return response.data;
  }

  /**
   * Wrap an async function to automatically trace its execution
   */
  traceFunction<T extends (...args: any[]) => Promise<any>>(
    fn: T,
    functionName?: string
  ): T {
    const self = this;
    
    return (async function tracedFunction(...args: any[]) {
      const name = functionName || fn.name || 'anonymous';
      self.startTrace({ function: name, args }, { traced_function: name });

      try {
        const result = await fn(...args);
        await self.endTrace(result, 'success');
        return result;
      } catch (error) {
        await self.endTrace({ error: String(error) }, 'error');
        throw error;
      }
    }) as T;
  }

  /**
   * Get all traces for the configured agent
   */
  async getTraces(limit: number = 100, skip: number = 0): Promise<Trace[]> {
    const params: Record<string, any> = {limit, skip};
    
    if (this.config.agentId) {
      params.agent_id = this.config.agentId;
    }

    const response = await this.client.get('/traces', { params });
    return response.data;
  }

  /**
   * Get a specific trace by ID
   */
  async getTrace(traceId: string): Promise<Trace> {
    const response = await this.client.get(`/traces/${traceId}`);
    return response.data;
  }

  /**
   * Get agent information
   */
  async getAgent(agentId?: string): Promise<Agent> {
    const id = agentId || this.config.agentId;
    if (!id) {
      throw new Error('Agent ID not provided');
    }

    const response = await this.client.get(`/agents/${id}`);
    return response.data;
  }

  /**
   * Generate tests from a trace
   */
  async generateTestFromTrace(traceId: string, testName?: string): Promise<{ generated_code: string; test_name: string }> {
    const response = await this.client.post('/tests/generate', {
      trace_id: traceId,
      test_name: testName,
    });
    return response.data;
  }

  /**
   * Generate a test suite from recent traces
   */
  async generateTestSuite(agentId?: string, limit: number = 20): Promise<{ generated_code: string; test_name: string }> {
    const id = agentId || this.config.agentId;
    if (!id) {
      throw new Error('Agent ID not provided');
    }

    const response = await this.client.post('/tests/generate-suite', null, {
      params: { agent_id: id, limit },
    });
    return response.data;
  }

  /**
   * Get insights about agent behavior
   */
  async getInsights(): Promise<any[]> {
    const response = await this.client.get('/insights');
    return response.data;
  }

  private generateTraceId(): string {
    return `trace_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

/**
 * Helper function to wrap OpenAI calls for automatic tracing
 */
export function traceOpenAI(overseeX: OverseeX, openai: any): any {
  return new Proxy(openai, {
    get(target, prop) {
      const original = target[prop];
      
      if (typeof original === 'object' && original !== null) {
        if (prop === 'chat' && original.completions) {
          return {
            completions: {
              create: overseeX.traceFunction(
                original.completions.create.bind(original.completions),
                'openai.chat.completions.create'
              ),
            },
          };
        }
      }
      
      return original;
    },
  });
}

export default OverseeX;
