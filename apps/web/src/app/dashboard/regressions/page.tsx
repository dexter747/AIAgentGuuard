'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  TrendingDown, AlertCircle, Clock, Filter, Loader2, 
  ChevronRight, Activity, Zap, XCircle
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface Regression {
  id: string
  agent_id: string
  agent_name: string
  metric_type: string
  current_value: number
  baseline_value: number
  change_percent: number
  severity: string
  detected_at: string
  time_window: string
}

export default function RegressionsPage() {
  const router = useRouter()
  const [regressions, setRegressions] = useState<Regression[]>([])
  const [loading, setLoading] = useState(true)
  const [timeWindow, setTimeWindow] = useState('24h')
  const [severityFilter, setSeverityFilter] = useState<string | null>(null)

  useEffect(() => {
    fetchRegressions()
  }, [timeWindow, severityFilter])

  const fetchRegressions = async () => {
    try {
      setLoading(true)
      const data = await apiClient.regressions.list({ 
        time_window: timeWindow,
        ...(severityFilter && { severity: severityFilter })
      })
      setRegressions(data)
    } catch (error) {
      console.error('Failed to fetch regressions:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/20 border-red-500/30'
      case 'high': return 'text-orange-400 bg-orange-500/20 border-orange-500/30'
      case 'medium': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30'
      case 'low': return 'text-blue-400 bg-blue-500/20 border-blue-500/30'
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30'
    }
  }

  const getMetricIcon = (metricType: string) => {
    switch (metricType) {
      case 'success_rate': return <TrendingDown className="h-5 w-5" />
      case 'avg_latency': return <Zap className="h-5 w-5" />
      case 'error_rate': return <XCircle className="h-5 w-5" />
      default: return <Activity className="h-5 w-5" />
    }
  }

  const getMetricLabel = (metricType: string) => {
    switch (metricType) {
      case 'success_rate': return 'Success Rate Dropped'
      case 'avg_latency': return 'Latency Increased'
      case 'error_rate': return 'Error Rate Increased'
      default: return metricType
    }
  }

  const formatValue = (metricType: string, value: number) => {
    if (metricType === 'success_rate' || metricType === 'error_rate') {
      return `${value.toFixed(1)}%`
    }
    return `${value.toFixed(0)}ms`
  }

  const stats = {
    total: regressions.length,
    critical: regressions.filter(r => r.severity === 'critical').length,
    high: regressions.filter(r => r.severity === 'high').length,
    medium: regressions.filter(r => r.severity === 'medium').length
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-xl">
            <AlertCircle className="h-6 w-6 text-red-400" />
          </div>
          <h1 className="text-3xl font-medium text-white">Regression Detection</h1>
        </div>
        <p className="text-gray-400">Performance degradations detected across your agents</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Total Alerts</p>
            <AlertCircle className="h-5 w-5 text-gray-400" />
          </div>
          <p className="text-3xl font-medium text-white">{stats.total}</p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Critical</p>
            <AlertCircle className="h-5 w-5 text-red-400" />
          </div>
          <p className="text-3xl font-medium text-red-400">{stats.critical}</p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">High</p>
            <AlertCircle className="h-5 w-5 text-orange-400" />
          </div>
          <p className="text-3xl font-medium text-orange-400">{stats.high}</p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">Medium</p>
            <AlertCircle className="h-5 w-5 text-yellow-400" />
          </div>
          <p className="text-3xl font-medium text-yellow-400">{stats.medium}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="flex gap-2">
          <button
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
          >
            <Clock className="h-4 w-4 inline mr-1" />
            Time Window:
          </button>
          {['1h', '6h', '24h', '7d'].map(window => (
            <button
              key={window}
              onClick={() => setTimeWindow(window)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                timeWindow === window
                  ? 'bg-purple-500 text-white'
                  : 'bg-black text-gray-400 hover:text-white'
              }`}
            >
              {window}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <button
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
          >
            <Filter className="h-4 w-4 inline mr-1" />
            Severity:
          </button>
          <button
            onClick={() => setSeverityFilter(null)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
              !severityFilter
                ? 'bg-purple-500 text-white'
                : 'bg-black text-gray-400 hover:text-white'
            }`}
          >
            All
          </button>
          {['critical', 'high', 'medium'].map(sev => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors capitalize ${
                severityFilter === sev
                  ? 'bg-purple-500 text-white'
                  : 'bg-black text-gray-400 hover:text-white'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Regressions List */}
      {regressions.length === 0 ? (
        <div className="bg-black border border-white/10 rounded-2xl p-12 text-center">
          <AlertCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
          <h3 className="text-xl font-medium text-white mb-2">No Regressions Detected</h3>
          <p className="text-gray-400">All agents are performing within expected parameters</p>
        </div>
      ) : (
        <div className="space-y-3">
          {regressions.map(regression => (
            <div
              key={regression.id}
              onClick={() => router.push(`/dashboard/regressions/${regression.id}`)}
              className="bg-black border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`p-2 rounded-lg ${getSeverityColor(regression.severity)}`}>
                      {getMetricIcon(regression.metric_type)}
                    </div>
                    <div>
                      <h3 className="text-white font-medium">{regression.agent_name}</h3>
                      <p className="text-sm text-gray-400">{getMetricLabel(regression.metric_type)}</p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-medium border capitalize ${getSeverityColor(regression.severity)}`}>
                      {regression.severity}
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-6 ml-11">
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Baseline</p>
                      <p className="text-sm font-medium text-gray-300">
                        {formatValue(regression.metric_type, regression.baseline_value)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Current</p>
                      <p className="text-sm font-medium text-white">
                        {formatValue(regression.metric_type, regression.current_value)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Change</p>
                      <p className={`text-sm font-medium ${
                        regression.metric_type === 'success_rate' 
                          ? 'text-red-400' 
                          : regression.change_percent > 0 
                          ? 'text-red-400' 
                          : 'text-green-400'
                      }`}>
                        {regression.change_percent > 0 ? '+' : ''}
                        {regression.change_percent.toFixed(1)}%
                      </p>
                    </div>
                  </div>

                  <p className="text-xs text-gray-500 mt-4 ml-11">
                    Detected: {new Date(regression.detected_at).toLocaleString()}
                  </p>
                </div>

                <ChevronRight className="h-5 w-5 text-gray-400" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
