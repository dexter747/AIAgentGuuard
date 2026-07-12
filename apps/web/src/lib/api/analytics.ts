/**
 * Analytics API client
 */

const API_BASE = (() => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.overseex.com'
  return baseUrl.endsWith('/api/v1') ? baseUrl : `${baseUrl}/api/v1`
})();
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

interface DashboardStats {
  total_traces: number;
  success_rate: number;
  total_errors: number;
  avg_duration: number;
  total_cost: number;
  total_tokens: number;
  traces_today: number;
  change_percent: {
    traces: number;
    errors: number;
    success_rate: number;
  };
}

interface TracesByDay {
  date: string;
  count: number;
  success_count: number;
  error_count: number;
}

interface AgentPerformance {
  agent_id: string;
  agent_name: string;
  total_traces: number;
  success_rate: number;
  avg_duration: number;
  total_cost: number;
}

interface CostBreakdown {
  agent_name: string;
  total_tokens: number;
  total_cost: number;
  percentage: number;
}

async function fetchWithAuth(url: string): Promise<Response> {
  const response = await fetch(url, {
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return response;
}

export async function getDashboardStats(days: number = 7): Promise<DashboardStats> {
  const response = await fetchWithAuth(
    `${API_BASE}/analytics/dashboard/stats?days=${days}`
  );
  return response.json();
}

export async function getTracesTimeline(days: number = 30): Promise<TracesByDay[]> {
  const response = await fetchWithAuth(
    `${API_BASE}/analytics/dashboard/traces-timeline?days=${days}`
  );
  return response.json();
}

export async function getAgentPerformance(days: number = 7): Promise<AgentPerformance[]> {
  const response = await fetchWithAuth(
    `${API_BASE}/analytics/dashboard/agent-performance?days=${days}`
  );
  return response.json();
}

export async function getCostBreakdown(days: number = 30): Promise<CostBreakdown[]> {
  const response = await fetchWithAuth(
    `${API_BASE}/analytics/dashboard/cost-breakdown?days=${days}`
  );
  return response.json();
}

export async function getRecentActivity(limit: number = 10): Promise<any[]> {
  const response = await fetchWithAuth(
    `${API_BASE}/analytics/dashboard/recent-activity?limit=${limit}`
  );
  return response.json();
}
