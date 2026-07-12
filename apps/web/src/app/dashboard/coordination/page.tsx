'use client'

import { useState, useEffect, useCallback } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  BackgroundVariant,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RefreshCw,
  Sparkles,
  Activity,
  GitBranch,
  Clock,
  TrendingUp,
  Filter,
  ThumbsUp,
  ThumbsDown
} from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.overseex.com'

interface CoordinationIssue {
  id: string
  issue_type: string
  severity: string
  title: string
  description: string
  affected_agents: string[]
  suggested_fix: string | null
  user_feedback: string
  is_resolved: boolean
  detected_at: string
}

interface Suggestion {
  id: string
  issue_id: string
  correction_strategy: string
  description: string
  confidence: number
  status: string
}

interface GraphData {
  nodes: any[]
  edges: any[]
}

interface Metrics {
  total_issues: number
  critical_issues: number
  high_issues: number
  resolved_issues: number
  resolution_rate: number
  total_handoffs: number
  handoff_success_rate: number
  suggestions_generated: number
  suggestion_approval_rate: number
  issues_by_type: Record<string, number>
}

// Custom node for agents
const AgentNode = ({ data }: { data: any }) => (
  <div className={`px-4 py-3 rounded-lg border ${
    data.status === 'healthy' ? 'border-green-500/50 bg-green-500/10' :
    data.status === 'warning' ? 'border-yellow-500/50 bg-yellow-500/10' :
    'border-red-500/50 bg-red-500/10'
  }`}>
    <div className="font-medium text-sm text-white">{data.label}</div>
    <div className="text-xs text-gray-400 mt-1">
      {data.trace_count} traces | {data.issue_count} issues
    </div>
  </div>
)

const nodeTypes = {
  agent: AgentNode,
}

export default function CoordinationPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [issues, setIssues] = useState<CoordinationIssue[]>([])
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [selectedIssue, setSelectedIssue] = useState<CoordinationIssue | null>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [analyzing, setAnalyzing] = useState(false)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  )

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token')
      const headers = { 'Authorization': `Bearer ${token}` }

      // Fetch coordination graph
      const graphRes = await fetch(`${API_URL}/api/v1/coordination/graph?time_window_hours=24`, {
        headers
      })

      if (graphRes.ok) {
        const graphData: GraphData = await graphRes.json()

        // Convert to ReactFlow format
        const flowNodes: Node[] = graphData.nodes.map((node, index) => ({
          id: node.id,
          type: 'agent',
          data: {
            label: node.label,
            trace_count: node.trace_count,
            issue_count: node.issue_count,
            status: node.status,
          },
          position: {
            x: 150 + (index % 4) * 250,
            y: 100 + Math.floor(index / 4) * 200,
          },
        }))

        const flowEdges: Edge[] = graphData.edges.map((edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          animated: edge.status !== 'error',
          style: {
            stroke: edge.status === 'success' ? '#10b981' :
                    edge.status === 'warning' ? '#f59e0b' : '#ef4444',
            strokeWidth: 2,
          },
          label: `${edge.success_rate}%`,
          labelStyle: { fill: '#9ca3af', fontSize: 10 },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: edge.status === 'success' ? '#10b981' :
                   edge.status === 'warning' ? '#f59e0b' : '#ef4444',
          },
        }))

        setNodes(flowNodes)
        setEdges(flowEdges)
      }

      // Fetch issues
      const issuesRes = await fetch(`${API_URL}/api/v1/coordination/issues?limit=20`, {
        headers
      })

      if (issuesRes.ok) {
        const issuesData = await issuesRes.json()
        setIssues(issuesData)
      }

      // Fetch suggestions
      const suggestionsRes = await fetch(`${API_URL}/api/v1/coordination/suggestions?status=pending&limit=10`, {
        headers
      })

      if (suggestionsRes.ok) {
        const suggestionsData = await suggestionsRes.json()
        setSuggestions(suggestionsData)
      }

      // Fetch metrics
      const metricsRes = await fetch(`${API_URL}/api/v1/coordination/metrics?time_window_hours=24`, {
        headers
      })

      if (metricsRes.ok) {
        const metricsData = await metricsRes.json()
        setMetrics(metricsData)
      }

    } catch (error) {
      console.error('Error fetching coordination data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const runAnalysis = async () => {
    setAnalyzing(true)
    try {
      const token = localStorage.getItem('token')
      await fetch(`${API_URL}/api/v1/coordination/analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ time_window_hours: 24 })
      })

      // Refresh data after analysis
      await fetchData()
    } catch (error) {
      console.error('Error running analysis:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  const provideFeedback = async (suggestionId: string, status: 'approved' | 'rejected') => {
    try {
      const token = localStorage.getItem('token')
      await fetch(`${API_URL}/api/v1/coordination/suggestions/${suggestionId}/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      })

      // Remove from list
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId))
    } catch (error) {
      console.error('Error providing feedback:', error)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30'
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      default: return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    }
  }

  const getIssueTypeIcon = (type: string) => {
    switch (type) {
      case 'state_drift': return <Activity className="h-4 w-4" />
      case 'handoff_failure': return <ArrowRight className="h-4 w-4" />
      case 'broken_assumption': return <AlertTriangle className="h-4 w-4" />
      case 'duplicate_work': return <GitBranch className="h-4 w-4" />
      default: return <XCircle className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading coordination data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-medium mb-2">Coordination Intelligence</h1>
            <p className="text-gray-400">Multi-agent coordination analysis and corrective suggestions</p>
          </div>
          <Button
            onClick={runAnalysis}
            disabled={analyzing}
            className="bg-violet-600 hover:bg-violet-700"
          >
            {analyzing ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4 mr-2" />
            )}
            {analyzing ? 'Analyzing...' : 'Run Analysis'}
          </Button>
        </div>

        {/* Metrics Cards */}
        {metrics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Card className="bg-black border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Issues</p>
                    <p className="text-2xl font-medium">{metrics.total_issues}</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-yellow-500/50" />
                </div>
                <div className="mt-2 flex items-center text-sm">
                  <span className="text-red-400">{metrics.critical_issues} critical</span>
                  <span className="mx-2 text-gray-600">|</span>
                  <span className="text-orange-400">{metrics.high_issues} high</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Resolution Rate</p>
                    <p className="text-2xl font-medium">{metrics.resolution_rate}%</p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-green-500/50" />
                </div>
                <div className="mt-2 text-sm text-gray-400">
                  {metrics.resolved_issues} resolved
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Handoff Success</p>
                    <p className="text-2xl font-medium">{metrics.handoff_success_rate}%</p>
                  </div>
                  <ArrowRight className="h-8 w-8 text-blue-500/50" />
                </div>
                <div className="mt-2 text-sm text-gray-400">
                  {metrics.total_handoffs} total handoffs
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Suggestions</p>
                    <p className="text-2xl font-medium">{metrics.suggestions_generated}</p>
                  </div>
                  <Sparkles className="h-8 w-8 text-violet-500/50" />
                </div>
                <div className="mt-2 text-sm text-gray-400">
                  {metrics.suggestion_approval_rate}% approval rate
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white/5 border border-white/10">
            <TabsTrigger value="overview" className="data-[state=active]:bg-violet-600">
              Overview
            </TabsTrigger>
            <TabsTrigger value="issues" className="data-[state=active]:bg-violet-600">
              Issues ({issues.length})
            </TabsTrigger>
            <TabsTrigger value="suggestions" className="data-[state=active]:bg-violet-600">
              Suggestions ({suggestions.length})
            </TabsTrigger>
            <TabsTrigger value="graph" className="data-[state=active]:bg-violet-600">
              Graph
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Recent Issues */}
              <Card className="bg-black border-white/10">
                <CardHeader>
                  <CardTitle className="text-lg">Recent Issues</CardTitle>
                  <CardDescription className="text-gray-400">
                    Latest detected coordination issues
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {issues.slice(0, 5).map((issue) => (
                    <div
                      key={issue.id}
                      className="p-3 rounded-lg bg-white/5 border border-white/10 hover:border-white/20 cursor-pointer transition-all"
                      onClick={() => setSelectedIssue(issue)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          {getIssueTypeIcon(issue.issue_type)}
                          <span className="text-sm font-medium">{issue.title}</span>
                        </div>
                        <Badge className={getSeverityColor(issue.severity)}>
                          {issue.severity}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-400 mt-2 line-clamp-2">
                        {issue.description}
                      </p>
                    </div>
                  ))}
                  {issues.length === 0 && (
                    <div className="text-center py-8 text-gray-400">
                      No issues detected. Run analysis to check for coordination problems.
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Pending Suggestions */}
              <Card className="bg-black border-white/10">
                <CardHeader>
                  <CardTitle className="text-lg">Pending Suggestions</CardTitle>
                  <CardDescription className="text-gray-400">
                    ML-powered fixes awaiting your approval
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {suggestions.slice(0, 5).map((suggestion) => (
                    <div
                      key={suggestion.id}
                      className="p-3 rounded-lg bg-white/5 border border-white/10"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <Badge variant="outline" className="text-violet-400 border-violet-400/30 mb-2">
                            {suggestion.correction_strategy}
                          </Badge>
                          <p className="text-sm">{suggestion.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-400">
                          {Math.round(suggestion.confidence * 100)}% confidence
                        </span>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 text-green-400 hover:text-green-300 hover:bg-green-500/10"
                            onClick={() => provideFeedback(suggestion.id, 'approved')}
                          >
                            <ThumbsUp className="h-3 w-3 mr-1" />
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-7 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                            onClick={() => provideFeedback(suggestion.id, 'rejected')}
                          >
                            <ThumbsDown className="h-3 w-3 mr-1" />
                            Reject
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                  {suggestions.length === 0 && (
                    <div className="text-center py-8 text-gray-400">
                      No pending suggestions. Approve or reject suggestions to help the system learn.
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Issues Tab */}
          <TabsContent value="issues">
            <Card className="bg-black border-white/10">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Coordination Issues</CardTitle>
                    <CardDescription className="text-gray-400">
                      All detected issues across your multi-agent system
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm" className="border-white/10">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {issues.map((issue) => (
                    <div
                      key={issue.id}
                      className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-white/20 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${getSeverityColor(issue.severity)}`}>
                            {getIssueTypeIcon(issue.issue_type)}
                          </div>
                          <div>
                            <h3 className="font-medium">{issue.title}</h3>
                            <p className="text-sm text-gray-400">
                              {issue.issue_type.replace('_', ' ')} | Detected {new Date(issue.detected_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={getSeverityColor(issue.severity)}>
                            {issue.severity}
                          </Badge>
                          {issue.is_resolved && (
                            <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                              Resolved
                            </Badge>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-300 mb-3">{issue.description}</p>
                      {issue.affected_agents && issue.affected_agents.length > 0 && (
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-xs text-gray-400">Affected:</span>
                          {issue.affected_agents.map((agent, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {agent}
                            </Badge>
                          ))}
                        </div>
                      )}
                      {issue.suggested_fix && (
                        <div className="p-3 rounded-lg bg-violet-500/10 border border-violet-500/30">
                          <div className="flex items-center gap-2 mb-1">
                            <Sparkles className="h-4 w-4 text-violet-400" />
                            <span className="text-sm font-medium text-violet-400">Suggested Fix</span>
                          </div>
                          <p className="text-sm text-gray-300">{issue.suggested_fix}</p>
                        </div>
                      )}
                    </div>
                  ))}
                  {issues.length === 0 && (
                    <div className="text-center py-12 text-gray-400">
                      <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No coordination issues detected</p>
                      <p className="text-sm mt-2">Run analysis to check for problems in your multi-agent system</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Suggestions Tab */}
          <TabsContent value="suggestions">
            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle>Corrective Suggestions</CardTitle>
                <CardDescription className="text-gray-400">
                  AI-generated fixes for coordination issues. Your feedback helps improve suggestions.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {suggestions.map((suggestion) => (
                    <div
                      key={suggestion.id}
                      className="p-4 rounded-lg bg-white/5 border border-white/10"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <Badge className="bg-violet-500/20 text-violet-400 border-violet-500/30 mb-2">
                            {suggestion.correction_strategy.replace('_', ' ')}
                          </Badge>
                          <h3 className="font-medium">{suggestion.description}</h3>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-400 mb-1">Confidence</div>
                          <div className="text-lg font-medium text-violet-400">
                            {Math.round(suggestion.confidence * 100)}%
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
                        <Button
                          variant="outline"
                          className="border-green-500/30 text-green-400 hover:bg-green-500/10"
                          onClick={() => provideFeedback(suggestion.id, 'approved')}
                        >
                          <ThumbsUp className="h-4 w-4 mr-2" />
                          Approve & Learn
                        </Button>
                        <Button
                          variant="outline"
                          className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                          onClick={() => provideFeedback(suggestion.id, 'rejected')}
                        >
                          <ThumbsDown className="h-4 w-4 mr-2" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  ))}
                  {suggestions.length === 0 && (
                    <div className="text-center py-12 text-gray-400">
                      <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No pending suggestions</p>
                      <p className="text-sm mt-2">When issues are detected, AI will suggest corrections here</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Graph Tab */}
          <TabsContent value="graph">
            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle>Coordination Graph</CardTitle>
                <CardDescription className="text-gray-400">
                  Visual representation of agent handoffs and coordination flow
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div style={{ height: '600px' }} className="bg-black rounded-b-lg">
                  {nodes.length > 0 ? (
                    <ReactFlow
                      nodes={nodes}
                      edges={edges}
                      onNodesChange={onNodesChange}
                      onEdgesChange={onEdgesChange}
                      onConnect={onConnect}
                      nodeTypes={nodeTypes}
                      fitView
                    >
                      <Controls />
                      <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#374151" />
                    </ReactFlow>
                  ) : (
                    <div className="h-full flex items-center justify-center text-gray-400">
                      <div className="text-center">
                        <GitBranch className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>No agent coordination data available</p>
                        <p className="text-sm mt-2">Start sending traces to visualize agent interactions</p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Legend */}
            <div className="mt-4 flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-gray-400">Healthy (90%+ success)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span className="text-gray-400">Warning (70-90% success)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-gray-400">Error (&lt;70% success)</span>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
