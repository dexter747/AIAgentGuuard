'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import {
  Activity, AlertCircle, CheckCircle2, XCircle, ArrowLeft, Settings,
  Loader2, TrendingUp, TrendingDown, Clock, Zap, Bell, BellOff
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface HealthCheck {
  id: string
  status: string
  response_time_ms: number
  error_message: string | null
  checked_at: string
}

interface AgentHealth {
  agent_id: string
  agent_name: string
  current_status: string
  uptime_percentage: number
  average_response_time: number
  last_check_time: string | null
  is_monitored: boolean
  alert_email: string | null
  history: HealthCheck[]
}

export default function AgentHealthDetailPage() {
  const router = useRouter()
  const params = useParams()
  const agentId = params?.agent_id as string

  const [healthData, setHealthData] = useState<AgentHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [alertsEnabled, setAlertsEnabled] = useState(false)
  const [alertEmail, setAlertEmail] = useState('')
  const [showAlertConfig, setShowAlertConfig] = useState(false)
  const [updatingAlerts, setUpdatingAlerts] = useState(false)

  useEffect(() => {
    if (agentId) {
      fetchAgentHealth()
      const interval = setInterval(fetchAgentHealth, 15000) // Refresh every 15s
      return () => clearInterval(interval)
    }
  }, [agentId])

  useEffect(() => {
    if (healthData) {
      setAlertsEnabled(!!healthData.alert_email)
      setAlertEmail(healthData.alert_email || '')
    }
  }, [healthData])

  const fetchAgentHealth = async () => {
    try {
      const [status, history] = await Promise.all([
        apiClient.health.status(agentId),
        apiClient.health.history(agentId, 50)
      ])
      
      setHealthData({
        agent_id: status.agent_id,
        agent_name: status.agent_name,
        current_status: status.current_status,
        uptime_percentage: status.uptime_percentage,
        average_response_time: status.average_response_time,
        last_check_time: status.last_check_time,
        is_monitored: status.is_monitored,
        alert_email: status.alert_email,
        history: history.checks || []
      })
    } catch (error) {
      console.error('Failed to fetch agent health:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateAlerts = async () => {
    try {
      setUpdatingAlerts(true)
      await apiClient.health.updateAlerts(agentId, {
        enabled: alertsEnabled,
        email: alertsEnabled ? alertEmail : null
      })
      await fetchAgentHealth()
      setShowAlertConfig(false)
    } catch (error) {
      console.error('Failed to update alerts:', error)
    } finally {
      setUpdatingAlerts(false)
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
      case 'healthy': return <CheckCircle2 className="h-6 w-6" />
      case 'degraded': return <AlertCircle className="h-6 w-6" />
      case 'unhealthy': return <XCircle className="h-6 w-6" />
      default: return <Clock className="h-6 w-6" />
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </div>
    )
  }

  if (!healthData) {
    return (
      <div className="p-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
        <p className="text-gray-400">Failed to load agent health data</p>
      </div>
    )
  }

  const healthyChecks = healthData.history.filter(c => c.status === 'healthy').length
  const totalChecks = healthData.history.length
  const uptimePercent = totalChecks > 0 ? (healthyChecks / totalChecks * 100).toFixed(1) : '0.0'

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.push('/dashboard/health')}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-medium text-white mb-2">{healthData.agent_name}</h1>
            <div className="flex items-center gap-3">
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium border ${getStatusColor(healthData.current_status)}`}>
                {getStatusIcon(healthData.current_status)}
                {healthData.current_status.toUpperCase()}
              </div>
              {!healthData.is_monitored && (
                <span className="px-3 py-1.5 bg-gray-500/20 text-gray-400 text-sm rounded-lg">
                  Not Monitored
                </span>
              )}
            </div>
          </div>

          <button
            onClick={() => setShowAlertConfig(true)}
            className="px-4 py-2 bg-black border border-white/10 text-white rounded-xl hover:border-purple-500/50 transition-colors flex items-center gap-2"
          >
            {alertsEnabled ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
            Configure Alerts
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Uptime</p>
            <TrendingUp className="h-5 w-5 text-green-400" />
          </div>
          <p className="text-3xl font-medium text-white">{uptimePercent}%</p>
          <p className="text-xs text-gray-500 mt-1">Last {totalChecks} checks</p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Avg Response</p>
            <Zap className="h-5 w-5 text-yellow-400" />
          </div>
          <p className="text-3xl font-medium text-white">
            {healthData.average_response_time?.toFixed(0) || '0'}ms
          </p>
          <p className="text-xs text-gray-500 mt-1">Average latency</p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Total Checks</p>
            <Activity className="h-5 w-5 text-purple-400" />
          </div>
          <p className="text-3xl font-medium text-white">{totalChecks}</p>
          <p className="text-xs text-gray-500 mt-1">{healthyChecks} successful</p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Last Check</p>
            <Clock className="h-5 w-5 text-blue-400" />
          </div>
          <p className="text-sm font-medium text-white">
            {healthData.last_check_time
              ? new Date(healthData.last_check_time).toLocaleString()
              : 'Never'}
          </p>
        </div>
      </div>

      {/* Health History Timeline */}
      <div className="bg-black border border-white/10 rounded-2xl p-6">
        <h2 className="text-xl font-medium text-white mb-4">Health History</h2>
        
        {healthData.history.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No health check history available</p>
        ) : (
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {healthData.history.map(check => (
              <div
                key={check.id}
                className="flex items-start gap-4 p-4 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-colors"
              >
                <div className={`p-2 rounded-lg ${getStatusColor(check.status)}`}>
                  {getStatusIcon(check.status)}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className={`font-medium ${check.status === 'healthy' ? 'text-green-400' : check.status === 'degraded' ? 'text-yellow-400' : 'text-red-400'}`}>
                      {check.status.toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-400">
                      {new Date(check.checked_at).toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-400">
                      Response: <span className="text-white font-medium">{check.response_time_ms}ms</span>
                    </span>
                    
                    {check.error_message && (
                      <span className="text-red-300/70 flex-1">{check.error_message}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Alert Configuration Modal */}
      {showAlertConfig && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-black border border-white/10 rounded-2xl p-6 max-w-md w-full">
            <h3 className="text-xl font-medium text-white mb-4">Alert Configuration</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">Email Alerts</p>
                  <p className="text-sm text-gray-400">Get notified when agent becomes unhealthy</p>
                </div>
                <button
                  onClick={() => setAlertsEnabled(!alertsEnabled)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    alertsEnabled ? 'bg-purple-500' : 'bg-gray-600'
                  }`}
                >
                  <div className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
                    alertsEnabled ? 'translate-x-6' : 'translate-x-0'
                  }`} />
                </button>
              </div>

              {alertsEnabled && (
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Email Address</label>
                  <input
                    type="email"
                    value={alertEmail}
                    onChange={(e) => setAlertEmail(e.target.value)}
                    placeholder="alerts@example.com"
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white focus:border-purple-500/50 focus:outline-none"
                  />
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAlertConfig(false)}
                className="flex-1 px-4 py-2 border border-white/10 text-white rounded-xl hover:bg-white/5 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateAlerts}
                disabled={updatingAlerts || (alertsEnabled && !alertEmail)}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {updatingAlerts ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
