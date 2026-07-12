// API Client for OverseeX Backend
// IMPORTANT: Always use HTTPS in production
const API_BASE_URL = (() => {
  // Force HTTPS for production domains
  let baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.overseex.com'
  
  // Ensure HTTPS is used (prevent mixed content errors)
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    baseUrl = baseUrl.replace('http://', 'https://')
  }
  
  // Ensure /api/v1 suffix
  return baseUrl.endsWith('/api/v1') ? baseUrl : `${baseUrl}/api/v1`
})()

class APIClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token')
    }
  }

  setToken(token: string | null) {
    this.token = token
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Generic HTTP methods
  get<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  post<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  put<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  delete<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  // Auth endpoints
  auth = {
    login: (email: string, password: string) =>
      this.request<{ access_token: string; user: any }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),

    register: (data: { email: string; password: string; full_name: string; company_name?: string }) =>
      this.request<{ access_token: string; user: any }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    forgotPassword: (email: string) =>
      this.request<{ message: string }>('/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email }),
      }),

    resetPassword: (token: string, password: string) =>
      this.request<{ message: string }>('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ token, password }),
      }),

    me: () => this.request<any>('/auth/me'),
  }

  // Agents endpoints
  agents = {
    list: () => this.request<any[]>('/agents'),
    get: (id: string) => this.request<any>(`/agents/${id}`),
    create: (data: any) => this.request<any>('/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => this.request<any>(`/agents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => this.request<void>(`/agents/${id}`, {
      method: 'DELETE',
    }),
    stats: (id: string) => this.request<any>(`/agents/${id}/stats`),
  }

  // Traces endpoints
  traces = {
    list: (params?: { agent_id?: string; limit?: number; offset?: number }) => {
      const query = new URLSearchParams()
      if (params?.agent_id) query.set('agent_id', params.agent_id)
      if (params?.limit) query.set('limit', params.limit.toString())
      if (params?.offset) query.set('offset', params.offset.toString())
      return this.request<{ traces: any[]; total: number }>(`/traces?${query}`)
    },
    get: (id: string) => this.request<any>(`/traces/${id}`),
    create: (data: any) => this.request<any>('/traces', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  }

  // Tests endpoints
  tests = {
    list: () => this.request<any[]>('/tests'),
    get: (id: string) => this.request<any>(`/tests/${id}`),
    create: (data: any) => this.request<any>('/tests', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    run: (id: string) => this.request<any>(`/tests/${id}/run`, {
      method: 'POST',
    }),
  }

  // API Keys endpoints
  apiKeys = {
    list: () => this.request<any[]>('/api-keys'),
    create: (name: string) => this.request<any>('/api-keys', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
    revoke: (id: string) => this.request<void>(`/api-keys/${id}/revoke`, {
      method: 'POST',
    }),
    delete: (id: string) => this.request<void>(`/api-keys/${id}`, {
      method: 'DELETE',
    }),
  }

  // Dashboard stats
  dashboard = {
    stats: () => this.request<any>('/dashboard/stats'),
    recentTraces: (limit: number = 10) => 
      this.request<any[]>(`/dashboard/recent-traces?limit=${limit}`),
    recentErrors: (limit: number = 10) =>
      this.request<any[]>(`/dashboard/recent-errors?limit=${limit}`),
  }

  // Webhooks endpoints
  webhooks = {
    list: () => this.request<any[]>('/webhooks'),
    create: (data: any) => this.request<any>('/webhooks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => this.request<any>(`/webhooks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => this.request<void>(`/webhooks/${id}`, {
      method: 'DELETE',
    }),
    test: (id: string) => this.request<any>(`/webhooks/${id}/test`, {
      method: 'POST',
    }),
  }

  // Organizations
  organizations = {
    get: () => this.request<any>('/organizations/me'),
    update: (data: any) => this.request<any>('/organizations/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    members: () => this.request<any[]>('/organizations/members'),
    inviteMember: (email: string, role: string) => this.request<any>('/organizations/members', {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    }),
    removeMember: (userId: string) => this.request<void>(`/organizations/members/${userId}`, {
      method: 'DELETE',
    }),
  }

  // Insights endpoints
  insights = {
    list: () => this.request<any[]>('/insights'),
    coordination: () => this.request<any[]>('/insights/coordination'),
  }

  // Coordination endpoints
  coordination = {
    // Issues
    listIssues: (params?: { issue_type?: string; severity?: string; status?: string; limit?: number; offset?: number }) => {
      const query = new URLSearchParams()
      if (params?.issue_type) query.set('issue_type', params.issue_type)
      if (params?.severity) query.set('severity', params.severity)
      if (params?.status) query.set('status', params.status)
      if (params?.limit) query.set('limit', params.limit.toString())
      if (params?.offset) query.set('offset', params.offset.toString())
      return this.request<any[]>(`/coordination/issues?${query}`)
    },
    getIssue: (id: string) => this.request<any>(`/coordination/issues/${id}`),
    resolveIssue: (id: string, notes?: string) => this.request<any>(`/coordination/issues/${id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution_notes: notes }),
    }),
    ignoreIssue: (id: string, reason?: string) => this.request<any>(`/coordination/issues/${id}/ignore`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    }),

    // Suggestions
    listSuggestions: (params?: { status?: string; min_confidence?: number; limit?: number }) => {
      const query = new URLSearchParams()
      if (params?.status) query.set('status', params.status)
      if (params?.min_confidence) query.set('min_confidence', params.min_confidence.toString())
      if (params?.limit) query.set('limit', params.limit.toString())
      return this.request<any[]>(`/coordination/suggestions?${query}`)
    },
    getSuggestion: (id: string) => this.request<any>(`/coordination/suggestions/${id}`),
    provideFeedback: (id: string, status: 'approved' | 'rejected', notes?: string) =>
      this.request<any>(`/coordination/suggestions/${id}/feedback`, {
        method: 'POST',
        body: JSON.stringify({ status, feedback_notes: notes }),
      }),

    // Patterns
    listPatterns: (params?: { issue_type?: string; is_active?: boolean; limit?: number }) => {
      const query = new URLSearchParams()
      if (params?.issue_type) query.set('issue_type', params.issue_type)
      if (params?.is_active !== undefined) query.set('is_active', params.is_active.toString())
      if (params?.limit) query.set('limit', params.limit.toString())
      return this.request<any[]>(`/coordination/patterns?${query}`)
    },
    getPattern: (id: string) => this.request<any>(`/coordination/patterns/${id}`),
    deactivatePattern: (id: string) => this.request<any>(`/coordination/patterns/${id}/deactivate`, {
      method: 'POST',
    }),

    // Handoffs
    listHandoffs: (params?: { trace_id?: string; agent_id?: string; limit?: number }) => {
      const query = new URLSearchParams()
      if (params?.trace_id) query.set('trace_id', params.trace_id)
      if (params?.agent_id) query.set('agent_id', params.agent_id)
      if (params?.limit) query.set('limit', params.limit.toString())
      return this.request<any[]>(`/coordination/handoffs?${query}`)
    },
    getHandoffStats: (params?: { agent_id?: string; days?: number }) => {
      const query = new URLSearchParams()
      if (params?.agent_id) query.set('agent_id', params.agent_id)
      if (params?.days) query.set('days', params.days.toString())
      return this.request<any>(`/coordination/handoffs/stats?${query}`)
    },

    // Metrics & Analysis
    getMetrics: (params?: { agent_id?: string; days?: number }) => {
      const query = new URLSearchParams()
      if (params?.agent_id) query.set('agent_id', params.agent_id)
      if (params?.days) query.set('days', params.days.toString())
      return this.request<any>(`/coordination/metrics?${query}`)
    },
    analyze: (traceIds: string[], autoCreateIssues: boolean = true) =>
      this.request<any>('/coordination/analyze', {
        method: 'POST',
        body: JSON.stringify({ trace_ids: traceIds, auto_create_issues: autoCreateIssues }),
      }),
    getGraph: (params?: { trace_id?: string; time_window_hours?: number }) => {
      const query = new URLSearchParams()
      if (params?.trace_id) query.set('trace_id', params.trace_id)
      if (params?.time_window_hours) query.set('time_window_hours', params.time_window_hours.toString())
      return this.request<any>(`/coordination/graph?${query}`)
    },
  }

  // Regressions endpoints
  regressions = {
    list: (params?: { time_window?: string; severity?: string }) => {
      const query = new URLSearchParams()
      if (params?.time_window) query.set('time_window', params.time_window)
      if (params?.severity) query.set('severity', params.severity)
      return this.request<any[]>(`/regressions?${query}`)
    },
    get: (id: string) => this.request<any>(`/regressions/${id}`),
  }

  // Mocks endpoints
  mocks = {
    list: () => this.request<any>('/mocks'),
    get: (toolName: string) => this.request<any>(`/mocks/${toolName}`),
    create: (data: any) => this.request<any>('/mocks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (toolName: string, data: any) => this.request<any>(`/mocks/${toolName}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (toolName: string) => this.request<void>(`/mocks/${toolName}`, {
      method: 'DELETE',
    }),
    toggle: (toolName: string) => this.request<any>(`/mocks/${toolName}/toggle`, {
      method: 'POST',
    }),
    history: (toolName: string) => this.request<any>(`/mocks/${toolName}/history`),
    reset: () => this.request<any>('/mocks/reset', {
      method: 'POST',
    }),
  }

  // Health monitoring endpoints
  health = {
    dashboard: () => this.request<any>('/health-monitoring/dashboard'),
    status: (agentId: string) => this.request<any>(`/health-monitoring/status/${agentId}`),
    history: (agentId: string, limit: number = 50) => 
      this.request<any>(`/health-monitoring/history/${agentId}?limit=${limit}`),
    updateAlerts: (agentId: string, data: any) => this.request<any>(`/health-monitoring/update-alerts/${agentId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  }
}

export const apiClient = new APIClient()
export default apiClient
