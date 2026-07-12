'use client'

import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getCostBreakdown } from '@/lib/api/analytics'

interface CostBreakdownChartProps {
  days?: number
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export function CostBreakdownChart({ days = 7 }: CostBreakdownChartProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      try {
        const result = await getCostBreakdown(days)
        // Transform data for pie chart
        const chartData = result.map((item: any) => ({
          name: item.agent_name,
          value: parseFloat(item.total_cost),
          tokens: item.total_tokens
        }))
        setData(chartData)
      } catch (error) {
        console.error('Failed to fetch cost breakdown:', error)
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
        No cost data available
      </div>
    )
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 shadow-lg rounded border">
          <p className="font-medium">{payload[0].name}</p>
          <p className="text-sm text-gray-600">Cost: ${payload[0].value.toFixed(4)}</p>
          <p className="text-sm text-gray-600">Tokens: {payload[0].payload.tokens.toLocaleString()}</p>
        </div>
      )
    }
    return null
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
