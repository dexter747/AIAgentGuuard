'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import {
  ArrowLeft, AlertCircle, TrendingDown, Zap, XCircle,
  Loader2, Activity, Clock
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface RegressionDetail {
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
  hourly_data: Array<{
    hour: string
    total_traces: number
    success_rate: number
    avg_latency: number
    error_count: number
  }>
  sample_failures: Array<{
    trace_id: string
    error_message: string
    timestamp: string
    duration_ms: number
  }>
}

export default function RegressionDetailPage() {
  const router = useRouter()
  const params = useParams()
  const regressionId = params?.regression_id as string

  const [regression, setRegression] = useState<RegressionDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (regressionId) {
      fetchRegressionDetail()
    }
  }, [regressionId])

  const fetchRegressionDetail = async () => {
    try {
      const data = await apiClient.regressions.get(regressionId)
      setRegression(data)
    } catch (error) {
      console.error('Failed to fetch regression detail:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/20 border-red-500/30'
      case 'high': return 'text-orange-400 bg-orange-500/20 border-orange-500/30'
      case 'medium': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30'
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30'
    }
  }

  const getMetricLabel = (metricType: string) => {
    switch (metricType) {
      case 'success_rate': return 'Success Rate'
      case 'avg_latency': return 'Average Latency'
      case 'error_rate': return 'Error Rate'
      default: return metricType
    }
  }

  const formatValue = (metricType: string, value: number) => {
    if (metricType === 'success_rate' || metricType === 'error_rate') {
      return `${value.toFixed(1)}%`
    }
    return `${value.toFixed(0)}ms`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
      </div>
    )
  }

  if (!regression) {
    return (
      <div className="p-8 text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
        <p className="text-gray-400">Failed to load regression details</p>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.push('/dashboard/regressions')}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Regressions
        </button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-medium text-white mb-2">{regression.agent_name}</h1>
            <div className="flex items-center gap-3">
              <p className="text-gray-400">{getMetricLabel(regression.metric_type)} Regression</p>
              <div className={`px-4 py-1.5 rounded-xl text-sm font-medium border capitalize ${getSeverityColor(regression.severity)}`}>
                {regression.severity} Severity
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metric Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <p className="text-gray-400 text-sm mb-2">Baseline Value</p>
          <p className="text-3xl font-medium text-gray-300">
            {formatValue(regression.metric_type, regression.baseline_value)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Previous period</p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <p className="text-gray-400 text-sm mb-2">Current Value</p>
          <p className="text-3xl font-medium text-red-400">
            {formatValue(regression.metric_type, regression.current_value)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Last {regression.time_window}</p>
        </div>

        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <p className="text-gray-400 text-sm mb-2">Change</p>
          <p className="text-3xl font-medium text-red-400">
            {regression.change_percent > 0 ? '+' : ''}
            {regression.change_percent.toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {regression.metric_type === 'success_rate' ? 'Decrease' : 'Increase'}
          </p>
        </div>
      </div>

      {/* Hourly Trend Chart */}
      <div className="bg-black border border-white/10 rounded-2xl p-6 mb-8">
        <h2 className="text-xl font-medium text-white mb-4">24-Hour Trend</h2>
        
        <div className="relative">
          {/* Simple bar chart visualization */}
          <div className="flex items-end justify-between h-48 gap-1">
            {regression.hourly_data.map((hour, idx) => {
              const value = regression.metric_type === 'success_rate' 
                ? hour.success_rate 
                : regression.metric_type === 'avg_latency'
                ? hour.avg_latency / 10  // Scale down for visualization
                : hour.error_count * 10
              
              const maxValue = Math.max(
                ...regression.hourly_data.map(h => 
                  regression.metric_type === 'success_rate' 
                    ? h.success_rate 
                    : regression.metric_type === 'avg_latency'
                    ? h.avg_latency / 10
                    : h.error_count * 10
                )
              )
              
              const heightPercent = maxValue > 0 ? (value / maxValue * 100) : 0

              return (
                <div key={idx} className="flex-1 flex flex-col items-center group">
                  <div className="w-full relative">
                    <div
                      className={`w-full rounded-t transition-all ${
                        hour.total_traces === 0 
                          ? 'bg-gray-700/30' 
                          : regression.metric_type === 'success_rate' && hour.success_rate < 80
                          ? 'bg-red-500/50 hover:bg-red-500/70'
                          : regression.metric_type === 'avg_latency' && hour.avg_latency > 500
                          ? 'bg-orange-500/50 hover:bg-orange-500/70'
                          : 'bg-purple-500/50 hover:bg-purple-500/70'
                      }`}
                      style={{ height: `${heightPercent}%` }}
                    />
                  </div>
                  
                  {/* Tooltip on hover */}
                  <div className="opacity-0 group-hover:opacity-100 absolute bottom-full mb-2 px-2 py-1 bg-black/90 text-white text-xs rounded whitespace-nowrap pointer-events-none transition-opacity">
                    {new Date(hour.hour).getHours()}:00
                    <br />
                    {regression.metric_type === 'success_rate' && `${hour.success_rate.toFixed(1)}%`}
                    {regression.metric_type === 'avg_latency' && `${hour.avg_latency.toFixed(0)}ms`}
                    {regression.metric_type === 'error_rate' && `${hour.error_count} errors`}
                  </div>
                </div>
              )
            })}
          </div>
          
          {/* X-axis labels */}
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>24h ago</span>
            <span>12h ago</span>
            <span>Now</span>
          </div>
        </div>
      </div>

      {/* Sample Failures */}
      {regression.sample_failures.length > 0 && (
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-medium text-white mb-4">Recent Failures</h2>
          
          <div className="space-y-3">
            {regression.sample_failures.map(failure => (
              <div
                key={failure.trace_id}
                className="p-4 bg-white/5 rounded-xl border border-white/5"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <XCircle className="h-4 w-4 text-red-400" />
                    <span className="text-xs text-gray-400 font-mono">{failure.trace_id}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(failure.timestamp).toLocaleString()}
                  </span>
                </div>
                
                <p className="text-sm text-red-300/70 mb-2">{failure.error_message}</p>
                
                {failure.duration_ms && (
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <Clock className="h-3 w-3" />
                    {failure.duration_ms}ms
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detection Info */}
      <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/30 rounded-xl">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-blue-400 mt-0.5" />
          <div>
            <p className="text-sm text-blue-200">
              This regression was detected by comparing the last {regression.time_window} of performance 
              against the previous {regression.time_window} baseline.
            </p>
            <p className="text-xs text-blue-300/70 mt-1">
              Detected at: {new Date(regression.detected_at).toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
