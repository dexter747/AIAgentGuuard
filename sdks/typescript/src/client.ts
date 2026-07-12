/**
 * OverseeX Main Client
 */

import { CoordinationClient } from './coordination';
import { Span } from './tracing';
import type {
  OverseeXConfig,
  Agent,
  Trace,
  TraceData,
} from './types';

export class OverseeX {
  private apiKey: string;
  private baseUrl: string;
  private agentId?: string;
  private timeout: number;
  private debug: boolean;

  private _coordination?: CoordinationClient;

  constructor(config: OverseeXConfig) {
    this.apiKey = config.apiKey;
    this.baseUrl = (config.baseUrl || 'https://api.overseex.com').replace(/\/$/, '');
    this.agentId = config.agentId;
    this.timeout = config.timeout || 30000;
    this.debug = config.debug || false;

    if (!config.agentId && config.autoRegisterAgent !== false) {
      this.registerAgent(config.agentName || 'JavaScript Agent')
        .then((id) => {
          this.agentId = id;
        })
        .catch((err) => {
          if (this.debug) console.error('Failed to register agent:', err);
        });
    } else if (!config.agentId) {
      // Try to use first available agent
      this.request<Agent[]>('GET', '/api/v1/agents', undefined, { limit: 1 })
        .then((data) => {
          const agents = Array.isArray(data) ? data : [];
          if (agents && agents.length > 0) {
            this.agentId = agents[0]?.id;
            if (this.debug) console.log(`Using existing agent: ${agents[0]?.name || 'N/A'} (${this.agentId})`);
          }
        })
        .catch((err) => {
          if (this.debug) console.warn('Failed to fetch agents:', err);
        });
    }
  }

  /**
   * Make an API request
   */
  private async request<T>(
    method: string,
    path: string,
    data?: Record<string, any>,
    params?: Record<string, any>
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const response = await fetch(url.toString(), {
      method,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': 'OverseeX-JavaScript/0.2.0',
      },
      body: data ? JSON.stringify(data) : undefined,
      signal: AbortSignal.timeout(this.timeout),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }

    return response.json() as Promise<T>;
  }

  /**
   * Register a new agent
   */
  private async registerAgent(name: string): Promise<string> {
    try {
      const data = await this.request<Agent>('POST', '/api/v1/agents', {
        name,
        description: 'Auto-registered by OverseeX JavaScript SDK',
        endpoint_url: 'javascript://local',
        metadata: { sdk: 'javascript', version: '0.2.0' },
      });
      if (this.debug) console.log(`Registered agent: ${name} (${data.id})`);
      return data.id;
    } catch (err) {
      if (this.debug) console.warn('Failed to register agent:', err);
      return 'default-agent';
    }
  }

  /**
   * Get the coordination client
   */
  get coordination(): CoordinationClient {
    if (!this._coordination) {
      this._coordination = new CoordinationClient(this);
    }
    return this._coordination;
  }

  /**
   * Internal method for coordination client to make requests
   */
  _request<T>(method: string, path: string, data?: Record<string, any>, params?: Record<string, any>): Promise<T> {
    return this.request<T>(method, path, data, params);
  }

  // ==================
  // Tracing Methods
  // ==================

  /**
   * Wrap a function to automatically trace it
   */
  wrap<T extends (...args: any[]) => any>(
    fn: T,
    options?: { name?: string; captureInput?: boolean; captureOutput?: boolean; tags?: string[] }
  ): T {
    const client = this;
    const name = options?.name || fn.name || 'anonymous';
    const captureInput = options?.captureInput !== false;
    const captureOutput = options?.captureOutput !== false;
    const tags = options?.tags || [];

    return (async (...args: any[]) => {
      const span = client.createSpan(name, { tags });

      if (captureInput) {
        span.setInput({ args });
      }

      try {
        const result = await fn(...args);

        if (captureOutput) {
          span.setOutput(result);
        }

        span.setStatus('success');
        await span.end();
        await client.sendTrace(span);

        return result;
      } catch (error) {
        span.setError(String(error));
        await span.end();
        await client.sendTrace(span);
        throw error;
      }
    }) as T;
  }

  /**
   * Create a new span
   */
  createSpan(name: string, options?: { tags?: string[]; metadata?: Record<string, any> }): Span {
    return new Span({
      name,
      agentId: this.agentId,
      tags: options?.tags,
      metadata: options?.metadata,
    });
  }

  /**
   * Send a completed span as a trace
   */
  private async sendTrace(span: Span): Promise<void> {
    try {
      const data = span.toJSON();
      await this.request('POST', '/api/v1/traces', {
        agent_id: data.agentId,
        input_data: data.inputData,
        output_data: data.outputData,
        status: data.status,
        error_message: data.error,
        total_duration_ms: data.durationMs,
        trace_data: data.traceData,
        metadata: data.metadata,
        tags: data.tags,
      });
      if (this.debug) console.log(`Trace sent: ${span.name}`);
    } catch (err) {
      if (this.debug) console.error('Failed to send trace:', err);
    }
  }

  // ==================
  // Agent Methods
  // ==================

  /**
   * List all agents
   */
  async listAgents(): Promise<Agent[]> {
    const data = await this.request<Agent[]>('GET', '/api/v1/agents');
    return Array.isArray(data) ? data : [];
  }

  /**
   * Get a specific agent
   */
  async getAgent(agentId: string): Promise<Agent> {
    return this.request<Agent>('GET', `/api/v1/agents/${agentId}`);
  }

  /**
   * Create a new agent
   */
  async createAgent(params: {
    name: string;
    description?: string;
    endpointUrl?: string;
    metadata?: Record<string, any>;
  }): Promise<Agent> {
    return this.request<Agent>('POST', '/api/v1/agents', {
      name: params.name,
      description: params.description,
      endpoint_url: params.endpointUrl,
      metadata: params.metadata || {},
    });
  }

  // ==================
  // Trace Methods
  // ==================

  /**
   * List traces
   */
  async listTraces(params?: {
    agentId?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<Trace[]> {
    const data = await this.request<any>('GET', '/api/v1/traces', undefined, {
      agent_id: params?.agentId,
      status: params?.status,
      limit: params?.limit || 50,
      offset: params?.offset || 0,
    });
    
    if (Array.isArray(data)) return data;
    if (data && typeof data === 'object') {
      if ('traces' in data) return data.traces || [];
      if ('items' in data) return data.items || [];
    }
    return [];
  }

  /**
   * Get a specific trace
   */
  async getTrace(traceId: string): Promise<Trace> {
    return this.request<Trace>('GET', `/api/v1/traces/${traceId}`);
  }

  /**
   * Create a trace manually
   */
  async createTrace(params: {
    inputData: any;
    outputData?: any;
    status?: string;
    errorMessage?: string;
    durationMs?: number;
    traceData?: TraceData;
    metadata?: Record<string, any>;
    tags?: string[];
  }): Promise<Trace> {
    return this.request<Trace>('POST', '/api/v1/traces', {
      agent_id: this.agentId,
      input_data: params.inputData,
      output_data: params.outputData,
      status: params.status || 'success',
      error_message: params.errorMessage,
      total_duration_ms: params.durationMs,
      trace_data: params.traceData || {},
      metadata: params.metadata || {},
      tags: params.tags || [],
    });
  }

  // ==================
  // Test Methods
  // ==================

  /**
   * Create a test
   */
  async createTest(params: {
    name: string;
    inputData: string;
    expectedOutput?: string;
    agentId?: string;
  }): Promise<any> {
    return this.request('POST', '/api/v1/tests', {
      name: params.name,
      agent_id: params.agentId || this.agentId,
      test_input: params.inputData,
      expected_output: params.expectedOutput,
    });
  }

  /**
   * Run a test
   */
  async runTest(testId: string): Promise<any> {
    return this.request('POST', `/api/v1/tests/${testId}/run`);
  }
}
