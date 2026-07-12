'use client'

import { useState, useEffect } from 'react'
import { getDashboardStats } from '@/lib/api/analytics'
import { TracesChart } from '@/components/TracesChart'
import { AgentPerformanceChart } from '@/components/AgentPerformanceChart'
import { CostBreakdownChart } from '@/components/CostBreakdownChart'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalTraces: 0,
    successRate: 0,
    totalErrors: 0,
    avgDuration: 0,
    totalCost: 0,
    tracesToday: 0,
    changePercent: { traces: 0, errors: 0, success_rate: 0 }
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await getDashboardStats(7)
        setStats({
          totalTraces: data.total_traces,
          successRate: data.success_rate,
          totalErrors: data.total_errors,
          avgDuration: data.avg_duration,
          totalCost: data.total_cost,
          tracesToday: data.traces_today,
          changePercent: data.change_percent
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-medium tracking-tight text-gray-900">
            Dashboard
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {loading ? (
            <>
              <div className="bg-white rounded-lg shadow p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16"></div>
              </div>
              <div className="bg-white rounded-lg shadow p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16"></div>
              </div>
              <div className="bg-white rounded-lg shadow p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16"></div>
              </div>
              <div className="bg-white rounded-lg shadow p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16"></div>
              </div>
            </>
          ) : (
            <>
              <StatCard 
                title="Total Traces" 
                value={stats.totalTraces}
                change={stats.changePercent.traces}
              />
              <StatCard 
                title="Success Rate" 
                value={`${stats.successRate.toFixed(1)}%`}
                change={stats.changePercent.success_rate}
              />
              <StatCard 
                title="Total Errors" 
                value={stats.totalErrors}
                change={stats.changePercent.errors}
                isNegative
              />
              <StatCard 
                title="Total Cost" 
                value={`$${stats.totalCost.toFixed(2)}`}
              />
            </>
          )}
        </div>

        {/* Traces Timeline Chart */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-medium mb-4">Traces Timeline (Last 7 Days)</h2>
          <TracesChart days={7} />
        </div>

        {/* Performance Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-medium mb-4">Agent Performance</h2>
            <AgentPerformanceChart days={7} />
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-medium mb-4">Cost Breakdown by Agent</h2>
            <CostBreakdownChart days={7} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-medium mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              View Traces
            </button>
            <button className="px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
              Run Tests
            </button>
            <button className="px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
              Generate API Key
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-medium mb-4">Recent Activity</h2>
          <div className="space-y-3">
            <ActivityItem 
              text="New trace received from n8n workflow"
              time="2 minutes ago"
              type="trace"
            />
            <ActivityItem 
              text="Test suite completed - 12/12 passed"
              time="15 minutes ago"
              type="success"
            />
            <ActivityItem 
              text="Health check warning on Agent #3"
              time="1 hour ago"
              type="warning"
            />
          </div>
        </div>
      </main>
    </div>
  )
}

function StatCard({ 
  title, 
  value, 
  change,
  isNegative = false
}: { 
  title: string; 
  value: number | string;
  change?: number;
  isNegative?: boolean;
}) {
  const showChange = change !== undefined && Math.abs(change) > 0.1;
  const isPositive = isNegative ? (change ?? 0) < 0 : (change ?? 0) > 0;
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <div className="mt-2 flex items-baseline justify-between">
        <p className="text-3xl font-medium text-gray-900">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        {showChange && (
          <span className={`text-sm font-medium ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            {change > 0 ? '+' : ''}{change.toFixed(1)}%
          </span>
        )}
      </div>
    </div>
  )
}

function ActivityItem({ text, time, type }: { text: string; time: string; type: string }) {
  const colors = {
    trace: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800'
  }

  return (
    <div className="flex items-center justify-between py-3 border-b last:border-0">
      <div className="flex items-center gap-3">
        <span className={`px-2 py-1 text-xs font-medium rounded ${colors[type as keyof typeof colors]}`}>
          {type.toUpperCase()}
        </span>
        <span className="text-gray-700">{text}</span>
      </div>
      <span className="text-sm text-gray-500">{time}</span>
    </div>
  )
}
