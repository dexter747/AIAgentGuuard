/**
 * OverseeX Coordination Client
 *
 * Client for accessing multi-agent coordination intelligence features.
 */

import type {
  CoordinationIssue,
  CorrectiveSuggestion,
  LearnedPattern,
  AgentHandoff,
  CoordinationMetrics,
  ListIssuesParams,
  ListSuggestionsParams,
  ListPatternsParams,
  ListHandoffsParams,
  FeedbackParams,
} from './types';

// Forward declaration to avoid circular import
interface OverseeXClient {
  _request<T>(method: string, path: string, data?: Record<string, any>, params?: Record<string, any>): Promise<T>;
}

/**
 * Client for coordination intelligence features
 */
export class CoordinationClient {
  private client: OverseeXClient;

  constructor(client: OverseeXClient) {
    this.client = client;
  }

  private request<T>(method: string, path: string, data?: Record<string, any>, params?: Record<string, any>): Promise<T> {
    return this.client._request<T>(method, `/api/v1/coordination${path}`, data, params);
  }

  // ==================
  // Issues
  // ==================

  /**
   * List coordination issues
   */
  async listIssues(params?: ListIssuesParams): Promise<CoordinationIssue[]> {
    const data = await this.request<{ items: CoordinationIssue[] } | CoordinationIssue[]>(
      'GET',
      '/issues',
      undefined,
      {
        issue_type: params?.issueType,
        severity: params?.severity,
        status: params?.status,
        limit: params?.limit || 50,
        offset: params?.offset || 0,
      }
    );
    return Array.isArray(data) ? data : data.items;
  }

  /**
   * Get a specific coordination issue
   */
  async getIssue(issueId: string): Promise<CoordinationIssue> {
    return this.request<CoordinationIssue>('GET', `/issues/${issueId}`);
  }

  /**
   * Mark an issue as resolved
   */
  async resolveIssue(issueId: string, resolutionNotes?: string): Promise<any> {
    return this.request('POST', `/issues/${issueId}/resolve`, {
      resolution_notes: resolutionNotes,
    });
  }

  /**
   * Mark an issue as ignored
   */
  async ignoreIssue(issueId: string, reason?: string): Promise<any> {
    return this.request('POST', `/issues/${issueId}/ignore`, {
      reason,
    });
  }

  // ==================
  // Suggestions
  // ==================

  /**
   * List corrective suggestions
   */
  async listSuggestions(params?: ListSuggestionsParams): Promise<CorrectiveSuggestion[]> {
    const data = await this.request<{ items: CorrectiveSuggestion[] } | CorrectiveSuggestion[]>(
      'GET',
      '/suggestions',
      undefined,
      {
        status: params?.status,
        min_confidence: params?.minConfidence,
        limit: params?.limit || 50,
        offset: params?.offset || 0,
      }
    );
    return Array.isArray(data) ? data : data.items;
  }

  /**
   * Get a specific suggestion
   */
  async getSuggestion(suggestionId: string): Promise<CorrectiveSuggestion> {
    return this.request<CorrectiveSuggestion>('GET', `/suggestions/${suggestionId}`);
  }

  /**
   * Approve a suggestion (this trains the model)
   */
  async approveSuggestion(
    suggestionId: string,
    feedbackNotes?: string,
    appliedChanges?: Record<string, any>
  ): Promise<any> {
    return this.request('POST', `/suggestions/${suggestionId}/feedback`, {
      approved: true,
      feedback_notes: feedbackNotes,
      applied_changes: appliedChanges,
    });
  }

  /**
   * Reject a suggestion
   */
  async rejectSuggestion(suggestionId: string, feedbackNotes?: string): Promise<any> {
    return this.request('POST', `/suggestions/${suggestionId}/feedback`, {
      approved: false,
      feedback_notes: feedbackNotes,
    });
  }

  /**
   * Provide feedback on a suggestion
   */
  async provideFeedback(suggestionId: string, params: FeedbackParams): Promise<any> {
    return this.request('POST', `/suggestions/${suggestionId}/feedback`, {
      approved: params.approved,
      feedback_notes: params.feedbackNotes,
      applied_changes: params.appliedChanges,
    });
  }

  // ==================
  // Patterns
  // ==================

  /**
   * List learned patterns
   */
  async listPatterns(params?: ListPatternsParams): Promise<LearnedPattern[]> {
    const data = await this.request<{ items: LearnedPattern[] } | LearnedPattern[]>(
      'GET',
      '/patterns',
      undefined,
      {
        issue_type: params?.issueType,
        is_active: params?.isActive !== false,
        limit: params?.limit || 50,
        offset: params?.offset || 0,
      }
    );
    return Array.isArray(data) ? data : data.items;
  }

  /**
   * Get a specific pattern
   */
  async getPattern(patternId: string): Promise<LearnedPattern> {
    return this.request<LearnedPattern>('GET', `/patterns/${patternId}`);
  }

  /**
   * Deactivate a pattern
   */
  async deactivatePattern(patternId: string): Promise<any> {
    return this.request('POST', `/patterns/${patternId}/deactivate`);
  }

  // ==================
  // Handoffs
  // ==================

  /**
   * List agent handoffs
   */
  async listHandoffs(params?: ListHandoffsParams): Promise<AgentHandoff[]> {
    const data = await this.request<{ items: AgentHandoff[] } | AgentHandoff[]>(
      'GET',
      '/handoffs',
      undefined,
      {
        trace_id: params?.traceId,
        agent_id: params?.agentId,
        limit: params?.limit || 50,
        offset: params?.offset || 0,
      }
    );
    return Array.isArray(data) ? data : data.items;
  }

  /**
   * Get handoff statistics
   */
  async getHandoffStats(params?: { agentId?: string; days?: number }): Promise<any> {
    return this.request('GET', '/handoffs/stats', undefined, {
      agent_id: params?.agentId,
      days: params?.days || 7,
    });
  }

  // ==================
  // Metrics
  // ==================

  /**
   * Get coordination metrics
   */
  async getMetrics(params?: { agentId?: string; days?: number }): Promise<CoordinationMetrics> {
    return this.request<CoordinationMetrics>('GET', '/metrics', undefined, {
      agent_id: params?.agentId,
      days: params?.days || 7,
    });
  }

  // ==================
  // Analysis
  // ==================

  /**
   * Analyze traces for coordination issues
   */
  async analyzeTraces(traceIds: string[], autoCreateIssues: boolean = true): Promise<any> {
    return this.request('POST', '/analyze', {
      trace_ids: traceIds,
      auto_create_issues: autoCreateIssues,
    });
  }

  /**
   * Get coordination graph data for visualization
   */
  async getGraphData(params?: { traceId?: string; days?: number }): Promise<any> {
    return this.request('GET', '/graph', undefined, {
      trace_id: params?.traceId,
      days: params?.days || 7,
    });
  }
}
