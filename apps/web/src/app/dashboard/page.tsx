'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Activity,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  DollarSign,
  Zap,
  Clock,
  ArrowUpRight,
  MoreHorizontal,
  Sparkles,
  Bot,
  CheckCircle2,
  Network,
  Lightbulb,
  AlertTriangle
} from 'lucide-react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { apiClient } from '@/lib/api-client'
import { NoticePopup } from '@/components/NoticePopup'

interface Stats {
  totalTraces: number
  successRate: number
  totalErrors: number
  avgDuration: number
  totalCost: number
  tracesToday: number
  changePercent: { traces: number; errors: number; success_rate: number }
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

interface CoordinationSummary {
  openIssues: number
  criticalIssues: number
  pendingSuggestions: number
  handoffSuccessRate: number
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [recentTraces, setRecentTraces] = useState<any[]>([])
  const [topAgents, setTopAgents] = useState<any[]>([])
  const [coordinationSummary, setCoordinationSummary] = useState<CoordinationSummary | null>(null)

  const handleGenerateReport = async () => {
    const reportData = {
      title: 'OverseeX Dashboard Report',
      date: new Date().toISOString(),
      dateFormatted: new Date().toLocaleDateString(),
      stats: stats,
      summary: {
        totalTraces: stats?.totalTraces || 0,
        successRate: stats?.successRate || 0,
        totalErrors: stats?.totalErrors || 0,
        avgDuration: stats?.avgDuration || 0,
        totalCost: stats?.totalCost || 0
      }
    }

    // Prompt user for format
    const format = confirm('Generate as PDF? (Cancel for JSON)') ? 'pdf' : 'json'
    
    if (format === 'json') {
      // Generate JSON
      const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `overseex-report-${Date.now()}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } else {
      // Generate PDF using HTML to PDF approach
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>OverseeX Report</title>
          <style>
            body { font-family: Arial, sans-serif; padding: 40px; background: #000; color: #fff; }
            h1 { color: #8b5cf6; margin-bottom: 10px; }
            .header { margin-bottom: 30px; border-bottom: 2px solid #8b5cf6; padding-bottom: 20px; }
            .stat { background: #1a1a1a; padding: 20px; margin: 10px 0; border-radius: 8px; }
            .stat-label { color: #9ca3af; font-size: 14px; }
            .stat-value { font-size: 24px; font-weight: bold; color: #fff; margin-top: 5px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>OverseeX Dashboard Report</h1>
            <p>Generated: ${reportData.dateFormatted}</p>
          </div>
          <div class="stat">
            <div class="stat-label">Total Traces</div>
            <div class="stat-value">${reportData.summary.totalTraces.toLocaleString()}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Success Rate</div>
            <div class="stat-value">${reportData.summary.successRate}%</div>
          </div>
          <div class="stat">
            <div class="stat-label">Total Errors</div>
            <div class="stat-value">${reportData.summary.totalErrors.toLocaleString()}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Average Duration</div>
            <div class="stat-value">${reportData.summary.avgDuration}s</div>
          </div>
          <div class="stat">
            <div class="stat-label">Total Cost</div>
            <div class="stat-value">$${reportData.summary.totalCost.toFixed(2)}</div>
          </div>
        </body>
        </html>
      `
      
      // Open in new window for print
      const printWindow = window.open('', '_blank')
      if (printWindow) {
        printWindow.document.write(htmlContent)
        printWindow.document.close()
        setTimeout(() => {
          printWindow.print()
        }, 500)
      }
    }
  }

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [statsData, tracesData, agentsData] = await Promise.all([
          apiClient.dashboard.stats(),
          apiClient.traces.list({ limit: 5 }),
          apiClient.agents.list()
        ])
        setStats(statsData)
        setRecentTraces(tracesData.traces || [])
        setTopAgents(agentsData.slice(0, 5))

        // Fetch coordination summary (fail gracefully)
        try {
          const [issues, suggestions, metrics] = await Promise.all([
            apiClient.coordination.listIssues({ status: 'open', limit: 100 }),
            apiClient.coordination.listSuggestions({ status: 'pending', limit: 100 }),
            apiClient.coordination.getMetrics({ days: 7 })
          ])
          setCoordinationSummary({
            openIssues: Array.isArray(issues) ? issues.length : 0,
            criticalIssues: Array.isArray(issues) ? issues.filter((i: any) => i.severity === 'critical').length : 0,
            pendingSuggestions: Array.isArray(suggestions) ? suggestions.length : 0,
            handoffSuccessRate: metrics?.handoff_success_rate || 0
          })
        } catch (coordErr) {
          console.log('Coordination data not available')
        }
      } catch (err: any) {
        setError(err.message)
        console.error('Failed to fetch dashboard data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black p-8">
      {/* Notice Popup */}
      <NoticePopup />
      
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-medium text-white">Dashboard</h1>
            <p className="text-muted-foreground mt-1">Welcome back! Here's what's happening with your agents.</p>
          </div>
          <Button className="gap-2" onClick={handleGenerateReport}>
            <Sparkles className="h-4 w-4" />
            Generate Report
          </Button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div 
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        <motion.div variants={item}>
          <StatsCard
            title="Total Traces"
            value={(stats?.totalTraces || 0).toLocaleString()}
            change={stats?.changePercent?.traces}
            icon={Activity}
            color="violet"
          />
        </motion.div>
        <motion.div variants={item}>
          <StatsCard
            title="Success Rate"
            value={`${stats?.successRate || 0}%`}
            change={stats?.changePercent?.success_rate}
            icon={CheckCircle2}
            color="emerald"
          />
        </motion.div>
        <motion.div variants={item}>
          <StatsCard
            title="Total Errors"
            value={(stats?.totalErrors || 0).toLocaleString()}
            change={stats?.changePercent?.errors}
            icon={AlertCircle}
            color="rose"
            isNegativeGood
          />
        </motion.div>
        <motion.div variants={item}>
          <StatsCard
            title="Total Cost"
            value={`$${stats?.totalCost?.toFixed(2) || '0.00'}`}
            icon={DollarSign}
            color="amber"
          />
        </motion.div>
      </motion.div>

      {/* Coordination Intelligence Summary */}
      {coordinationSummary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="mb-8"
        >
          <Link href="/dashboard/coordination">
            <Card className="bg-gradient-to-r from-violet-500/10 to-purple-500/10 border-violet-500/20 hover:border-violet-500/40 transition-all cursor-pointer group">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-violet-500/20">
                      <Network className="h-6 w-6 text-violet-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-white flex items-center gap-2">
                        Coordination Intelligence
                        <Sparkles className="h-4 w-4 text-violet-400" />
                      </h3>
                      <p className="text-sm text-gray-400">Multi-agent coordination analysis</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-8">
                    <div className="text-center">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className={cn(
                          "h-4 w-4",
                          coordinationSummary.criticalIssues > 0 ? "text-red-400" : "text-gray-500"
                        )} />
                        <span className={cn(
                          "text-2xl font-medium",
                          coordinationSummary.criticalIssues > 0 ? "text-red-400" : "text-white"
                        )}>
                          {coordinationSummary.openIssues}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">Open Issues</p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-amber-400" />
                        <span className="text-2xl font-medium text-white">
                          {coordinationSummary.pendingSuggestions}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">Suggestions</p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                        <span className="text-2xl font-medium text-white">
                          {Math.round(coordinationSummary.handoffSuccessRate * 100)}%
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">Handoff Success</p>
                    </div>
                    <ArrowUpRight className="h-5 w-5 text-gray-500 group-hover:text-violet-400 transition-colors" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Section */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Trace Activity</CardTitle>
                <CardDescription>Your agent activity over the last 7 days</CardDescription>
              </div>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] flex items-end justify-between gap-2 pt-4">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => {
                  const height = [65, 78, 55, 89, 72, 45, 82][i]
                  return (
                    <div key={day} className="flex-1 flex flex-col items-center gap-2">
                      <motion.div 
                        initial={{ height: 0 }}
                        animate={{ height: `${height}%` }}
                        transition={{ delay: 0.5 + i * 0.1, duration: 0.5 }}
                        className="w-full bg-gradient-to-t from-violet-500 to-purple-400 rounded-t-lg relative group cursor-pointer"
                      >
                        <div className="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 bg-secondary rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                          {Math.round(height * 20)} traces
                        </div>
                      </motion.div>
                      <span className="text-xs text-muted-foreground">{day}</span>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Performance</CardTitle>
              <CardDescription>Real-time metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Avg. Response Time</span>
                  <span className="text-white font-medium">{stats?.avgDuration || 0}s</span>
                </div>
                <Progress value={(stats?.avgDuration || 0) * 20} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Success Rate</span>
                  <span className="text-white font-medium">{stats?.successRate || 0}%</span>
                </div>
                <Progress value={stats?.successRate || 0} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">API Usage</span>
                  <span className="text-white font-medium">67%</span>
                </div>
                <Progress value={67} />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted-foreground">Daily Quota</span>
                  <span className="text-white font-medium">45%</span>
                </div>
                <Progress value={45} />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Activity & Top Agents */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest trace executions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentTraces.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No recent traces</p>
                  </div>
                ) : recentTraces.map((trace, i) => (
                  <motion.div 
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.7 + i * 0.1 }}
                    className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "p-2 rounded-lg",
                        trace.status === 'success' ? 'bg-emerald-500/20' : 'bg-rose-500/20'
                      )}>
                        <Bot className={cn(
                          "h-4 w-4",
                          trace.status === 'success' ? 'text-emerald-400' : 'text-rose-400'
                        )} />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{trace.agent_name || 'Agent'}</p>
                        <p className="text-xs text-muted-foreground">{new Date(trace.created_at).toLocaleTimeString()}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-muted-foreground">{trace.duration_ms ? `${(trace.duration_ms / 1000).toFixed(1)}s` : 'N/A'}</span>
                      <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Top Agents</CardTitle>
              <CardDescription>Most active agents this week</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topAgents.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Bot className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No agents registered</p>
                  </div>
                ) : topAgents.map((agent, i) => (
                  <motion.div 
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 + i * 0.1 }}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 text-white text-sm font-medium">
                        {i + 1}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{agent.name}</p>
                        <p className="text-xs text-muted-foreground">Active agent</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-violet-400">{agent.type || 'single'}</p>
                      <p className="text-xs text-muted-foreground">type</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

function StatsCard({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  color,
  isNegativeGood = false
}: { 
  title: string
  value: string
  change?: number
  icon: React.ElementType
  color: 'violet' | 'emerald' | 'rose' | 'amber'
  isNegativeGood?: boolean
}) {
  const colors = {
    violet: 'from-violet-500 to-purple-600',
    emerald: 'from-emerald-500 to-green-600',
    rose: 'from-rose-500 to-red-600',
    amber: 'from-amber-500 to-orange-600'
  }

  const iconBg = {
    violet: 'bg-violet-500/20 text-violet-400',
    emerald: 'bg-emerald-500/20 text-emerald-400',
    rose: 'bg-rose-500/20 text-rose-400',
    amber: 'bg-amber-500/20 text-amber-400'
  }

  const isPositive = change !== undefined && (isNegativeGood ? change < 0 : change > 0)

  return (
    <Card className="relative overflow-hidden group hover:border-violet-500/30 transition-colors">
      <div className={cn(
        "absolute top-0 right-0 w-32 h-32 bg-gradient-to-br opacity-10 blur-2xl transition-opacity group-hover:opacity-20",
        colors[color]
      )} />
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className={cn("p-3 rounded-xl", iconBg[color])}>
            <Icon className="h-5 w-5" />
          </div>
          {change !== undefined && (
            <div className={cn(
              "flex items-center gap-1 text-sm font-medium",
              isPositive ? "text-emerald-400" : "text-rose-400"
            )}>
              {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
              {Math.abs(change)}%
            </div>
          )}
        </div>
        <div className="mt-4">
          <p className="text-3xl font-medium text-white">{value}</p>
          <p className="text-sm text-muted-foreground mt-1">{title}</p>
        </div>
      </CardContent>
    </Card>
  )
}
