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
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.overseex.com'

export default function AgentGraphPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({ totalAgents: 0, activePaths: 0, totalDuration: '0s' })

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  )

  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        const token = localStorage.getItem('token')
        
        // Fetch agents
        const agentsRes = await fetch(`${API_URL}/api/v1/agents`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        if (!agentsRes.ok) {
          throw new Error('Failed to fetch agents')
        }
        
        const agentsData = await agentsRes.json()
        
        // Fetch recent traces to build graph connections
        const tracesRes = await fetch(`${API_URL}/api/v1/traces?limit=50`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        const tracesData = tracesRes.ok ? await tracesRes.json() : { items: [] }
        
        // Convert agents to nodes
        const agentNodes: Node[] = agentsData.map((agent: any, index: number) => ({
          id: agent.id,
          type: 'default',
          data: { 
            label: (
              <div className="p-2">
                <div className="font-medium text-sm">{agent.name}</div>
                <div className="text-xs text-gray-500">Agent</div>
              </div>
            )
          },
          position: { 
            x: 100 + (index % 3) * 250, 
            y: 100 + Math.floor(index / 3) * 200 
          },
          style: {
            background: '#1f2937',
            color: '#fff',
            border: '1px solid #374151',
            borderRadius: '8px',
            padding: '0'
          }
        }))
        
        // Build edges from trace data (if trace_data contains agent flow info)
        const agentEdges: Edge[] = []
        const agentConnections = new Map<string, Set<string>>()
        
        tracesData.items?.forEach((trace: any) => {
          if (trace.trace_data?.agent_flow) {
            const flow = trace.trace_data.agent_flow
            for (let i = 0; i < flow.length - 1; i++) {
              const key = `${flow[i]}-${flow[i+1]}`
              if (!agentConnections.has(key)) {
                agentConnections.set(key, new Set([trace.id]))
              } else {
                agentConnections.get(key)?.add(trace.id)
              }
            }
          }
        })
        
        agentConnections.forEach((traces, key) => {
          const [source, target] = key.split('-')
          agentEdges.push({
            id: key,
            source,
            target,
            animated: true,
            style: { stroke: '#10b981', strokeWidth: 2 },
            label: `${traces.size} traces`
          })
        })
        
        setNodes(agentNodes)
        setEdges(agentEdges)
        setStats({
          totalAgents: agentNodes.length,
          activePaths: agentEdges.length,
          totalDuration: tracesData.items?.[0]?.total_duration_ms 
            ? `${(tracesData.items[0].total_duration_ms / 1000).toFixed(1)}s`
            : '0s'
        })
        
      } catch (error) {
        console.error('Error fetching graph data:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchGraphData()
  }, [setNodes, setEdges])

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white p-8 flex items-center justify-center">
        <div className="text-gray-400">Loading agent graph...</div>
      </div>
    )
  }

  if (nodes.length === 0) {
    return (
      <div className="min-h-screen bg-black text-white p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-medium mb-2">Multi-Agent Graph</h1>
            <p className="text-gray-400">Visualize agent communication and data flow</p>
          </div>
          <Card className="bg-black border-white/10">
            <CardContent className="p-12 text-center">
              <div className="text-gray-400 mb-4">No agents found</div>
              <p className="text-sm text-gray-500">
                Integrate the OverseeX SDK in your code to start tracking agents
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-medium mb-2">Multi-Agent Graph</h1>
          <p className="text-gray-400">Visualize agent communication and data flow</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Graph Visualization */}
          <div className="lg:col-span-3">
            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle>Agent Execution Flow</CardTitle>
                <CardDescription className="text-gray-400">
                  Interactive graph showing how agents interact
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div style={{ height: '600px' }} className="bg-black rounded-b-lg">
                  <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    onConnect={onConnect}
                    fitView
                  >
                    <Controls />
                    <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#374151" />
                  </ReactFlow>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar Stats */}
          <div className="space-y-6">
            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle>Graph Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="text-sm text-gray-400 mb-1">Total Agents</div>
                  <div className="text-2xl font-medium">{stats.totalAgents}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Active Paths</div>
                  <div className="text-2xl font-medium">{stats.activePaths}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400 mb-1">Avg Duration</div>
                  <div className="text-2xl font-medium">{stats.totalDuration}</div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}