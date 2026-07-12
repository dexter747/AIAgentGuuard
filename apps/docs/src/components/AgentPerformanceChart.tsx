'use client'

import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getAgentPerformance } from '@/lib/api/analytics'

interface AgentPerformanceChartProps {
  days?: number
}

export function AgentPerformanceChart({ days = 7 }: AgentPerformanceChartProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await getAgentPerformance(days)
        setData(result)
      } catch (error) {
        console.error('Failed to fetch agent performance:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [days])

  if (loading) {
    return (
      <div className="h-80 bg-gray-100 rounded animate-pulse flex items-center justify-center">
        <span className="text-gray-500">Loading chart...</span>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="h-80 flex items-center justify-center text-gray-500">
        No agent performance data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="agent_name" />
        <YAxis yAxisId="left" />
        <YAxis yAxisId="right" orientation="right" />
        <Tooltip />
        <Legend />
        <Bar yAxisId="left" dataKey="trace_count" fill="#3b82f6" name="Trace Count" />
        <Bar yAxisId="right" dataKey="avg_duration" fill="#10b981" name="Avg Duration (ms)" />
        <Bar yAxisId="left" dataKey="error_count" fill="#ef4444" name="Errors" />
      </BarChart>
    </ResponsiveContainer>
  )
}
