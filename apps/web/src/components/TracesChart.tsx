'use client'

import { useEffect, useState } from 'react'
import { getTracesTimeline } from '@/lib/api/analytics'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface TracesByDay {
  date: string
  count: number
  success_count: number
  error_count: number
}

export function TracesChart({ days = 7 }: { days?: number }) {
  const [data, setData] = useState<TracesByDay[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const timeline = await getTracesTimeline(days)
        setData(timeline)
      } catch (error) {
        console.error('Failed to fetch timeline:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [days])

  if (loading) {
    return (
      <div className="h-80 bg-gray-100 rounded-lg animate-pulse flex items-center justify-center">
        <p className="text-gray-500">Loading chart...</p>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-80 bg-gray-50 rounded-lg flex items-center justify-center">
        <p className="text-gray-500">No trace data available</p>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => {
            const date = new Date(value)
            return `${date.getMonth() + 1}/${date.getDate()}`
          }}
        />
        <YAxis />
        <Tooltip 
          labelFormatter={(value) => {
            const date = new Date(value as string)
            return date.toLocaleDateString()
          }}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="count" 
          stroke="#3b82f6" 
          name="Total Traces"
          strokeWidth={2}
        />
        <Line 
          type="monotone" 
          dataKey="success_count" 
          stroke="#10b981" 
          name="Successful"
          strokeWidth={2}
        />
        <Line 
          type="monotone" 
          dataKey="error_count" 
          stroke="#ef4444" 
          name="Errors"
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
