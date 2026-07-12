'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  Boxes, Plus, Trash2, Power, PowerOff, History, Download, 
  Loader2, Search, Filter, Sparkles, CheckCircle2, XCircle 
} from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface Mock {
  tool_name: string
  is_active: boolean
  response_data: any
  call_count: number
  created_at: string
  last_called?: string
}

interface CallHistory {
  timestamp: string
  input_data: any
  output_data: any
  success: boolean
}

export default function MocksPage() {
  const router = useRouter()
  const [mocks, setMocks] = useState<Mock[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterActive, setFilterActive] = useState<boolean | null>(null)
  const [selectedMock, setSelectedMock] = useState<string | null>(null)
  const [callHistory, setCallHistory] = useState<CallHistory[]>([])
  const [showHistory, setShowHistory] = useState(false)

  useEffect(() => {
    fetchMocks()
  }, [])

  const fetchMocks = async () => {
    try {
      setLoading(true)
      const data = await apiClient.mocks.list()
      setMocks(data.mocks || [])
    } catch (error) {
      console.error('Failed to fetch mocks:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleMock = async (toolName: string, currentStatus: boolean) => {
    try {
      await apiClient.mocks.toggle(toolName)
      setMocks(prev => prev.map(m => 
        m.tool_name === toolName ? { ...m, is_active: !currentStatus } : m
      ))
    } catch (error) {
      console.error('Failed to toggle mock:', error)
    }
  }

  const deleteMock = async (toolName: string) => {
    if (!confirm(`Delete mock "${toolName}"?`)) return

    try {
      await apiClient.mocks.delete(toolName)
      setMocks(prev => prev.filter(m => m.tool_name !== toolName))
    } catch (error) {
      console.error('Failed to delete mock:', error)
    }
  }

  const viewHistory = async (toolName: string) => {
    try {
      setSelectedMock(toolName)
      setShowHistory(true)
      const data = await apiClient.mocks.history(toolName)
      setCallHistory(data.history || [])
    } catch (error) {
      console.error('Failed to fetch history:', error)
    }
  }

  const resetAllMocks = async () => {
    if (!confirm('Reset all mocks? This will clear call history.')) return

    try {
      await apiClient.mocks.reset()
      fetchMocks()
    } catch (error) {
      console.error('Failed to reset mocks:', error)
    }
  }

  const filteredMocks = mocks.filter(mock => {
    const matchesSearch = mock.tool_name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterActive === null || mock.is_active === filterActive
    return matchesSearch && matchesFilter
  })

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl">
                <Boxes className="h-6 w-6 text-purple-400" />
              </div>
              <h1 className="text-3xl font-medium text-white">Mock Management</h1>
            </div>
            <p className="text-gray-400">Manage and monitor API mocks for testing</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push('/dashboard/mocks/prebuilt')}
              className="px-4 py-2 bg-black border border-white/10 text-white rounded-xl hover:border-purple-500/50 transition-colors flex items-center gap-2"
            >
              <Sparkles className="h-4 w-4" />
              Pre-built Mocks
            </button>
            <button
              onClick={() => router.push('/dashboard/mocks/create')}
              className="px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-purple-500/50 transition-all flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Create Mock
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search mocks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-black border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setFilterActive(null)}
              className={`px-4 py-3 rounded-xl font-medium transition-all ${
                filterActive === null
                  ? 'bg-gradient-to-r from-violet-500 to-purple-600 text-white'
                  : 'bg-black border border-white/10 text-gray-400'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterActive(true)}
              className={`px-4 py-3 rounded-xl font-medium transition-all ${
                filterActive === true
                  ? 'bg-gradient-to-r from-violet-500 to-purple-600 text-white'
                  : 'bg-black border border-white/10 text-gray-400'
              }`}
            >
              Active
            </button>
            <button
              onClick={() => setFilterActive(false)}
              className={`px-4 py-3 rounded-xl font-medium transition-all ${
                filterActive === false
                  ? 'bg-gradient-to-r from-violet-500 to-purple-600 text-white'
                  : 'bg-black border border-white/10 text-gray-400'
              }`}
            >
              Inactive
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-black border border-white/10 rounded-2xl p-4">
          <p className="text-gray-400 text-sm mb-1">Total Mocks</p>
          <p className="text-2xl font-medium text-white">{mocks.length}</p>
        </div>
        <div className="bg-black border border-white/10 rounded-2xl p-4">
          <p className="text-gray-400 text-sm mb-1">Active</p>
          <p className="text-2xl font-medium text-green-400">{mocks.filter(m => m.is_active).length}</p>
        </div>
        <div className="bg-black border border-white/10 rounded-2xl p-4">
          <p className="text-gray-400 text-sm mb-1">Total Calls</p>
          <p className="text-2xl font-medium text-purple-400">{mocks.reduce((sum, m) => sum + m.call_count, 0)}</p>
        </div>
        <div className="bg-black border border-white/10 rounded-2xl p-4 flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm mb-1">Actions</p>
            <button
              onClick={resetAllMocks}
              className="text-red-400 text-sm hover:text-red-300 transition-colors"
            >
              Reset All
            </button>
          </div>
        </div>
      </div>

      {/* Mocks List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
        </div>
      ) : filteredMocks.length === 0 ? (
        <div className="bg-black border border-white/10 rounded-2xl p-12 text-center">
          <Boxes className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400 mb-4">
            {searchTerm ? 'No mocks match your search' : 'No mocks created yet'}
          </p>
          <button
            onClick={() => router.push('/dashboard/mocks/create')}
            className="px-6 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-xl hover:shadow-lg hover:shadow-purple-500/50 transition-all inline-flex items-center gap-2"
          >
            <Plus className="h-5 w-5" />
            Create Your First Mock
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredMocks.map(mock => (
            <div
              key={mock.tool_name}
              className="bg-black border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-medium text-white">{mock.tool_name}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      mock.is_active
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-gray-500/20 text-gray-400'
                    }`}>
                      {mock.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-400">Calls</p>
                      <p className="text-white font-medium">{mock.call_count}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Created</p>
                      <p className="text-white font-medium">
                        {new Date(mock.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400">Last Called</p>
                      <p className="text-white font-medium">
                        {mock.last_called ? new Date(mock.last_called).toLocaleDateString() : 'Never'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => viewHistory(mock.tool_name)}
                    className="p-2 bg-[#0a0a0f] border border-white/10 rounded-lg text-gray-300 hover:border-purple-500/50 hover:text-white transition-colors"
                    title="View History"
                  >
                    <History className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => toggleMock(mock.tool_name, mock.is_active)}
                    className={`p-2 bg-[#0a0a0f] border border-white/10 rounded-lg transition-colors ${
                      mock.is_active
                        ? 'text-green-400 hover:border-green-500/50'
                        : 'text-gray-400 hover:border-gray-500/50'
                    }`}
                    title={mock.is_active ? 'Deactivate' : 'Activate'}
                  >
                    {mock.is_active ? <Power className="h-5 w-5" /> : <PowerOff className="h-5 w-5" />}
                  </button>
                  <button
                    onClick={() => deleteMock(mock.tool_name)}
                    className="p-2 bg-[#0a0a0f] border border-white/10 rounded-lg text-red-400 hover:border-red-500/50 transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* History Modal */}
      {showHistory && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-black border border-white/10 rounded-2xl p-6 max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-medium text-white">Call History: {selectedMock}</h2>
              <button
                onClick={() => setShowHistory(false)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <XCircle className="h-6 w-6 text-gray-400" />
              </button>
            </div>

            {callHistory.length === 0 ? (
              <div className="text-center py-12">
                <History className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No calls recorded yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {callHistory.map((call, i) => (
                  <div key={i} className="bg-[#0a0a0f] border border-white/10 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm text-gray-400">
                        {new Date(call.timestamp).toLocaleString()}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        call.success
                          ? 'bg-green-500/20 text-green-400'
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {call.success ? <CheckCircle2 className="h-3 w-3 inline mr-1" /> : <XCircle className="h-3 w-3 inline mr-1" />}
                        {call.success ? 'Success' : 'Failed'}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-400 mb-1">Input</p>
                        <pre className="bg-black/30 p-2 rounded text-xs text-gray-300 overflow-x-auto">
                          {JSON.stringify(call.input_data, null, 2)}
                        </pre>
                      </div>
                      <div>
                        <p className="text-gray-400 mb-1">Output</p>
                        <pre className="bg-black/30 p-2 rounded text-xs text-gray-300 overflow-x-auto">
                          {JSON.stringify(call.output_data, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
