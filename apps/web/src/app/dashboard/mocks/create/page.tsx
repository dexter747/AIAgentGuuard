'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Plus, Code2, Save, Loader2, AlertCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

export default function CreateMockPage() {
  const router = useRouter()
  const [toolName, setToolName] = useState('')
  const [responseData, setResponseData] = useState('{\n  "status": "success",\n  "data": {}\n}')
  const [failureMode, setFailureMode] = useState(false)
  const [failureRate, setFailureRate] = useState(0)
  const [errorMessage, setErrorMessage] = useState('')
  const [saving, setSaving] = useState(false)
  const [jsonError, setJsonError] = useState<string | null>(null)

  const validateJSON = (json: string) => {
    try {
      JSON.parse(json)
      setJsonError(null)
      return true
    } catch (e: any) {
      setJsonError(e.message)
      return false
    }
  }

  const handleResponseChange = (value: string) => {
    setResponseData(value)
    validateJSON(value)
  }

  const createMock = async () => {
    if (!toolName || !validateJSON(responseData)) return

    try {
      setSaving(true)
      await apiClient.post('/mocks', {
        tool_name: toolName,
        response: JSON.parse(responseData),
        behavior: failureMode ? 'error' : 'success',
        conditions: failureMode ? { 
          failure_rate: failureRate,
          error_message: errorMessage || 'Operation failed'
        } : undefined
      })
      router.push('/dashboard/mocks')
    } catch (error) {
      console.error('Failed to create mock:', error)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-gradient-to-br from-violet-500/20 to-purple-600/20 rounded-xl">
            <Plus className="h-6 w-6 text-purple-400" />
          </div>
          <h1 className="text-3xl font-medium text-white">Create Custom Mock</h1>
        </div>
        <p className="text-gray-400">Define a custom mock for testing your AI agents</p>
      </div>

      <div className="space-y-6">
        {/* Tool Name */}
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Tool Name <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={toolName}
            onChange={(e) => setToolName(e.target.value)}
            placeholder="my_custom_tool"
            className="w-full px-4 py-3 bg-[#0a0a0f] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors"
          />
          <p className="text-gray-500 text-xs mt-2">Use lowercase with underscores (e.g., stripe_create_charge)</p>
        </div>

        {/* Response Data */}
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <label className="block text-sm font-medium text-gray-300 mb-3">
            Response Data (JSON) <span className="text-red-400">*</span>
          </label>
          <div className="relative">
            <Code2 className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <textarea
              value={responseData}
              onChange={(e) => handleResponseChange(e.target.value)}
              rows={12}
              className="w-full pl-10 pr-4 py-3 bg-[#0a0a0f] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors font-mono text-sm"
            />
          </div>
          {jsonError && (
            <div className="mt-3 p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-2">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-400 font-medium text-sm">Invalid JSON</p>
                <p className="text-red-300/70 text-xs">{jsonError}</p>
              </div>
            </div>
          )}
        </div>

        {/* Failure Injection */}
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <label className="text-sm font-medium text-gray-300">
              Failure Injection
            </label>
            <button
              onClick={() => setFailureMode(!failureMode)}
              className={`px-3 py-1.5 rounded-lg font-medium text-sm transition-all ${
                failureMode
                  ? 'bg-purple-500 text-white'
                  : 'bg-[#0a0a0f] border border-white/10 text-gray-400'
              }`}
            >
              {failureMode ? 'Enabled' : 'Disabled'}
            </button>
          </div>

          {failureMode && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Failure Rate ({failureRate}%)
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={failureRate}
                  onChange={(e) => setFailureRate(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Error Message
                </label>
                <input
                  type="text"
                  value={errorMessage}
                  onChange={(e) => setErrorMessage(e.target.value)}
                  placeholder="Rate limit exceeded"
                  className="w-full px-4 py-2 bg-[#0a0a0f] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors"
                />
              </div>
            </div>
          )}

          <p className="text-gray-500 text-xs mt-3">
            Enable failure injection to test error handling in your agents
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            onClick={() => router.back()}
            className="flex-1 py-3 bg-black border border-white/10 text-white rounded-xl hover:border-purple-500/50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={createMock}
            disabled={!toolName || !!jsonError || saving}
            className="flex-1 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium rounded-xl hover:shadow-lg hover:shadow-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {saving ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Save className="h-5 w-5" />
                Create Mock
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
