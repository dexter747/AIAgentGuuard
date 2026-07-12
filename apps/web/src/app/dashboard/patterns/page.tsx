'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Brain,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Activity,
  ArrowRight,
  AlertTriangle,
  GitBranch,
  TrendingUp,
  Filter,
  Search,
  Layers,
  Sparkles,
  Clock,
  BarChart3,
  Zap
} from 'lucide-react'
import { Input } from "@/components/ui/input"

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.overseex.com'

interface LearnedPattern {
  id: string
  org_id: string
  issue_type: string
  pattern_signature: string
  correction_template: string
  success_rate: number
  times_applied: number
  times_approved: number
  times_rejected: number
  is_active: boolean
  created_at: string
  last_applied_at: string | null
}

interface PatternStats {
  total_patterns: number
  active_patterns: number
  total_applications: number
  avg_success_rate: number
  patterns_by_type: Record<string, number>
}

export default function PatternsPage() {
  const [loading, setLoading] = useState(true)
  const [patterns, setPatterns] = useState<LearnedPattern[]>([])
  const [stats, setStats] = useState<PatternStats | null>(null)
  const [activeTab, setActiveTab] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token')
      const headers = { 'Authorization': `Bearer ${token}` }

      // Fetch patterns
      const patternsRes = await fetch(`${API_URL}/api/v1/coordination/patterns?limit=50`, {
        headers
      })

      if (patternsRes.ok) {
        const patternsData = await patternsRes.json()
        setPatterns(patternsData)

        // Calculate stats
        const stats: PatternStats = {
          total_patterns: patternsData.length,
          active_patterns: patternsData.filter((p: LearnedPattern) => p.is_active).length,
          total_applications: patternsData.reduce((sum: number, p: LearnedPattern) => sum + p.times_applied, 0),
          avg_success_rate: patternsData.length > 0
            ? Math.round(patternsData.reduce((sum: number, p: LearnedPattern) => sum + p.success_rate, 0) / patternsData.length)
            : 0,
          patterns_by_type: patternsData.reduce((acc: Record<string, number>, p: LearnedPattern) => {
            acc[p.issue_type] = (acc[p.issue_type] || 0) + 1
            return acc
          }, {})
        }
        setStats(stats)
      }

    } catch (error) {
      console.error('Error fetching patterns:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const deactivatePattern = async (patternId: string) => {
    try {
      const token = localStorage.getItem('token')
      await fetch(`${API_URL}/api/v1/coordination/patterns/${patternId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      // Update local state
      setPatterns(prev => prev.map(p =>
        p.id === patternId ? { ...p, is_active: false } : p
      ))
    } catch (error) {
      console.error('Error deactivating pattern:', error)
    }
  }

  const getIssueTypeIcon = (type: string) => {
    switch (type) {
      case 'state_drift': return <Activity className="h-4 w-4" />
      case 'handoff_failure': return <ArrowRight className="h-4 w-4" />
      case 'broken_assumption': return <AlertTriangle className="h-4 w-4" />
      case 'duplicate_work': return <GitBranch className="h-4 w-4" />
      case 'timeout': return <Clock className="h-4 w-4" />
      default: return <Layers className="h-4 w-4" />
    }
  }

  const getIssueTypeColor = (type: string) => {
    switch (type) {
      case 'state_drift': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'handoff_failure': return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
      case 'broken_assumption': return 'bg-red-500/20 text-red-400 border-red-500/30'
      case 'duplicate_work': return 'bg-purple-500/20 text-purple-400 border-purple-500/30'
      case 'timeout': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 80) return 'text-green-400'
    if (rate >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const filteredPatterns = patterns.filter(pattern => {
    const matchesSearch = searchQuery === '' ||
      pattern.pattern_signature.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pattern.correction_template.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesType = selectedType === null || pattern.issue_type === selectedType

    const matchesTab = activeTab === 'all' ||
      (activeTab === 'active' && pattern.is_active) ||
      (activeTab === 'inactive' && !pattern.is_active)

    return matchesSearch && matchesType && matchesTab
  })

  const issueTypes = [...new Set(patterns.map(p => p.issue_type))]

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading learned patterns...</p>
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
            <h1 className="text-4xl font-medium mb-2">Learned Patterns</h1>
            <p className="text-gray-400">ML patterns learned from your feedback on coordination issues</p>
          </div>
          <Button
            onClick={fetchData}
            variant="outline"
            className="border-white/10"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Card className="bg-black border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Patterns</p>
                    <p className="text-2xl font-medium">{stats.total_patterns}</p>
                  </div>
                  <Brain className="h-8 w-8 text-violet-500/50" />
                </div>
                <div className="mt-2 text-sm text-gray-400">
                  {stats.active_patterns} active
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Applications</p>
                    <p className="text-2xl font-medium">{stats.total_applications}</p>
                  </div>
                  <Zap className="h-8 w-8 text-blue-500/50" />
                </div>
                <div className="mt-2 text-sm text-gray-400">
                  Times patterns were used
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Avg Success Rate</p>
                    <p className={`text-2xl font-medium ${getSuccessRateColor(stats.avg_success_rate)}`}>
                      {stats.avg_success_rate}%
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-500/50" />
                </div>
                <div className="mt-2 text-sm text-gray-400">
                  Based on user feedback
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Pattern Types</p>
                    <p className="text-2xl font-medium">{Object.keys(stats.patterns_by_type).length}</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-orange-500/50" />
                </div>
                <div className="mt-2 text-sm text-gray-400">
                  Different issue categories
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Pattern Type Distribution */}
        {stats && Object.keys(stats.patterns_by_type).length > 0 && (
          <Card className="bg-black border-white/10 mb-8">
            <CardHeader>
              <CardTitle className="text-lg">Patterns by Issue Type</CardTitle>
              <CardDescription className="text-gray-400">
                Distribution of learned patterns across different issue categories
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                {Object.entries(stats.patterns_by_type).map(([type, count]) => (
                  <button
                    key={type}
                    onClick={() => setSelectedType(selectedType === type ? null : type)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                      selectedType === type
                        ? 'bg-violet-500/20 border-violet-500/50'
                        : 'bg-white/5 border-white/10 hover:border-white/20'
                    }`}
                  >
                    {getIssueTypeIcon(type)}
                    <span className="capitalize">{type.replace('_', ' ')}</span>
                    <Badge variant="outline" className="ml-1">{count}</Badge>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Filters and Search */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search patterns..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-white/5 border-white/10"
            />
          </div>
          {selectedType && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSelectedType(null)}
              className="text-gray-400 hover:text-white"
            >
              Clear filter
              <XCircle className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white/5 border border-white/10">
            <TabsTrigger value="all" className="data-[state=active]:bg-violet-600">
              All ({patterns.length})
            </TabsTrigger>
            <TabsTrigger value="active" className="data-[state=active]:bg-violet-600">
              Active ({patterns.filter(p => p.is_active).length})
            </TabsTrigger>
            <TabsTrigger value="inactive" className="data-[state=active]:bg-violet-600">
              Inactive ({patterns.filter(p => !p.is_active).length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab}>
            <div className="space-y-4">
              {filteredPatterns.map((pattern) => (
                <Card key={pattern.id} className="bg-black border-white/10 hover:border-white/20 transition-all">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-lg ${getIssueTypeColor(pattern.issue_type)}`}>
                          {getIssueTypeIcon(pattern.issue_type)}
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <Badge className={getIssueTypeColor(pattern.issue_type)}>
                              {pattern.issue_type.replace('_', ' ')}
                            </Badge>
                            {pattern.is_active ? (
                              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                Active
                              </Badge>
                            ) : (
                              <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">
                                Inactive
                              </Badge>
                            )}
                          </div>
                          <h3 className="font-medium text-lg mb-2">Pattern Signature</h3>
                          <p className="text-gray-300 font-mono text-sm bg-white/5 p-3 rounded-lg">
                            {pattern.pattern_signature}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-medium ${getSuccessRateColor(pattern.success_rate)}`}>
                          {Math.round(pattern.success_rate)}%
                        </div>
                        <div className="text-xs text-gray-400">success rate</div>
                      </div>
                    </div>

                    <div className="mb-4">
                      <h4 className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-violet-400" />
                        Correction Template
                      </h4>
                      <p className="text-gray-300 bg-violet-500/10 border border-violet-500/30 p-3 rounded-lg">
                        {pattern.correction_template}
                      </p>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-white/10">
                      <div className="flex items-center gap-6 text-sm text-gray-400">
                        <span className="flex items-center gap-1">
                          <Zap className="h-4 w-4" />
                          Applied {pattern.times_applied}x
                        </span>
                        <span className="flex items-center gap-1 text-green-400">
                          <CheckCircle2 className="h-4 w-4" />
                          {pattern.times_approved} approved
                        </span>
                        <span className="flex items-center gap-1 text-red-400">
                          <XCircle className="h-4 w-4" />
                          {pattern.times_rejected} rejected
                        </span>
                        {pattern.last_applied_at && (
                          <span className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            Last used {new Date(pattern.last_applied_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>

                      {pattern.is_active && (
                        <Button
                          variant="outline"
                          size="sm"
                          className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                          onClick={() => deactivatePattern(pattern.id)}
                        >
                          Deactivate
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}

              {filteredPatterns.length === 0 && (
                <div className="text-center py-16">
                  <Brain className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                  <h3 className="text-lg font-medium text-gray-300 mb-2">No Patterns Found</h3>
                  <p className="text-gray-400 max-w-md mx-auto">
                    {patterns.length === 0
                      ? "No patterns have been learned yet. Approve or reject suggestions on the Coordination page to help the system learn."
                      : "No patterns match your current filters. Try adjusting your search or filter criteria."}
                  </p>
                  {patterns.length === 0 && (
                    <Button
                      className="mt-6 bg-violet-600 hover:bg-violet-700"
                      onClick={() => window.location.href = '/dashboard/coordination'}
                    >
                      <Sparkles className="h-4 w-4 mr-2" />
                      Go to Coordination
                    </Button>
                  )}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>

        {/* How It Works */}
        <Card className="bg-black border-white/10 mt-8">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Brain className="h-5 w-5 text-violet-400" />
              How Pattern Learning Works
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-violet-500/20 flex items-center justify-center mx-auto mb-3">
                  <AlertTriangle className="h-6 w-6 text-violet-400" />
                </div>
                <h4 className="font-medium mb-1">1. Issue Detected</h4>
                <p className="text-sm text-gray-400">System detects coordination issues in your multi-agent workflows</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center mx-auto mb-3">
                  <Sparkles className="h-6 w-6 text-blue-400" />
                </div>
                <h4 className="font-medium mb-1">2. Suggestion Generated</h4>
                <p className="text-sm text-gray-400">ML generates a corrective suggestion based on the issue context</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-3">
                  <CheckCircle2 className="h-6 w-6 text-green-400" />
                </div>
                <h4 className="font-medium mb-1">3. You Approve/Reject</h4>
                <p className="text-sm text-gray-400">Your feedback helps the system understand what works</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-orange-500/20 flex items-center justify-center mx-auto mb-3">
                  <Brain className="h-6 w-6 text-orange-400" />
                </div>
                <h4 className="font-medium mb-1">4. Pattern Learned</h4>
                <p className="text-sm text-gray-400">System learns from feedback to improve future suggestions</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
