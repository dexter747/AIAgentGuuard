'use client'

import { useState, useEffect } from 'react'
import { AlertTriangle, CheckCircle, Info, TrendingUp, TrendingDown, DollarSign, Zap, RefreshCw, ChevronRight } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface Insight {
  insight_type: 'anomaly' | 'performance' | 'cost' | 'pattern' | 'root_cause' | 'recommendation'
  severity: 'info' | 'warning' | 'critical'
  title: string
  description: string
  affected_agents: string[]
  evidence: Record<string, any>
  recommendation?: string
  created_at: string
}

interface CoordinationIssue {
  issue_type: string
  severity: string
  description: string
  affected_agents: string[]
  evidence: Record<string, any>
  suggested_fix?: string
}

export default function InsightsPage() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [coordinationIssues, setCoordinationIssues] = useState<CoordinationIssue[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState<'insights' | 'coordination'>('insights')
  const [severityFilter, setSeverityFilter] = useState<string>('all')

  useEffect(() => {
    fetchInsights()
  }, [])

  const fetchInsights = async () => {
    try {
      setLoading(true)
      const [insightsData, coordinationData] = await Promise.all([
        apiClient.insights.list().catch(() => []),
        apiClient.insights.coordination().catch(() => [])
      ])
      setInsights(insightsData)
      setCoordinationIssues(coordinationData)
    } catch (error) {
      console.error('Failed to fetch insights:', error)
    } finally {
      setLoading(false)
    }
  }

  const refreshInsights = async () => {
    await fetchInsights()
  }

  const getInsightIcon = (type: Insight['insight_type']) => {
    switch (type) {
      case 'anomaly':
        return <AlertTriangle className="h-5 w-5" />
      case 'performance':
        return <Zap className="h-5 w-5" />
      case 'cost':
        return <DollarSign className="h-5 w-5" />
      case 'pattern':
        return <TrendingUp className="h-5 w-5" />
      default:
        return <Info className="h-5 w-5" />
    }
  }

  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200'
    }
  }

  const getIssueTypeLabel = (type: string) => {
    return type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase())
  }

  const filteredInsights = severityFilter === 'all' 
    ? insights 
    : insights.filter(i => i.severity === severityFilter)

  const criticalCount = insights.filter(i => i.severity === 'critical').length
  const warningCount = insights.filter(i => i.severity === 'warning').length

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="bg-black shadow border-b border-white/10">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-medium tracking-tight text-white">
              AI Insights
            </h1>
            <p className="mt-1 text-sm text-gray-400">
              Intelligent analysis and recommendations for your AI agents
            </p>
          </div>
          <button
            onClick={refreshInsights}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Summary */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-4 mb-8">
          <div className="bg-black rounded-xl shadow p-6 border border-white/10">
            <p className="text-sm font-medium text-gray-400">Total Insights</p>
            <p className="text-3xl font-medium text-white">{insights.length}</p>
          </div>
          <div className="bg-black rounded-xl shadow p-6 border border-white/10">
            <p className="text-sm font-medium text-gray-400">Critical</p>
            <p className="text-3xl font-medium text-red-400">{criticalCount}</p>
          </div>
          <div className="bg-black rounded-xl shadow p-6 border border-white/10">
            <p className="text-sm font-medium text-gray-400">Warnings</p>
            <p className="text-3xl font-medium text-yellow-400">{warningCount}</p>
          </div>
          <div className="bg-black rounded-xl shadow p-6 border border-white/10">
            <p className="text-sm font-medium text-gray-400">Coordination Issues</p>
            <p className="text-3xl font-medium text-purple-400">{coordinationIssues.length}</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-black rounded-xl shadow mb-6 border border-white/10">
          <div className="border-b border-white/10">
            <nav className="flex -mb-px">
              <button
                onClick={() => setSelectedTab('insights')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  selectedTab === 'insights'
                    ? 'border-violet-500 text-violet-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-white/20'
                }`}
              >
                AI Insights ({insights.length})
              </button>
              <button
                onClick={() => setSelectedTab('coordination')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  selectedTab === 'coordination'
                    ? 'border-violet-500 text-violet-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-white/20'
                }`}
              >
                Coordination Issues ({coordinationIssues.length})
              </button>
            </nav>
          </div>

          {/* Filter */}
          <div className="px-6 py-3 bg-black border-b border-white/10 flex items-center gap-4">
            <span className="text-sm text-gray-400">Filter by severity:</span>
            <div className="flex gap-2">
              {['all', 'critical', 'warning', 'info'].map(severity => (
                <button
                  key={severity}
                  onClick={() => setSeverityFilter(severity)}
                  className={`px-3 py-1 text-sm rounded-full transition-colors ${
                    severityFilter === severity
                      ? 'bg-violet-500/20 text-violet-300'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10'
                  }`}
                >
                  {severity.charAt(0).toUpperCase() + severity.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="divide-y divide-white/10">
            {selectedTab === 'insights' ? (
              filteredInsights.length > 0 ? (
                filteredInsights.map((insight, idx) => (
                  <InsightCard key={idx} insight={insight} />
                ))
              ) : (
                <div className="p-12 text-center text-gray-500">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-400" />
                  <p className="text-lg font-medium">No insights found</p>
                  <p className="text-sm">Everything looks good!</p>
                </div>
              )
            ) : (
              coordinationIssues.length > 0 ? (
                coordinationIssues.map((issue, idx) => (
                  <CoordinationIssueCard key={idx} issue={issue} />
                ))
              ) : (
                <div className="p-12 text-center text-gray-500">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-400" />
                  <p className="text-lg font-medium">No coordination issues</p>
                  <p className="text-sm">Your agents are working well together!</p>
                </div>
              )
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

function InsightCard({ insight }: { insight: Insight }) {
  const [expanded, setExpanded] = useState(false)

  const getInsightIcon = (type: Insight['insight_type']) => {
    switch (type) {
      case 'anomaly':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      case 'performance':
        return <Zap className="h-5 w-5 text-yellow-500" />
      case 'cost':
        return <DollarSign className="h-5 w-5 text-green-500" />
      case 'pattern':
        return <TrendingUp className="h-5 w-5 text-blue-500" />
      default:
        return <Info className="h-5 w-5 text-gray-500" />
    }
  }

  const getSeverityBadge = (severity: string) => {
    const styles = {
      critical: 'bg-red-500/20 text-red-400 border-red-500/20',
      warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/20',
      info: 'bg-blue-500/20 text-blue-400 border-blue-500/20'
    }
    return styles[severity as keyof typeof styles] || styles.info
  }

  return (
    <div className="p-6 hover:bg-white/5 transition-colors">
      <div 
        className="flex items-start gap-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-shrink-0 p-2 bg-white/5 rounded-lg">
          {getInsightIcon(insight.insight_type)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1">
            <h3 className="font-medium text-white">{insight.title}</h3>
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getSeverityBadge(insight.severity)}`}>
              {insight.severity}
            </span>
            <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-white/5 text-gray-400">
              {insight.insight_type}
            </span>
          </div>
          <p className="text-gray-400">{insight.description}</p>
          {insight.affected_agents.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {insight.affected_agents.map(agent => (
                <span key={agent} className="px-2 py-0.5 text-xs bg-violet-500/20 text-violet-300 rounded">
                  {agent}
                </span>
              ))}
            </div>
          )}
        </div>
        <ChevronRight className={`h-5 w-5 text-gray-400 transition-transform ${expanded ? 'rotate-90' : ''}`} />
      </div>

      {expanded && (
        <div className="mt-4 ml-14 space-y-4">
          {insight.recommendation && (
            <div className="p-4 bg-violet-500/10 rounded-lg border border-violet-500/20">
              <h4 className="text-sm font-medium text-violet-300 mb-1">Recommendation</h4>
              <p className="text-sm text-violet-200">{insight.recommendation}</p>
            </div>
          )}
          <div className="p-4 bg-black rounded-lg border border-white/10">
            <h4 className="text-sm font-medium text-gray-400 mb-2">Evidence</h4>
            <pre className="text-xs text-gray-300 overflow-x-auto">
              {JSON.stringify(insight.evidence, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}

function CoordinationIssueCard({ issue }: { issue: CoordinationIssue }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="p-6 hover:bg-white/5 transition-colors">
      <div 
        className="flex items-start gap-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-shrink-0 p-2 bg-purple-500/20 rounded-lg">
          <AlertTriangle className="h-5 w-5 text-purple-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1">
            <h3 className="font-medium text-white">
              {issue.issue_type.replace(/_/g, ' ')}
            </h3>
            <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${
              issue.severity === 'critical' ? 'bg-red-500/20 text-red-400 border-red-500/20' : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/20'
            }`}>
              {issue.severity}
            </span>
          </div>
          <p className="text-gray-400">{issue.description}</p>
          <div className="mt-2 flex flex-wrap gap-1">
            {issue.affected_agents.map(agent => (
              <span key={agent} className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-300 rounded">
                {agent}
              </span>
            ))}
          </div>
        </div>
        <ChevronRight className={`h-5 w-5 text-gray-400 transition-transform ${expanded ? 'rotate-90' : ''}`} />
      </div>

      {expanded && (
        <div className="mt-4 ml-14 space-y-4">
          {issue.suggested_fix && (
            <div className="p-4 bg-green-500/10 rounded-lg border border-green-500/20">
              <h4 className="text-sm font-medium text-green-300 mb-1">Suggested Fix</h4>
              <p className="text-sm text-green-200">{issue.suggested_fix}</p>
            </div>
          )}
          <div className="p-4 bg-black rounded-lg border border-white/10">
            <h4 className="text-sm font-medium text-gray-400 mb-2">Evidence</h4>
            <pre className="text-xs text-gray-300 overflow-x-auto">
              {JSON.stringify(issue.evidence, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
