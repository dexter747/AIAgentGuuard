'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Bot,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Zap,
  Network,
  Settings,
  Trash2,
  Play,
  Pause,
  ExternalLink,
  ChevronRight,
  BarChart3,
  Loader2
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { apiClient } from '@/lib/api-client'

interface AgentFromAPI {
  id: string
  name: string
  endpoint_url?: string
  health_check_interval: number
  status: string
  created_at: string
  traces_total: number
  traces_today: number
  success_rate: number
  avg_latency: number
}

interface Agent {
  id: string
  name: string
  description: string
  status: 'healthy' | 'degraded' | 'failing' | 'inactive'
  type: 'single' | 'multi' | 'pipeline'
  tracesTotal: number
  tracesToday: number
  successRate: number
  avgLatency: number
  costToday: number
  lastActive: string
  tools: string[]
}

// Transform API response to frontend format
function transformAgent(api: AgentFromAPI): Agent {
  return {
    id: api.id,
    name: api.name,
    description: api.endpoint_url || 'AI Agent',
    status: (api.status as Agent['status']) || 'healthy',
    type: 'single',
    tracesTotal: api.traces_total || 0,
    tracesToday: api.traces_today || 0,
    successRate: api.success_rate || 0,
    avgLatency: api.avg_latency || 0,
    costToday: 0,
    lastActive: api.created_at || new Date().toISOString(),
    tools: []
  }
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.05 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

function getStatusConfig(status: Agent['status']) {
  switch (status) {
    case 'healthy':
      return { color: 'emerald', icon: CheckCircle2, label: 'Healthy' }
    case 'degraded':
      return { color: 'amber', icon: AlertTriangle, label: 'Degraded' }
    case 'failing':
      return { color: 'red', icon: XCircle, label: 'Failing' }
    case 'inactive':
      return { color: 'gray', icon: Clock, label: 'Inactive' }
  }
}

function getTypeConfig(type: Agent['type']) {
  switch (type) {
    case 'single':
      return { icon: Bot, label: 'Single Agent' }
    case 'multi':
      return { icon: Network, label: 'Multi-Agent' }
    case 'pipeline':
      return { icon: Activity, label: 'Pipeline' }
  }
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<Agent['status'] | 'all'>('all')
  const [showRegisterModal, setShowRegisterModal] = useState(false)

  useEffect(() => {
    async function fetchAgents() {
      try {
        setLoading(true)
        const data = await apiClient.agents.list()
        // Transform API response to frontend format
        const transformed = (data || []).map(transformAgent)
        setAgents(transformed)
      } catch (error) {
        console.error('Failed to fetch agents:', error)
        setAgents([])
      } finally {
        setLoading(false)
      }
    }

    fetchAgents()
    const interval = setInterval(fetchAgents, 30000) // Refresh every 30s

    return () => clearInterval(interval)
  }, [])

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || agent.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const stats = {
    total: agents.length,
    healthy: agents.filter(a => a.status === 'healthy').length,
    degraded: agents.filter(a => a.status === 'degraded').length,
    failing: agents.filter(a => a.status === 'failing').length,
  }

  return (
    <div className="min-h-screen p-8 bg-black">
      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 text-violet-500 animate-spin" />
        </div>
      )}

      {!loading && (
        <>
          {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-medium text-white">Agents</h1>
            <p className="text-muted-foreground mt-1">Monitor and manage your AI agents.</p>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/dashboard/agents/graph">
              <Button variant="outline" className="gap-2">
                <Network className="h-4 w-4" />
                View Graph
              </Button>
            </Link>
            <Button className="gap-2" onClick={() => setShowRegisterModal(true)}>
              <Plus className="h-4 w-4" />
              Register Agent
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Stats Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-4 gap-4 mb-8"
      >
        {[
          { label: 'Total Agents', value: stats.total, icon: Bot, color: 'violet' },
          { label: 'Healthy', value: stats.healthy, icon: CheckCircle2, color: 'emerald' },
          { label: 'Degraded', value: stats.degraded, icon: AlertTriangle, color: 'amber' },
          { label: 'Failing', value: stats.failing, icon: XCircle, color: 'red' },
        ].map((stat) => (
          <Card key={stat.label} className="bg-white/5 border-white/10">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className="text-2xl font-medium text-white mt-1">{stat.value}</p>
                </div>
                <div className={cn(
                  "p-2 rounded-lg",
                  stat.color === 'violet' ? 'bg-violet-500/20' :
                  stat.color === 'emerald' ? 'bg-emerald-500/20' :
                  stat.color === 'amber' ? 'bg-amber-500/20' :
                  'bg-red-500/20'
                )}>
                  <stat.icon className={cn(
                    "h-5 w-5",
                    stat.color === 'violet' ? 'text-violet-400' :
                    stat.color === 'emerald' ? 'text-emerald-400' :
                    stat.color === 'amber' ? 'text-amber-400' :
                    'text-red-400'
                  )} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex items-center gap-4 mb-6"
      >
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-white/5 border-white/10"
          />
        </div>
        <div className="flex items-center gap-2">
          {(['all', 'healthy', 'degraded', 'failing', 'inactive'] as const).map((status) => (
            <Button
              key={status}
              variant="outline"
              size="sm"
              onClick={() => setStatusFilter(status)}
              className={cn(
                "capitalize",
                statusFilter === status && "bg-violet-500/20 border-violet-500/50 text-violet-300"
              )}
            >
              {status}
            </Button>
          ))}
        </div>
      </motion.div>

      {/* Agents Grid */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {filteredAgents.map((agent) => {
          const statusConfig = getStatusConfig(agent.status)
          const typeConfig = getTypeConfig(agent.type)
          const StatusIcon = statusConfig.icon
          const TypeIcon = typeConfig.icon

          return (
            <motion.div key={agent.id} variants={item}>
              <Card className="bg-white/5 border-white/10 hover:border-white/20 transition-all group">
                <CardContent className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "p-2 rounded-xl",
                        agent.status === 'healthy' ? 'bg-violet-500/20' :
                        agent.status === 'degraded' ? 'bg-amber-500/20' :
                        agent.status === 'failing' ? 'bg-red-500/20' :
                        'bg-gray-500/20'
                      )}>
                        <Bot className={cn(
                          "h-5 w-5",
                          agent.status === 'healthy' ? 'text-violet-400' :
                          agent.status === 'degraded' ? 'text-amber-400' :
                          agent.status === 'failing' ? 'text-red-400' :
                          'text-gray-400'
                        )} />
                      </div>
                      <div>
                        <h3 className="font-medium text-white group-hover:text-violet-300 transition-colors">
                          {agent.name}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <StatusIcon className={cn(
                            "h-3.5 w-3.5",
                            statusConfig.color === 'emerald' ? 'text-emerald-400' :
                            statusConfig.color === 'amber' ? 'text-amber-400' :
                            statusConfig.color === 'red' ? 'text-red-400' :
                            'text-gray-400'
                          )} />
                          <span className={cn(
                            "text-xs",
                            statusConfig.color === 'emerald' ? 'text-emerald-400' :
                            statusConfig.color === 'amber' ? 'text-amber-400' :
                            statusConfig.color === 'red' ? 'text-red-400' :
                            'text-gray-400'
                          )}>
                            {statusConfig.label}
                          </span>
                          <span className="text-xs text-muted-foreground">•</span>
                          <TypeIcon className="h-3.5 w-3.5 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">{typeConfig.label}</span>
                        </div>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Description */}
                  <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                    {agent.description}
                  </p>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-muted-foreground">Success Rate</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-lg font-medium text-white">{agent.successRate}%</span>
                        {agent.successRate >= 95 ? (
                          <TrendingUp className="h-4 w-4 text-emerald-400" />
                        ) : agent.successRate >= 80 ? (
                          <TrendingDown className="h-4 w-4 text-amber-400" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-red-400" />
                        )}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Avg Latency</p>
                      <p className="text-lg font-medium text-white mt-1">{agent.avgLatency}s</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Traces Today</p>
                      <p className="text-lg font-medium text-white mt-1">{agent.tracesToday.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Cost Today</p>
                      <p className="text-lg font-medium text-white mt-1">${agent.costToday.toFixed(2)}</p>
                    </div>
                  </div>

                  {/* Success Rate Bar */}
                  <div className="mb-4">
                    <Progress 
                      value={agent.successRate} 
                      className="h-2 bg-white/10"
                    />
                  </div>

                  {/* Tools */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {agent.tools.map((tool) => (
                      <Badge key={tool} variant="secondary" className="bg-white/10 text-gray-300 text-xs">
                        {tool}
                      </Badge>
                    ))}
                  </div>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-white/10">
                    <span className="text-xs text-muted-foreground">
                      Last active {agent.lastActive}
                    </span>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="sm" className="h-8 px-2">
                        <BarChart3 className="h-4 w-4" />
                      </Button>
                      <Link href={`/dashboard/traces?agent=${agent.id}`}>
                        <Button variant="ghost" size="sm" className="h-8 px-2">
                          <Activity className="h-4 w-4" />
                        </Button>
                      </Link>
                      <Button variant="ghost" size="sm" className="h-8 gap-1 text-violet-400 hover:text-violet-300">
                        View
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </motion.div>

      {filteredAgents.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Bot className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">No agents found</h3>
          <p className="text-muted-foreground mb-4">
            {searchQuery || statusFilter !== 'all' 
              ? 'Try adjusting your search or filters.'
              : 'Register your first agent to get started.'}
          </p>
          <Button className="gap-2" onClick={() => setShowRegisterModal(true)}>
            <Plus className="h-4 w-4" />
            Register Agent
          </Button>
        </motion.div>
      )}
        </>
      )}

      {/* Register Agent Modal */}
      {showRegisterModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50" onClick={() => setShowRegisterModal(false)}>
          <div className="bg-black rounded-xl shadow-2xl max-w-md w-full mx-4 border border-violet-500/30" onClick={(e) => e.stopPropagation()}>
            <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
              <h2 className="text-lg font-medium text-white">Register New Agent</h2>
              <button onClick={() => setShowRegisterModal(false)} className="p-1 hover:bg-white/10 rounded">
                <Plus className="h-5 w-5 text-gray-400 rotate-45" />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Agent Name</label>
                <input
                  type="text"
                  placeholder="My AI Agent"
                  className="w-full px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 text-white placeholder:text-gray-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Agent Type</label>
                <select className="w-full px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 text-white appearance-none cursor-pointer">
                  <option value="single">Single Agent</option>
                  <option value="multi">Multi-Agent</option>
                  <option value="pipeline">Pipeline</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Description (Optional)</label>
                <textarea
                  placeholder="Brief description of what this agent does..."
                  rows={3}
                  className="w-full px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 text-white placeholder:text-gray-500"
                />
              </div>
              
              <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg p-3">
                <p className="text-xs text-violet-300">
                  💡 After registering, you'll receive an API key to integrate this agent with OverseeX SDK.
                </p>
              </div>
            </div>
            
            <div className="px-6 py-4 border-t border-white/10 flex justify-end gap-3">
              <button
                onClick={() => setShowRegisterModal(false)}
                className="px-4 py-2 border border-white/10 rounded-lg hover:bg-white/5 text-white"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  const nameInput = document.querySelector('input[placeholder="My AI Agent"]') as HTMLInputElement
                  const typeSelect = document.querySelector('select') as HTMLSelectElement
                  const descInput = document.querySelector('textarea') as HTMLTextAreaElement
                  
                  if (!nameInput.value) {
                    alert('Please enter an agent name')
                    return
                  }
                  
                  try {
                    const newAgent = await apiClient.agents.create({
                      name: nameInput.value,
                      type: typeSelect.value,
                      description: descInput.value || undefined,
                      endpoint_url: 'https://your-agent-endpoint.com'
                    })
                    setShowRegisterModal(false)
                    // Refresh agents list
                    const data = await apiClient.agents.list()
                    setAgents(data)
                  } catch (error) {
                    console.error('Failed to register agent:', error)
                    alert('Failed to register agent. Please try again.')
                  }
                }}
                className="px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700"
              >
                Register Agent
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
