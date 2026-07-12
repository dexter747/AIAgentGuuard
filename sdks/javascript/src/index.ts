/**
 * OverseeX JavaScript/TypeScript SDK
 *
 * Full-featured SDK for AI agent monitoring, tracing, and multi-agent coordination.
 * Provides trace capture, agent monitoring, test generation, and coordination intelligence.
 */

import axios, { AxiosInstance } from 'axios';

// ======================
// Configuration Types
// ======================

export interface OverseeXConfig {
  apiKey: string;
  baseURL?: string;
  agentId?: string;
  autoCapture?: boolean;
  debug?: boolean;
}

// ======================
// Core Data Types
// ======================

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
  llm_calls?: LLMCall[];
  handoffs?: HandoffRecord[];
  steps?: Step[];
  agent_flow?: string[];
}

export interface ToolCall {
  tool: string;
  input: any;
  output?: any;
  error?: string;
  timestamp?: Date;
  duration_ms?: number;
}

export interface LLMCall {
  model: string;
  prompt: any;
  response: any;
  tokens?: number;
  duration_ms?: number;
  timestamp?: Date;
  metadata?: Record<string, any>;
}

export interface HandoffRecord {
  from_agent: string;
  to_agent: string;
  context: any;
  timestamp?: Date;
  status?: 'success' | 'failed' | 'timeout';
  duration_ms?: number;
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
  status?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface Trace {
  id: string;
  agent_id: string;
  trace_data: TraceData;
  status?: string;
  input_data?: any;
  output_data?: any;
  total_duration_ms?: number;
  token_count?: number;
  cost_usd?: string;
  metadata?: Record<string, any>;
  tags?: string[];
  created_at: string;
}

// ======================
// Coordination Types
// ======================

export interface CoordinationIssue {
  id: string;
  org_id: string;
  issue_type: 'state_drift' | 'handoff_failure' | 'broken_assumption' | 'timeout' | 'schema_mismatch' | string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  trace_id?: string;
  affected_agents: string[];
  evidence: Record<string, any>;
  suggested_fix?: string;
  status: 'open' | 'resolved' | 'ignored';
  resolution_notes?: string;
  created_at?: string;
  resolved_at?: string;
}

export interface CorrectiveSuggestion {
  id: string;
  org_id: string;
  suggestion_type: 'reorder' | 'add_sync' | 'add_check' | 'fix_schema' | 'add_retry' | string;
  title: string;
  description: string;
  suggested_fix?: string;
  confidence_score: number;
  priority: 'high' | 'medium' | 'low';
  issue_id?: string;
  trace_id?: string;
  status: 'pending' | 'approved' | 'rejected';
  feedback_notes?: string;
  evidence: Record<string, any>;
  created_at?: string;
  feedback_at?: string;
}

export interface LearnedPattern {
  id: string;
  org_id: string;
  issue_type: string;
  strategy: string;
  pattern_data: Record<string, any>;
  success_count: number;
  total_applications: number;
  success_rate: number;
  is_active: boolean;
  source_suggestion_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AgentHandoff {
  id: string;
  org_id: string;
  trace_id: string;
  from_agent_id: string;
  to_agent_id: string;
  handoff_type: 'delegation' | 'escalation' | 'routing';
  status: 'success' | 'failed' | 'timeout';
  context_data: Record<string, any>;
  duration_ms?: number;
  error_message?: string;
  created_at?: string;
}

export interface CoordinationMetrics {
  total_traces: number;
  total_issues: number;
  total_handoffs: number;
  handoff_success_rate: number;
  avg_handoff_duration_ms: number;
  issues_by_type: Record<string, number>;
  issues_by_severity: Record<string, number>;
  suggestions_pending: number;
  suggestions_approved: number;
  suggestions_rejected: number;
  approval_rate: number;
  active_patterns: number;
  period_days: number;
}

export interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
    type: 'agent' | 'tool' | 'external';
    metadata?: Record<string, any>;
  }>;
  edges: Array<{
    source: string;
    target: string;
    label?: string;
    status?: string;
    weight?: number;
  }>;
}

// ======================
// Pagination Types
// ======================

export interface PaginatedResponse<T> {
  items: T[];
  total?: number;
  limit?: number;
  offset?: number;
}

// ======================
// Coordination Client
// ======================

/**
 * Client for coordination intelligence features.
 *
 * Features:
 * - List and analyze coordination issues (state drift, handoff failures, etc.)
 * - Get corrective suggestions with ML-powered confidence scores
 * - Provide feedback to improve suggestions
 * - View learned patterns
 * - Track agent handoffs
 */
export class CoordinationClient {
  private client: AxiosInstance;

  constructor(client: AxiosInstance) {
    this.client = client;
  }

  // ==================
  // Issues
  // ==================

  /**
   * List coordination issues.
   */
  async listIssues(options: {
    issueType?: string;
    severity?: string;
    status?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<CoordinationIssue[]> {
    const params: Record<string, any> = {
      limit: options.limit || 50,
      offset: options.offset || 0,
    };
    if (options.issueType) params.issue_type = options.issueType;
    if (options.severity) params.severity = options.severity;
    if (options.status) params.status = options.status;

    const response = await this.client.get('/coordination/issues', { params });
    const data = response.data;
    return Array.isArray(data) ? data : (data.items || []);
  }

  /**
   * Get a specific coordination issue.
   */
  async getIssue(issueId: string): Promise<CoordinationIssue> {
    const response = await this.client.get(`/coordination/issues/${issueId}`);
    return response.data;
  }

  /**
   * Mark an issue as resolved.
   */
  async resolveIssue(issueId: string, resolutionNotes?: string): Promise<any> {
    const response = await this.client.post(`/coordination/issues/${issueId}/resolve`, {
      resolution_notes: resolutionNotes,
    });
    return response.data;
  }

  /**
   * Mark an issue as ignored.
   */
  async ignoreIssue(issueId: string, reason?: string): Promise<any> {
    const response = await this.client.post(`/coordination/issues/${issueId}/ignore`, {
      reason,
    });
    return response.data;
  }

  // ==================
  // Suggestions
  // ==================

  /**
   * List corrective suggestions.
   */
  async listSuggestions(options: {
    status?: string;
    minConfidence?: number;
    limit?: number;
    offset?: number;
  } = {}): Promise<CorrectiveSuggestion[]> {
    const params: Record<string, any> = {
      limit: options.limit || 50,
      offset: options.offset || 0,
    };
    if (options.status) params.status = options.status;
    if (options.minConfidence !== undefined) params.min_confidence = options.minConfidence;

    const response = await this.client.get('/coordination/suggestions', { params });
    const data = response.data;
    return Array.isArray(data) ? data : (data.items || []);
  }

  /**
   * Get a specific suggestion.
   */
  async getSuggestion(suggestionId: string): Promise<CorrectiveSuggestion> {
    const response = await this.client.get(`/coordination/suggestions/${suggestionId}`);
    return response.data;
  }

  /**
   * Approve a suggestion. The pattern will be learned for future use.
   */
  async approveSuggestion(
    suggestionId: string,
    feedbackNotes?: string,
    appliedChanges?: Record<string, any>
  ): Promise<any> {
    const response = await this.client.post(`/coordination/suggestions/${suggestionId}/feedback`, {
      approved: true,
      feedback_notes: feedbackNotes,
      applied_changes: appliedChanges,
    });
    return response.data;
  }

  /**
   * Reject a suggestion.
   */
  async rejectSuggestion(suggestionId: string, feedbackNotes?: string): Promise<any> {
    const response = await this.client.post(`/coordination/suggestions/${suggestionId}/feedback`, {
      approved: false,
      feedback_notes: feedbackNotes,
    });
    return response.data;
  }

  // ==================
  // Patterns
  // ==================

  /**
   * List learned patterns.
   */
  async listPatterns(options: {
    issueType?: string;
    isActive?: boolean;
    limit?: number;
    offset?: number;
  } = {}): Promise<LearnedPattern[]> {
    const params: Record<string, any> = {
      limit: options.limit || 50,
      offset: options.offset || 0,
      is_active: options.isActive !== false,
    };
    if (options.issueType) params.issue_type = options.issueType;

    const response = await this.client.get('/coordination/patterns', { params });
    const data = response.data;
    return Array.isArray(data) ? data : (data.items || []);
  }

  /**
   * Get a specific pattern.
   */
  async getPattern(patternId: string): Promise<LearnedPattern> {
    const response = await this.client.get(`/coordination/patterns/${patternId}`);
    return response.data;
  }

  /**
   * Deactivate a pattern (stop using it for recommendations).
   */
  async deactivatePattern(patternId: string): Promise<any> {
    const response = await this.client.delete(`/coordination/patterns/${patternId}`);
    return response.data;
  }

  // ==================
  // Handoffs
  // ==================

  /**
   * List agent handoffs.
   */
  async listHandoffs(options: {
    traceId?: string;
    agentId?: string;
    limit?: number;
    offset?: number;
  } = {}): Promise<AgentHandoff[]> {
    const params: Record<string, any> = {
      limit: options.limit || 50,
      offset: options.offset || 0,
    };
    if (options.traceId) params.trace_id = options.traceId;
    if (options.agentId) params.agent_id = options.agentId;

    const response = await this.client.get('/coordination/handoffs', { params });
    const data = response.data;
    return Array.isArray(data) ? data : (data.items || []);
  }

  /**
   * Get handoff statistics.
   */
  async getHandoffStats(options: {
    agentId?: string;
    days?: number;
  } = {}): Promise<any> {
    const params: Record<string, any> = {
      days: options.days || 7,
    };
    if (options.agentId) params.agent_id = options.agentId;

    const response = await this.client.get('/coordination/handoffs/stats', { params });
    return response.data;
  }

  // ==================
  // Metrics
  // ==================

  /**
   * Get coordination metrics.
   */
  async getMetrics(options: {
    agentId?: string;
    days?: number;
  } = {}): Promise<CoordinationMetrics> {
    const params: Record<string, any> = {
      days: options.days || 7,
    };
    if (options.agentId) params.agent_id = options.agentId;

    const response = await this.client.get('/coordination/metrics', { params });
    return response.data;
  }

  // ==================
  // Analysis
  // ==================

  /**
   * Analyze traces for coordination issues.
   */
  async analyzeTraces(traceIds: string[], autoCreateIssues: boolean = true): Promise<any> {
    const response = await this.client.post('/coordination/analyze', {
      trace_ids: traceIds,
      auto_create_issues: autoCreateIssues,
    });
    return response.data;
  }

  /**
   * Get coordination graph data for visualization.
   */
  async getGraphData(options: {
    traceId?: string;
    days?: number;
  } = {}): Promise<GraphData> {
    const params: Record<string, any> = {
      days: options.days || 7,
    };
    if (options.traceId) params.trace_id = options.traceId;

    const response = await this.client.get('/coordination/graph', { params });
    return response.data;
  }
}

// ======================
// Span Context Manager
// ======================

/**
 * Span for tracking nested operations within a trace.
 */
export class Span {
  private overseeX: OverseeX;
  private name: string;
  private startTime: Date;
  private metadata: Record<string, any>;
  private toolCalls: ToolCall[] = [];
  private llmCalls: LLMCall[] = [];
  private childSpans: Span[] = [];
  private ended: boolean = false;

  constructor(overseeX: OverseeX, name: string, metadata: Record<string, any> = {}) {
    this.overseeX = overseeX;
    this.name = name;
    this.startTime = new Date();
    this.metadata = metadata;
  }

  /**
   * Record a tool call within this span.
   */
  recordToolCall(toolName: string, input: any, output?: any, error?: string): this {
    this.toolCalls.push({
      tool: toolName,
      input,
      output,
      error,
      timestamp: new Date(),
    });
    return this;
  }

  /**
   * Record an LLM call within this span.
   */
  recordLLMCall(
    model: string,
    prompt: any,
    response: any,
    tokens?: number,
    durationMs?: number,
    metadata?: Record<string, any>
  ): this {
    this.llmCalls.push({
      model,
      prompt,
      response,
      tokens,
      duration_ms: durationMs,
      timestamp: new Date(),
      metadata,
    });
    return this;
  }

  /**
   * Create a child span.
   */
  startChildSpan(name: string, metadata: Record<string, any> = {}): Span {
    const child = new Span(this.overseeX, name, metadata);
    this.childSpans.push(child);
    return child;
  }

  /**
   * End this span and return the data.
   */
  end(): { name: string; durationMs: number; metadata: Record<string, any>; toolCalls: ToolCall[]; llmCalls: LLMCall[] } {
    if (this.ended) {
      throw new Error('Span already ended');
    }
    this.ended = true;
    const endTime = new Date();
    const durationMs = endTime.getTime() - this.startTime.getTime();

    return {
      name: this.name,
      durationMs,
      metadata: this.metadata,
      toolCalls: this.toolCalls,
      llmCalls: this.llmCalls,
    };
  }
}

// ======================
// Main OverseeX Client
// ======================

export class OverseeX {
  private client: AxiosInstance;
  private config: OverseeXConfig;
  private currentTrace: Partial<TraceData> | null = null;
  private currentSpan: Span | null = null;

  /**
   * Coordination intelligence client for multi-agent features.
   */
  public coordination: CoordinationClient;

  constructor(config: OverseeXConfig) {
    this.config = {
      baseURL: 'https://api.overseex.com/api/v1',
      autoCapture: true,
      debug: false,
      ...config,
    };

    this.client = axios.create({
      baseURL: this.config.baseURL,
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json',
      },
    });

    // Initialize sub-clients
    this.coordination = new CoordinationClient(this.client);
  }

  // ======================
  // Trace Management
  // ======================

  /**
   * Start a new trace.
   */
  startTrace(input: any, metadata?: Record<string, any>): string {
    const traceId = this.generateTraceId();

    this.currentTrace = {
      input,
      metadata: metadata || {},
      start_time: new Date(),
      tool_calls: [],
      llm_calls: [],
      handoffs: [],
      steps: [],
      agent_flow: [],
      status: 'success',
    };

    if (this.config.debug) {
      console.log(`[OverseeX] Started trace: ${traceId}`);
    }

    return traceId;
  }

  /**
   * End the current trace and send to OverseeX.
   */
  async endTrace(output: any, status: 'success' | 'error' | 'failed' = 'success'): Promise<Trace | null> {
    if (!this.currentTrace) {
      console.warn('[OverseeX] No active trace to end');
      return null;
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
      const result = await this.sendTrace(completeTrace);
      if (this.config.debug) {
        console.log(`[OverseeX] Trace sent successfully`);
      }
      return result;
    } catch (error) {
      console.error('[OverseeX] Failed to send trace:', error);
      return null;
    } finally {
      this.currentTrace = null;
    }
  }

  /**
   * Record a tool call within the current trace.
   */
  recordToolCall(toolName: string, input: any, output?: any, error?: string): void {
    if (!this.currentTrace) {
      console.warn('[OverseeX] No active trace to record tool call');
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
   * Record an LLM call within the current trace.
   */
  recordLLMCall(
    model: string,
    prompt: any,
    response: any,
    tokens?: number,
    durationMs?: number,
    metadata?: Record<string, any>
  ): void {
    if (!this.currentTrace) {
      console.warn('[OverseeX] No active trace to record LLM call');
      return;
    }

    const llmCall: LLMCall = {
      model,
      prompt,
      response,
      tokens,
      duration_ms: durationMs,
      timestamp: new Date(),
      metadata,
    };

    this.currentTrace.llm_calls = this.currentTrace.llm_calls || [];
    this.currentTrace.llm_calls.push(llmCall);
  }

  /**
   * Record an agent handoff within the current trace.
   */
  recordHandoff(
    fromAgent: string,
    toAgent: string,
    context: any,
    status: 'success' | 'failed' | 'timeout' = 'success',
    durationMs?: number
  ): void {
    if (!this.currentTrace) {
      console.warn('[OverseeX] No active trace to record handoff');
      return;
    }

    const handoff: HandoffRecord = {
      from_agent: fromAgent,
      to_agent: toAgent,
      context,
      timestamp: new Date(),
      status,
      duration_ms: durationMs,
    };

    this.currentTrace.handoffs = this.currentTrace.handoffs || [];
    this.currentTrace.handoffs.push(handoff);

    // Track agent flow
    this.currentTrace.agent_flow = this.currentTrace.agent_flow || [];
    if (!this.currentTrace.agent_flow.includes(fromAgent)) {
      this.currentTrace.agent_flow.push(fromAgent);
    }
    if (!this.currentTrace.agent_flow.includes(toAgent)) {
      this.currentTrace.agent_flow.push(toAgent);
    }
  }

  /**
   * Record a step within the current trace.
   */
  recordStep(type: string, data: Partial<Step>): void {
    if (!this.currentTrace) {
      console.warn('[OverseeX] No active trace to record step');
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

  // ======================
  // Span Management
  // ======================

  /**
   * Start a new span within the current trace.
   */
  startSpan(name: string, metadata: Record<string, any> = {}): Span {
    const span = new Span(this, name, metadata);
    this.currentSpan = span;
    return span;
  }

  // ======================
  // API Methods
  // ======================

  /**
   * Send a complete trace to OverseeX.
   */
  async sendTrace(traceData: TraceData): Promise<Trace> {
    if (!this.config.agentId) {
      throw new Error('Agent ID not configured');
    }

    const response = await this.client.post('/traces', {
      agent_id: this.config.agentId,
      input_data: traceData.input,
      output_data: traceData.output,
      trace_data: {
        tool_calls: traceData.tool_calls,
        llm_calls: traceData.llm_calls,
        handoffs: traceData.handoffs,
        steps: traceData.steps,
        agent_flow: traceData.agent_flow,
      },
      status: traceData.status || 'success',
      total_duration_ms: traceData.total_duration_ms,
      token_count: traceData.token_count,
      cost_usd: traceData.cost_usd,
      metadata: traceData.metadata,
    });

    return response.data;
  }

  /**
   * Get all traces for the configured agent.
   */
  async getTraces(limit: number = 100, skip: number = 0): Promise<Trace[]> {
    const params: Record<string, any> = { limit, skip };

    if (this.config.agentId) {
      params.agent_id = this.config.agentId;
    }

    const response = await this.client.get('/traces', { params });
    return response.data;
  }

  /**
   * Get a specific trace by ID.
   */
  async getTrace(traceId: string): Promise<Trace> {
    const response = await this.client.get(`/traces/${traceId}`);
    return response.data;
  }

  /**
   * Get agent information.
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
   * List all agents.
   */
  async listAgents(): Promise<Agent[]> {
    const response = await this.client.get('/agents');
    return response.data;
  }

  /**
   * Create a new agent.
   */
  async createAgent(name: string, description?: string, metadata?: Record<string, any>): Promise<Agent> {
    const response = await this.client.post('/agents', {
      name,
      description,
      metadata,
    });
    return response.data;
  }

  // ======================
  // Test Generation
  // ======================

  /**
   * Generate tests from a trace.
   */
  async generateTestFromTrace(traceId: string, testName?: string): Promise<{ generated_code: string; test_name: string }> {
    const response = await this.client.post('/tests/generate', {
      trace_id: traceId,
      test_name: testName,
    });
    return response.data;
  }

  /**
   * Generate a test suite from recent traces.
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

  // ======================
  // Insights
  // ======================

  /**
   * Get insights about agent behavior.
   */
  async getInsights(): Promise<any[]> {
    const response = await this.client.get('/insights');
    return response.data;
  }

  // ======================
  // Function Wrapper
  // ======================

  /**
   * Wrap an async function to automatically trace its execution.
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
   * Wrap a multi-agent workflow to automatically trace handoffs.
   */
  traceWorkflow<T>(
    workflow: () => Promise<T>,
    workflowName: string,
    metadata?: Record<string, any>
  ): Promise<T> {
    return new Promise(async (resolve, reject) => {
      this.startTrace({ workflow: workflowName }, { ...metadata, workflow_name: workflowName });

      try {
        const result = await workflow();
        await this.endTrace(result, 'success');
        resolve(result);
      } catch (error) {
        await this.endTrace({ error: String(error) }, 'error');
        reject(error);
      }
    });
  }

  // ======================
  // Utilities
  // ======================

  private generateTraceId(): string {
    return `trace_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Set the agent ID for subsequent operations.
   */
  setAgentId(agentId: string): void {
    this.config.agentId = agentId;
  }

  /**
   * Get the current configuration.
   */
  getConfig(): OverseeXConfig {
    return { ...this.config };
  }
}

// ======================
// Helper Functions
// ======================

/**
 * Helper function to wrap OpenAI calls for automatic tracing.
 */
export function traceOpenAI(overseeX: OverseeX, openai: any): any {
  return new Proxy(openai, {
    get(target, prop) {
      const original = target[prop];

      if (typeof original === 'object' && original !== null) {
        if (prop === 'chat' && original.completions) {
          return {
            completions: {
              create: async (...args: any[]) => {
                const startTime = Date.now();
                const result = await original.completions.create(...args);
                const duration = Date.now() - startTime;

                // Record LLM call
                const messages = args[0]?.messages;
                const model = args[0]?.model || result.model;
                const tokens = result.usage?.total_tokens;

                overseeX.recordLLMCall(
                  model,
                  messages,
                  result.choices?.[0]?.message?.content,
                  tokens,
                  duration,
                  { model, finish_reason: result.choices?.[0]?.finish_reason }
                );

                return result;
              },
            },
          };
        }
      }

      return original;
    },
  });
}

/**
 * Helper function to wrap Anthropic calls for automatic tracing.
 */
export function traceAnthropic(overseeX: OverseeX, anthropic: any): any {
  return new Proxy(anthropic, {
    get(target, prop) {
      const original = target[prop];

      if (typeof original === 'object' && original !== null) {
        if (prop === 'messages') {
          return {
            create: async (...args: any[]) => {
              const startTime = Date.now();
              const result = await original.create(...args);
              const duration = Date.now() - startTime;

              // Record LLM call
              const messages = args[0]?.messages;
              const model = args[0]?.model || result.model;
              const tokens = result.usage?.input_tokens + result.usage?.output_tokens;

              overseeX.recordLLMCall(
                model,
                messages,
                result.content?.[0]?.text,
                tokens,
                duration,
                { model, stop_reason: result.stop_reason }
              );

              return result;
            },
          };
        }
      }

      return original;
    },
  });
}

/**
 * Create an OverseeX client instance.
 */
export function createClient(config: OverseeXConfig): OverseeX {
  return new OverseeX(config);
}

export default OverseeX;
