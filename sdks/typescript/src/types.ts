/**
 * OverseeX Type Definitions
 */

export interface OverseeXConfig {
  apiKey: string;
  baseUrl?: string;
  agentId?: string;
  autoRegisterAgent?: boolean;
  agentName?: string;
  timeout?: number;
  debug?: boolean;
}

export interface Agent {
  id: string;
  name: string;
  description?: string;
  endpointUrl?: string;
  status: string;
  metadata: Record<string, any>;
  createdAt?: string;
  updatedAt?: string;
}

export interface Trace {
  id: string;
  agentId: string;
  inputData: any;
  outputData: any;
  status: 'success' | 'error' | 'pending';
  errorMessage?: string;
  totalDurationMs?: number;
  tokenCount?: number;
  costUsd?: string;
  traceData: TraceData;
  metadata: Record<string, any>;
  tags: string[];
  createdAt?: string;
}

export interface TraceData {
  llmCalls?: LLMCall[];
  toolCalls?: ToolCall[];
  handoffs?: Handoff[];
  agentFlow?: string[];
}

export interface LLMCall {
  model: string;
  prompt: string;
  response: string;
  tokens: number;
  durationMs: number;
  cost: number;
  timestamp: number;
}

export interface ToolCall {
  tool: string;
  input: string;
  output: string;
  durationMs: number;
  timestamp: number;
}

export interface Handoff {
  fromAgent: string;
  toAgent: string;
  reason?: string;
  context?: Record<string, any>;
  timestamp: number;
}

// Coordination Types

export type IssueSeverity = 'critical' | 'high' | 'medium' | 'low';
export type IssueType = 'state_drift' | 'handoff_failure' | 'broken_assumption' | 'duplicate_work' | 'circular_dependency';
export type IssueStatus = 'open' | 'resolved' | 'ignored';
export type SuggestionStatus = 'pending' | 'approved' | 'rejected';

export interface CoordinationIssue {
  id: string;
  orgId: string;
  issueType: IssueType;
  severity: IssueSeverity;
  title: string;
  description: string;
  traceId?: string;
  affectedAgents: string[];
  evidence: Record<string, any>;
  suggestedFix?: string;
  status: IssueStatus;
  resolutionNotes?: string;
  createdAt?: string;
  resolvedAt?: string;
}

export interface CorrectiveSuggestion {
  id: string;
  orgId: string;
  suggestionType: string;
  title: string;
  description: string;
  suggestedFix?: string;
  confidenceScore: number;
  priority: string;
  issueId?: string;
  traceId?: string;
  status: SuggestionStatus;
  feedbackNotes?: string;
  evidence: Record<string, any>;
  createdAt?: string;
  feedbackAt?: string;
}

export interface LearnedPattern {
  id: string;
  orgId: string;
  issueType: string;
  strategy: string;
  patternData: Record<string, any>;
  successCount: number;
  totalApplications: number;
  successRate: number;
  isActive: boolean;
  sourceSuggestionId?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface AgentHandoff {
  id: string;
  orgId: string;
  traceId: string;
  fromAgentId: string;
  toAgentId: string;
  handoffType: string;
  status: string;
  contextData: Record<string, any>;
  durationMs?: number;
  errorMessage?: string;
  createdAt?: string;
}

export interface CoordinationMetrics {
  totalTraces: number;
  totalIssues: number;
  totalHandoffs: number;
  handoffSuccessRate: number;
  avgHandoffDurationMs: number;
  issuesByType: Record<string, number>;
  issuesBySeverity: Record<string, number>;
  suggestionsPending: number;
  suggestionsApproved: number;
  suggestionsRejected: number;
  approvalRate: number;
  activePatterns: number;
  periodDays: number;
}

export interface ListIssuesParams {
  issueType?: IssueType;
  severity?: IssueSeverity;
  status?: IssueStatus;
  limit?: number;
  offset?: number;
}

export interface ListSuggestionsParams {
  status?: SuggestionStatus;
  minConfidence?: number;
  limit?: number;
  offset?: number;
}

export interface ListPatternsParams {
  issueType?: string;
  isActive?: boolean;
  limit?: number;
  offset?: number;
}

export interface ListHandoffsParams {
  traceId?: string;
  agentId?: string;
  limit?: number;
  offset?: number;
}

export interface FeedbackParams {
  approved: boolean;
  feedbackNotes?: string;
  appliedChanges?: Record<string, any>;
}

export interface SpanOptions {
  name: string;
  agentId?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface SpanData {
  spanId: string;
  parentSpanId?: string;
  name: string;
  agentId?: string;
  startTime: number;
  endTime?: number;
  durationMs: number;
  status: string;
  error?: string;
  inputData: any;
  outputData: any;
  traceData: TraceData;
  metadata: Record<string, any>;
  tags: string[];
}
