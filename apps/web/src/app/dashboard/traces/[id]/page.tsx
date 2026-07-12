'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowRight, CheckCircle2, XCircle, AlertCircle, Clock, Sparkles, TrendingDown, ArrowLeft, Loader2 } from "lucide-react"
import { apiClient } from '@/lib/api-client'

interface TraceDetail {
  id: string
  agent_id: string
  agent_name?: string
  session_id?: string
  trace_type?: string
  input_data?: any
  output_data?: any
  trace_data?: any
  status: string
  total_duration_ms?: number
  cost_usd?: number
  created_at: string
}

export default function TraceDetailPage() {
  const params = useParams()
  const router = useRouter()
  const traceId = params.id as string
  
  const [trace, setTrace] = useState<TraceDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchTrace() {
      if (!traceId) return
      
      try {
        setLoading(true)
        setError(null)
        const data = await apiClient.traces.get(traceId)
        setTrace(data)
      } catch (err: any) {
        console.error('Failed to fetch trace:', err)
        setError(err?.message || 'Failed to load trace')
      } finally {
        setLoading(false)
      }
    }

    fetchTrace()
  }, [traceId])

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white p-8 flex items-center justify-center">
        <Loader2 className="h-8 w-8 text-violet-500 animate-spin" />
      </div>
    )
  }

  if (error || !trace) {
    return (
      <div className="min-h-screen bg-black text-white p-8">
        <div className="max-w-7xl mx-auto">
          <Button variant="ghost" onClick={() => router.push('/dashboard/traces')} className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to traces
          </Button>
          <Card className="bg-black border-white/10">
            <CardContent className="p-12 text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-medium mb-2">Failed to load trace</h2>
              <p className="text-gray-400">{error || 'Trace not found'}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const totalDuration = trace.total_duration_ms ? (trace.total_duration_ms / 1000).toFixed(2) : '0'
  const totalCost = trace.cost_usd ? parseFloat(trace.cost_usd.toString()) : 0

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <Button variant="ghost" size="sm" onClick={() => router.push('/dashboard/traces')}>
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to traces
            </Button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-medium mb-2">Trace Details</h1>
              <p className="text-gray-400 font-mono text-sm">{trace.id}</p>
            </div>
            <Badge className={trace.status === 'success' ? 'bg-green-600' : 'bg-red-600'}>
              {trace.status}
            </Badge>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle>Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4">
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Duration</div>
                    <div className="text-2xl font-medium">{totalDuration}s</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Agent</div>
                    <div className="text-lg font-medium truncate">{trace.agent_name || 'Unknown'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Type</div>
                    <div className="text-lg font-medium">{trace.trace_type || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-1">Cost</div>
                    <div className="text-2xl font-medium">${totalCost.toFixed(4)}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle>Input & Output</CardTitle>
                <CardDescription className="text-gray-400">
                  Data sent to and received from the agent
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-950 border border-gray-800 rounded p-4">
                    <div className="text-xs text-gray-500 mb-2 font-medium">Input</div>
                    <pre className="text-xs text-gray-300 overflow-auto max-h-64">
                      {JSON.stringify(trace.input_data || trace.trace_data?.input || {}, null, 2)}
                    </pre>
                  </div>
                  <div className="bg-gray-950 border border-gray-800 rounded p-4">
                    <div className="text-xs text-gray-500 mb-2 font-medium">Output</div>
                    <pre className="text-xs text-gray-300 overflow-auto max-h-64">
                      {JSON.stringify(trace.output_data || trace.trace_data?.output || {}, null, 2)}
                    </pre>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle>Raw Trace Data</CardTitle>
                <CardDescription className="text-gray-400">
                  Complete trace data captured by the SDK
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-950 border border-gray-800 rounded p-4">
                  <pre className="text-xs text-gray-300 overflow-auto max-h-96">
                    {JSON.stringify(trace.trace_data || {}, null, 2)}
                  </pre>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle>Metadata</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Created</span>
                  <span className="font-mono">
                    {new Date(trace.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Agent ID</span>
                  <span className="font-mono text-xs truncate max-w-[150px]">{trace.agent_id}</span>
                </div>
                {trace.session_id && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Session ID</span>
                    <span className="font-mono text-xs truncate max-w-[150px]">{trace.session_id}</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {trace.status === 'error' && (
              <Card className="bg-black border-white/10">
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    <CardTitle>Error Details</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-red-400">
                    {trace.trace_data?.error || 'An error occurred during execution'}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
