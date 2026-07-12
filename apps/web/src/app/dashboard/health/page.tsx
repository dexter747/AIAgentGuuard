'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Activity, AlertCircle, CheckCircle2, XCircle, Clock, 
  TrendingUp, TrendingDown, RefreshCw, Plus, Loader2, Zap
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface AgentStatus {
  agent_id: string
  agent_name: string
  current_status: string
  uptime_24h: number
  avg_response_time_ms: number
  is_monitored: boolean
  last_check: string | null
  consecutive_failures: number
  total_checks_24h: number
}

interface DashboardData {
  overview: {
    total_agents: number
    monitored_agents: number
    healthy_agents: number
    degraded_agents: number
    unhealthy_agents: number
    avg_uptime_24h: number
    avg_response_time_ms: number
  }
  agents: AgentStatus[]
  recent_alerts: Array<{
    id: string
    agent_id: string
    agent_name: string
    status: string
    error_message: string
    checked_at: string
    response_time_ms: number
  }>
}

export default function HealthDashboardPage() {
  const router = useRouter()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboard()
    const interval = setInterval(fetchDashboard, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const fetchDashboard = async () => {
    try {
      if (!loading) setRefreshing(true)
      setError(null)
      const data = await apiClient.health.dashboard()
      setDashboardData(data)
    } catch (error: any) {
      console.error('Failed to fetch dashboard:', error)
      setError(error?.message || 'Failed to load health monitoring data')
      // Set empty dashboard data on error so page still renders
      setDashboardData({
        overview: {
          total_agents: 0,
          monitored_agents: 0,
          healthy_agents: 0,
          degraded_agents: 0,
          unhealthy_agents: 0,
          avg_uptime_24h: 0,
          avg_response_time_ms: 0
        },
        agents: [],
        recent_alerts: []
      })
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400 bg-green-500/20 border-green-500/30'
      case 'degraded': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30'
      case 'unhealthy': return 'text-red-400 bg-red-500/20 border-red-500/30'
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle2 className="h-5 w-5" />
      case 'degraded': return <AlertCircle className="h-5 w-5" />
      case 'unhealthy': return <XCircle className="h-5 w-5" />
      default: return <Clock className="h-5 w-5" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="p-8 text-center">
        <Activity className="h-12 w-12 text-gray-600 mx-auto mb-4" />
        <h2 className="text-xl font-medium text-white mb-2">Health Monitoring</h2>
        <p className="text-gray-400 mb-4">No agents registered for health monitoring yet.</p>
        <a 
          href="/dashboard/agents" 
          className="inline-flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg transition-colors"
        >
          <Plus className="h-4 w-4" />
          Register an Agent
        </a>
      </div>
    )
  }

  const { overview, agents, recent_alerts } = dashboardData

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-to-br from-green-500/20 to-emerald-500/20 rounded-xl">
                <Activity className="h-6 w-6 text-green-400" />
              </div>
              <h1 className="text-3xl font-medium text-white">Health Monitoring</h1>
            </div>
            <p className="text-gray-400">Real-time status of your AI agents</p>
          </div>
          <button
            onClick={fetchDashboard}
            disabled={refreshing}
            className="px-4 py-2 bg-black border border-white/10 text-white rounded-xl hover:border-purple-500/50 transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Healthy Agents</p>
            <CheckCircle2 className="h-5 w-5 text-green-400" />
          </div>
          <p className="text-3xl font-medium text-green-400">{overview.healthy_agents}</p>
          <p className="text-xs text-gray-500 mt-1">
            {overview.total_agents} total
          </p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Avg Uptime (24h)</p>
            <TrendingUp className="h-5 w-5 text-purple-400" />
          </div>
          <p className="text-3xl font-medium text-white">{overview.avg_uptime_24h.toFixed(1)}%</p>
          <p className="text-xs text-gray-500 mt-1">
            {overview.monitored_agents} monitored
          </p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Avg Response</p>
            <Zap className="h-5 w-5 text-yellow-400" />
          </div>
          <p className="text-3xl font-medium text-white">{overview.avg_response_time_ms.toFixed(0)}ms</p>
          <p className="text-xs text-gray-500 mt-1">
            Last 24 hours
          </p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Issues</p>
            <AlertCircle className="h-5 w-5 text-red-400" />
          </div>
          <p className="text-3xl font-medium text-red-400">
            {overview.degraded_agents + overview.unhealthy_agents}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {overview.degraded_agents} degraded, {overview.unhealthy_agents} unhealthy
          </p>
        </div>
      </div>

      {/* Agent Status Grid */}
      <div className="mb-6">
        <h2 className="text-xl font-medium text-white mb-4">Agent Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map(agent => (
            <div
              key={agent.agent_id}
              onClick={() => router.push(`/dashboard/health/${agent.agent_id}`)}
              className="bg-black border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-white font-medium mb-1">{agent.agent_name}</h3>
                  <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(agent.current_status)}`}>
                    {getStatusIcon(agent.current_status)}
                    {agent.current_status.toUpperCase()}
                  </div>
                </div>
                {!agent.is_monitored && (
                  <span className="px-2 py-1 bg-gray-500/20 text-gray-400 text-xs rounded-lg">
                    Not Monitored
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-400">Uptime (24h)</p>
                  <p className="text-white font-medium">{agent.uptime_24h.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-gray-400">Avg Response</p>
                  <p className="text-white font-medium">{agent.avg_response_time_ms.toFixed(0)}ms</p>
                </div>
                <div>
                  <p className="text-gray-400">Checks (24h)</p>
                  <p className="text-white font-medium">{agent.total_checks_24h}</p>
                </div>
                <div>
                  <p className="text-gray-400">Failures</p>
                  <p className={`font-medium ${agent.consecutive_failures > 0 ? 'text-red-400' : 'text-gray-500'}`}>
                    {agent.consecutive_failures}
                  </p>
                </div>
              </div>

              {agent.last_check && (
                <p className="text-xs text-gray-500 mt-4">
                  Last checked: {new Date(agent.last_check).toLocaleString()}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Alerts */}
      {recent_alerts.length > 0 && (
        <div>
          <h2 className="text-xl font-medium text-white mb-4">Recent Alerts</h2>
          <div className="bg-black border border-white/10 rounded-2xl overflow-hidden">
            <div className="divide-y divide-white/10">
              {recent_alerts.map(alert => (
                <div key={alert.id} className="p-4 hover:bg-white/5 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className={`p-1.5 rounded-lg ${getStatusColor(alert.status)}`}>
                          {getStatusIcon(alert.status)}
                        </div>
                        <div>
                          <h4 className="text-white font-medium">{alert.agent_name}</h4>
                          <p className="text-sm text-gray-400">
                            {new Date(alert.checked_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      {alert.error_message && (
                        <p className="text-sm text-red-300/70 ml-11">{alert.error_message}</p>
                      )}
                    </div>
                    {alert.response_time_ms && (
                      <span className="text-sm text-gray-400">{alert.response_time_ms}ms</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
