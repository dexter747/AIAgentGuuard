'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Activity, AlertCircle, CheckCircle2, Clock, Loader2 } from "lucide-react"
import { apiClient } from '@/lib/api-client'

export default function TracesPage() {
  const router = useRouter()
  const [traces, setTraces] = useState<any[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const [tracesData, dashboardStats] = await Promise.all([
          apiClient.traces.list(),
          apiClient.dashboard.stats()
        ])
        setTraces(tracesData.traces || tracesData)
        setStats(dashboardStats)
      } catch (error) {
        console.error('Failed to fetch traces:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30s

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-black text-white p-8">
      {loading && (
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 text-violet-500 animate-spin" />
        </div>
      )}

      {!loading && (
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-medium mb-2">Traces</h1>
            <p className="text-gray-400">Monitor your agent execution in real-time</p>
          </div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <StatCard
              icon={<Activity className="w-5 h-5" />}
              title="Total Traces"
              value={stats?.totalTraces?.toLocaleString() || '0'}
              trend="+12%"
            />
            <StatCard
              icon={<CheckCircle2 className="w-5 h-5 text-green-500" />}
              title="Success Rate"
              value={`${stats?.successRate || 0}%`}
              trend="+2.1%"
            />
            <StatCard
              icon={<AlertCircle className="w-5 h-5 text-red-500" />}
              title="Errors"
              value={stats?.totalErrors?.toLocaleString() || '0'}
              trend="-5%"
              positive={true}
            />
            <StatCard
              icon={<Clock className="w-5 h-5" />}
              title="Avg Duration"
              value={`${stats?.avgDuration || 0}s`}
              trend="-0.2s"
              positive={true}
            />
          </div>

          {/* Traces List */}
          <Card className="bg-black border-white/10">
            <CardHeader>
              <CardTitle>Recent Traces</CardTitle>
              <CardDescription className="text-gray-400">
                All agent executions from the last 24 hours
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {traces.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No traces found</p>
                ) : (
                  traces.map((trace) => (
                    <TraceRow 
                      key={trace.id} 
                      trace={trace} 
                      onViewDetails={(id) => router.push(`/dashboard/traces/${id}`)}
                    />
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

function StatCard({ 
  icon, 
  title, 
  value, 
  trend, 
  positive 
}: { 
  icon: React.ReactNode
  title: string
  value: string
  trend: string
  positive?: boolean
}) {
  return (
    <Card className="bg-black border-white/10">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <div className="text-gray-400">{icon}</div>
          <span className={`text-sm ${positive !== false && trend.startsWith('+') ? 'text-green-500' : positive ? 'text-green-500' : 'text-red-500'}`}>
            {trend}
          </span>
        </div>
        <div className="text-2xl font-medium">{value}</div>
        <div className="text-sm text-gray-400">{title}</div>
      </CardContent>
    </Card>
  )
}

function TraceRow({ trace, onViewDetails }: { trace: any, onViewDetails: (id: string) => void }) {
  const isError = trace.status === 'error'
  const agentName = trace.agent_name || trace.agent || 'Unknown Agent'
  const duration = trace.total_duration_ms 
    ? `${(trace.total_duration_ms / 1000).toFixed(2)}s`
    : trace.duration || 'N/A'
  const timestamp = trace.created_at 
    ? new Date(trace.created_at).toLocaleString()
    : trace.timestamp || 'N/A'
  
  return (
    <div 
      className="flex items-center justify-between p-4 border border-white/10 rounded-lg hover:border-violet-500/30 bg-white/5 transition cursor-pointer"
      onClick={() => onViewDetails(trace.id)}
    >
      <div className="flex items-center gap-4 flex-1">
        <div className={`w-2 h-2 rounded-full ${isError ? 'bg-red-500' : 'bg-green-500'}`} />
        
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium">{agentName}</span>
            {isError && (
              <span className="text-xs px-2 py-0.5 bg-red-900/30 text-red-400 rounded">
                Error
              </span>
            )}
            {!isError && trace.confidence && (
              <span className="text-xs px-2 py-0.5 bg-green-900/30 text-green-400 rounded">
                {trace.confidence}% confidence
              </span>
            )}
          </div>
          <div className="text-sm text-gray-400">
            {trace.trace_type || 'trace'} • {duration}
            {trace.error && (
              <span className="text-red-400 ml-2">• {trace.error}</span>
            )}
          </div>
        </div>
        
        <div className="text-sm text-gray-500">{timestamp}</div>
      </div>
      
      <Button 
        variant="ghost" 
        size="sm" 
        className="text-gray-400 hover:text-white"
        onClick={(e) => {
          e.stopPropagation()
          onViewDetails(trace.id)
        }}
      >
        View Details
      </Button>
    </div>
  )
}