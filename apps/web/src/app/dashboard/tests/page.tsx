'use client'

import { useState, useEffect } from 'react'
import { Play, Pause, Check, X, Clock, ChevronRight, RefreshCw, Plus, Trash2, Settings, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface Test {
  id: string
  name: string
  agent_id: string
  agent_name: string
  status: 'pending' | 'running' | 'passed' | 'failed'
  input: string
  expected_output?: string
  actual_output?: string
  duration_ms?: number
  last_run?: string
  assertions: Assertion[]
}

interface Assertion {
  type: 'contains' | 'equals' | 'regex' | 'json_path' | 'not_empty'
  value: string
  passed?: boolean
}

interface TestRun {
  id: string
  started_at: string
  completed_at?: string
  total_tests: number
  passed: number
  failed: number
  status: 'running' | 'completed'
}

export default function TestsPage() {
  const [tests, setTests] = useState<Test[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTest, setSelectedTest] = useState<Test | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [currentRun, setCurrentRun] = useState<TestRun | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    async function fetchTests() {
      try {
        setLoading(true)
        const data = await apiClient.tests.list()
        setTests(data)
      } catch (error) {
        console.error('Failed to fetch tests:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchTests()
    const interval = setInterval(fetchTests, 30000) // Refresh every 30s

    return () => clearInterval(interval)
  }, [])

  const runAllTests = async () => {
    setIsRunning(true)
    setCurrentRun({
      id: Date.now().toString(),
      started_at: new Date().toISOString(),
      total_tests: tests.length,
      passed: 0,
      failed: 0,
      status: 'running'
    })

    // Simulate running tests
    for (let i = 0; i < tests.length; i++) {
      const test = tests[i]
      setTests(prev => prev.map(t => 
        t.id === test.id ? { ...t, status: 'running' as const } : t
      ))
      
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const passed = Math.random() > 0.3
      setTests(prev => prev.map(t => 
        t.id === test.id 
          ? { 
              ...t, 
              status: passed ? 'passed' as const : 'failed' as const,
              duration_ms: Math.floor(Math.random() * 3000) + 500,
              last_run: new Date().toISOString()
            } 
          : t
      ))

      setCurrentRun(prev => prev ? {
        ...prev,
        passed: prev.passed + (passed ? 1 : 0),
        failed: prev.failed + (passed ? 0 : 1)
      } : null)
    }

    setCurrentRun(prev => prev ? {
      ...prev,
      completed_at: new Date().toISOString(),
      status: 'completed'
    } : null)
    setIsRunning(false)
  }

  const runSingleTest = async (testId: string) => {
    setTests(prev => prev.map(t => 
      t.id === testId ? { ...t, status: 'running' as const } : t
    ))
    
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const passed = Math.random() > 0.3
    setTests(prev => prev.map(t => 
      t.id === testId 
        ? { 
            ...t, 
            status: passed ? 'passed' as const : 'failed' as const,
            duration_ms: Math.floor(Math.random() * 3000) + 500,
            last_run: new Date().toISOString()
          } 
        : t
    ))
  }

  const getStatusIcon = (status: Test['status']) => {
    switch (status) {
      case 'passed':
        return <Check className="h-5 w-5 text-green-500" />
      case 'failed':
        return <X className="h-5 w-5 text-red-500" />
      case 'running':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: Test['status']) => {
    switch (status) {
      case 'passed':
        return 'bg-green-500/10 text-green-400 border-green-500/20'
      case 'failed':
        return 'bg-red-500/10 text-red-400 border-red-500/20'
      case 'running':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
      default:
        return 'bg-white/5 text-gray-400 border-white/10'
    }
  }

  const passedTests = tests.filter(t => t.status === 'passed').length
  const failedTests = tests.filter(t => t.status === 'failed').length
  const passRate = tests.length > 0 ? (passedTests / tests.length) * 100 : 0

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="bg-black border-b border-white/10">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-medium tracking-tight text-white">
              Test Automation
            </h1>
            <p className="mt-1 text-sm text-gray-400">
              Run and monitor automated tests for your AI agents
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors"
            >
              <Plus className="h-5 w-5" />
              New Test
            </button>
            <button
              onClick={runAllTests}
              disabled={isRunning}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isRunning ? (
                <>
                  <RefreshCw className="h-5 w-5 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="h-5 w-5" />
                  Run All Tests
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Summary */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-4 mb-8">
          <div className="bg-black rounded-xl shadow p-6 border border-white/10">
            <p className="text-sm font-medium text-gray-400">Total Tests</p>
            <p className="text-3xl font-medium text-white">{tests.length}</p>
          </div>
          <div className="bg-black rounded-xl shadow p-6 border border-white/10">
            <p className="text-sm font-medium text-gray-400">Passed</p>
            <p className="text-3xl font-medium text-green-400">{passedTests}</p>
          </div>
          <div className="bg-black rounded-xl shadow p-6 border border-white/10">
            <p className="text-sm font-medium text-gray-400">Failed</p>
            <p className="text-3xl font-medium text-red-400">{failedTests}</p>
          </div>
          <div className="bg-black rounded-xl shadow p-6 border border-white/10">
            <p className="text-sm font-medium text-gray-400">Pass Rate</p>
            <p className="text-3xl font-medium text-violet-400">{passRate.toFixed(1)}%</p>
          </div>
        </div>

        {/* Current Run Status */}
        {currentRun && (
          <div className={`mb-6 rounded-xl p-4 ${currentRun.status === 'running' ? 'bg-blue-500/10 border border-blue-500/20' : 'bg-emerald-500/10 border border-emerald-500/20'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {currentRun.status === 'running' ? (
                  <RefreshCw className="h-5 w-5 text-blue-400 animate-spin" />
                ) : (
                  <Check className="h-5 w-5 text-emerald-400" />
                )}
                <div>
                  <p className="font-medium text-white">
                    {currentRun.status === 'running' ? 'Running tests...' : 'Test run completed'}
                  </p>
                  <p className="text-sm text-gray-400">
                    {currentRun.passed} passed, {currentRun.failed} failed of {currentRun.total_tests} tests
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-48 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-emerald-500 transition-all duration-300"
                    style={{ width: `${((currentRun.passed + currentRun.failed) / currentRun.total_tests) * 100}%` }}
                  />
                </div>
                <span className="text-sm text-gray-400">
                  {Math.round(((currentRun.passed + currentRun.failed) / currentRun.total_tests) * 100)}%
                </span>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Test List */}
          <div className="lg:col-span-2">
            <div className="bg-black rounded-xl shadow border border-white/10">
              <div className="px-6 py-4 border-b border-white/10">
                <h2 className="text-lg font-medium text-white">Test Cases ({tests.length})</h2>
              </div>
              <div className="divide-y divide-white/10">
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 text-violet-500 animate-spin" />
                  </div>
                ) : tests.length === 0 ? (
                  <div className="px-6 py-12 text-center">
                    <Clock className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400 mb-4">No tests found</p>
                    <button
                      onClick={() => setShowCreateModal(true)}
                      className="px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700"
                    >
                      Create Your First Test
                    </button>
                  </div>
                ) : tests.map(test => (
                  <div
                    key={test.id}
                    className={`px-6 py-4 cursor-pointer hover:bg-white/5 transition-colors ${selectedTest?.id === test.id ? 'bg-violet-500/10' : ''}`}
                    onClick={() => setSelectedTest(test)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(test.status)}
                        <div>
                          <p className="font-medium text-white">{test.name}</p>
                          <p className="text-sm text-gray-400">{test.agent_name}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full border ${getStatusColor(test.status)}`}>
                          {test.status}
                        </span>
                        {test.duration_ms && (
                          <span className="text-sm text-gray-500">
                            {test.duration_ms}ms
                          </span>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            runSingleTest(test.id)
                          }}
                          className="p-1 hover:bg-white/10 rounded"
                          disabled={test.status === 'running'}
                        >
                          <Play className="h-4 w-4 text-gray-400" />
                        </button>
                        <ChevronRight className="h-5 w-5 text-gray-400" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Test Details */}
          <div className="lg:col-span-1">
            <div className="bg-black rounded-xl shadow sticky top-6 border border-white/10">
              <div className="px-6 py-4 border-b border-white/10">
                <h2 className="text-lg font-medium text-white">Test Details</h2>
              </div>
              {selectedTest ? (
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium text-white">{selectedTest.name}</h3>
                    <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full border ${getStatusColor(selectedTest.status)}`}>
                      {selectedTest.status}
                    </span>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-gray-400">Agent</label>
                      <p className="text-white">{selectedTest.agent_name}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-400">Input</label>
                      <pre className="mt-1 p-3 bg-black rounded-lg text-sm text-gray-300 overflow-x-auto border border-white/10">
                        {selectedTest.input}
                      </pre>
                    </div>
                    
                    {selectedTest.actual_output && (
                      <div>
                        <label className="text-sm font-medium text-gray-400">Output</label>
                        <pre className="mt-1 p-3 bg-black rounded-lg text-sm text-gray-300 overflow-x-auto whitespace-pre-wrap border border-white/10">
                          {selectedTest.actual_output}
                        </pre>
                      </div>
                    )}
                    
                    <div>
                      <label className="text-sm font-medium text-gray-400">Assertions</label>
                      <div className="mt-2 space-y-2">
                        {selectedTest.assertions.map((assertion, idx) => (
                          <div 
                            key={idx}
                            className={`flex items-center gap-2 p-2 rounded ${
                              assertion.passed === true ? 'bg-green-500/10 border border-green-500/20' :
                              assertion.passed === false ? 'bg-red-500/10 border border-red-500/20' :
                              'bg-white/5 border border-white/10'
                            }`}
                          >
                            {assertion.passed === true ? (
                              <Check className="h-4 w-4 text-green-500" />
                            ) : assertion.passed === false ? (
                              <X className="h-4 w-4 text-red-500" />
                            ) : (
                              <Clock className="h-4 w-4 text-gray-400" />
                            )}
                            <span className="text-sm">
                              <span className="font-mono text-violet-400">{assertion.type}</span>
                              {assertion.value && (
                                <span className="text-gray-400">: {assertion.value}</span>
                              )}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {selectedTest.last_run && (
                      <div>
                        <label className="text-sm font-medium text-gray-400">Last Run</label>
                        <p className="text-white">
                          {new Date(selectedTest.last_run).toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-6 flex gap-2">
                    <button
                      onClick={() => runSingleTest(selectedTest.id)}
                      disabled={selectedTest.status === 'running'}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700 disabled:opacity-50"
                    >
                      <Play className="h-4 w-4" />
                      Run Test
                    </button>
                    <button className="p-2 border border-white/10 rounded-lg hover:bg-white/5">
                      <Settings className="h-5 w-5 text-gray-400" />
                    </button>
                    <button className="p-2 border border-white/10 rounded-lg hover:bg-red-500/10 text-red-400">
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-6 text-center text-gray-400">
                  <Clock className="h-12 w-12 mx-auto mb-4 text-gray-600" />
                  <p>Select a test to view details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Create Test Modal */}
      {showCreateModal && (
        <CreateTestModal onClose={() => setShowCreateModal(false)} />
      )}
    </div>
  )
}

function CreateTestModal({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState('')
  const [agentId, setAgentId] = useState('')
  const [input, setInput] = useState('')
  const [assertions, setAssertions] = useState<{type: string, value: string}[]>([
    { type: 'not_empty', value: '' }
  ])
  const [creating, setCreating] = useState(false)
  const [agents, setAgents] = useState<any[]>([])

  useEffect(() => {
    async function fetchAgents() {
      try {
        const data = await apiClient.agents.list()
        setAgents(data)
      } catch (error) {
        console.error('Failed to fetch agents:', error)
      }
    }
    fetchAgents()
  }, [])

  const addAssertion = () => {
    setAssertions([...assertions, { type: 'contains', value: '' }])
  }

  const removeAssertion = (idx: number) => {
    setAssertions(assertions.filter((_, i) => i !== idx))
  }

  const handleSubmit = async () => {
    if (!name || !agentId || !input) return
    
    try {
      setCreating(true)
      await apiClient.tests.create({
        name,
        agent_id: agentId,
        input,
        assertions: assertions.map(a => ({
          type: a.type as any,
          value: a.value
        }))
      })
      onClose()
      // Refresh the page to show new test
      window.location.reload()
    } catch (error) {
      console.error('Failed to create test:', error)
      alert('Failed to create test. Please try again.')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-black rounded-xl shadow-2xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto border border-violet-500/30" onClick={(e) => e.stopPropagation()}>
        <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
          <h2 className="text-lg font-medium text-white">Create New Test</h2>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded">
            <X className="h-5 w-5 text-gray-400" />
          </button>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Test Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Customer Query Response"
              className="w-full px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 text-white placeholder:text-gray-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Agent</label>
            <select
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              className="w-full px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 text-white appearance-none cursor-pointer"
            >
              <option value="">Select an agent</option>
              {agents.map(agent => (
                <option key={agent.id} value={agent.id}>{agent.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Test Input</label>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter the input to send to the agent"
              rows={3}
              className="w-full px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 text-white placeholder:text-gray-500"
            />
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-400">Assertions</label>
              <button
                onClick={addAssertion}
                className="text-sm text-violet-400 hover:text-violet-300"
              >
                + Add Assertion
              </button>
            </div>
            <div className="space-y-2">
              {assertions.map((assertion, idx) => (
                <div key={idx} className="flex gap-2">
                  <select
                    value={assertion.type}
                    onChange={(e) => {
                      const updated = [...assertions]
                      updated[idx].type = e.target.value
                      setAssertions(updated)
                    }}
                    className="px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 text-white appearance-none cursor-pointer"
                  >
                    <option value="contains">contains</option>
                    <option value="equals">equals</option>
                    <option value="regex">regex</option>
                    <option value="json_path">json_path</option>
                    <option value="not_empty">not_empty</option>
                  </select>
                  <input
                    type="text"
                    value={assertion.value}
                    onChange={(e) => {
                      const updated = [...assertions]
                      updated[idx].value = e.target.value
                      setAssertions(updated)
                    }}
                    placeholder="Expected value"
                    className="flex-1 px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 text-white placeholder:text-gray-500"
                  />
                  {assertions.length > 1 && (
                    <button
                      onClick={() => removeAssertion(idx)}
                      className="p-2 text-red-400 hover:bg-red-500/10 rounded"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="px-6 py-4 border-t border-white/10 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-white/10 rounded-lg hover:bg-white/5 text-white"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!name || !agentId || !input || creating}
            className="px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {creating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating...
              </>
            ) : (
              'Create Test'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
