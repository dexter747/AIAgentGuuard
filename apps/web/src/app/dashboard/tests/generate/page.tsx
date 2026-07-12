'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Wand2, Code2, Download, Copy, Check, Loader2, ChevronDown, Sparkles, FileCode, AlertCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface Trace {
  id: string
  agent_id: string
  agent_name: string
  input: string
  output: string
  status: 'success' | 'error'
  created_at: string
  duration_ms: number
  tools_used: string[]
}

interface Pattern {
  type: string
  confidence: number
  description: string
}

export default function TestGenerationPage() {
  const router = useRouter()
  const [traces, setTraces] = useState<Trace[]>([])
  const [selectedTrace, setSelectedTrace] = useState<string>('')
  const [testName, setTestName] = useState('')
  const [testType, setTestType] = useState<'unit' | 'integration' | 'e2e'>('integration')
  const [generatedCode, setGeneratedCode] = useState('')
  const [patterns, setPatterns] = useState<Pattern[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [copied, setCopied] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)

  useEffect(() => {
    fetchTraces()
  }, [])

  const fetchTraces = async () => {
    try {
      setLoading(true)
      const data = await apiClient.traces.list({ limit: 50 })
      setTraces(data.traces || [])
    } catch (error) {
      console.error('Failed to fetch traces:', error)
    } finally {
      setLoading(false)
    }
  }

  const analyzePatterns = async (traceId: string) => {
    try {
      const response = await apiClient.get(`/tests/analyze-patterns/${traceId}`)
      setPatterns(response.patterns || [])
    } catch (error) {
      console.error('Failed to analyze patterns:', error)
      setPatterns([])
    }
  }

  const handleTraceSelect = (traceId: string) => {
    setSelectedTrace(traceId)
    setShowDropdown(false)
    
    const trace = traces.find(t => t.id === traceId)
    if (trace) {
      setTestName(`test_${trace.agent_name.toLowerCase().replace(/\s+/g, '_')}_${trace.tools_used[0] || 'execution'}`)
      analyzePatterns(traceId)
    }
  }

  const generateTest = async () => {
    if (!selectedTrace || !testName) return

    try {
      setGenerating(true)
      const response = await apiClient.post('/tests/generate', {
        trace_id: selectedTrace,
        test_name: testName,
        test_type: testType
      })
      
      setGeneratedCode(response.generated_code || '')
    } catch (error) {
      console.error('Failed to generate test:', error)
    } finally {
      setGenerating(false)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadTest = () => {
    const blob = new Blob([generatedCode], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${testName}.py`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const selectedTraceData = traces.find(t => t.id === selectedTrace)

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl">
            <Wand2 className="h-6 w-6 text-purple-400" />
          </div>
          <h1 className="text-3xl font-medium text-white">Generate Tests</h1>
        </div>
        <p className="text-gray-400">Automatically generate test code from execution traces</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <div className="space-y-6">
          {/* Trace Selection */}
          <div className="bg-black border border-white/10 rounded-2xl p-6">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Select Trace
            </label>
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="w-full px-4 py-3 bg-[#0a0a0f] border border-white/10 rounded-xl text-left text-white hover:border-purple-500/50 transition-colors flex items-center justify-between"
              >
                <span className={!selectedTrace ? 'text-gray-500' : ''}>
                  {selectedTraceData 
                    ? `${selectedTraceData.agent_name} - ${new Date(selectedTraceData.created_at).toLocaleDateString()}`
                    : 'Select a trace...'}
                </span>
                <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
              </button>

              {showDropdown && (
                <div className="absolute z-10 w-full mt-2 bg-[#0a0a0f] border border-white/10 rounded-xl shadow-xl max-h-80 overflow-y-auto">
                  {loading ? (
                    <div className="p-4 text-center text-gray-400">
                      <Loader2 className="h-5 w-5 animate-spin inline" />
                    </div>
                  ) : traces.length === 0 ? (
                    <div className="p-4 text-center text-gray-400">
                      No successful traces found
                    </div>
                  ) : (
                    traces.map(trace => (
                      <button
                        key={trace.id}
                        onClick={() => handleTraceSelect(trace.id)}
                        className="w-full px-4 py-3 text-left hover:bg-purple-500/10 transition-colors border-b border-white/5 last:border-0"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="text-white font-medium">{trace.agent_name}</p>
                            <p className="text-sm text-gray-400 truncate max-w-xs">{trace.input}</p>
                          </div>
                          <span className="text-xs text-gray-500">
                            {new Date(trace.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        {trace.tools_used.length > 0 && (
                          <div className="flex gap-2 mt-2">
                            {trace.tools_used.slice(0, 3).map((tool, i) => (
                              <span key={i} className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-lg">
                                {tool}
                              </span>
                            ))}
                          </div>
                        )}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            {selectedTraceData && (
              <div className="mt-4 p-4 bg-purple-500/10 border border-purple-500/20 rounded-xl">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-400">Duration</p>
                    <p className="text-white font-medium">{selectedTraceData.duration_ms}ms</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Tools Used</p>
                    <p className="text-white font-medium">{selectedTraceData.tools_used.length}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Test Configuration */}
          <div className="bg-black border border-white/10 rounded-2xl p-6">
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Test Name
            </label>
            <input
              type="text"
              value={testName}
              onChange={(e) => setTestName(e.target.value)}
              placeholder="test_payment_processing"
              className="w-full px-4 py-3 bg-[#0a0a0f] border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors"
            />

            <label className="block text-sm font-medium text-gray-300 mb-3 mt-4">
              Test Type
            </label>
            <div className="grid grid-cols-3 gap-2">
              {(['unit', 'integration', 'e2e'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setTestType(type)}
                  className={`px-4 py-2 rounded-xl font-medium transition-all ${
                    testType === type
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                      : 'bg-[#0a0a0f] border border-white/10 text-gray-400 hover:border-purple-500/50'
                  }`}
                >
                  {type.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Detected Patterns */}
          {patterns.length > 0 && (
            <div className="bg-black border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="h-5 w-5 text-purple-400" />
                <h3 className="text-white font-medium">Detected Patterns</h3>
              </div>
              <div className="space-y-2">
                {patterns.map((pattern, i) => (
                  <div key={i} className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-white text-sm font-medium">{pattern.type}</span>
                      <span className="text-purple-300 text-xs">{Math.round(pattern.confidence * 100)}%</span>
                    </div>
                    <p className="text-gray-400 text-xs">{pattern.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Generate Button */}
          <button
            onClick={generateTest}
            disabled={!selectedTrace || !testName || generating}
            className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium rounded-xl hover:shadow-lg hover:shadow-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Wand2 className="h-5 w-5" />
                Generate Test
              </>
            )}
          </button>
        </div>

        {/* Code Preview Panel */}
        <div className="bg-black border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileCode className="h-5 w-5 text-purple-400" />
              <h3 className="text-white font-medium">Generated Test</h3>
            </div>
            {generatedCode && (
              <div className="flex gap-2">
                <button
                  onClick={copyToClipboard}
                  className="px-3 py-2 bg-[#0a0a0f] border border-white/10 rounded-xl text-gray-300 hover:border-purple-500/50 transition-colors flex items-center gap-2"
                >
                  {copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4" />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
                <button
                  onClick={downloadTest}
                  className="px-3 py-2 bg-[#0a0a0f] border border-white/10 rounded-xl text-gray-300 hover:border-purple-500/50 transition-colors flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Download
                </button>
              </div>
            )}
          </div>

          {generatedCode ? (
            <div className="relative">
              <SyntaxHighlighter
                language="python"
                style={vscDarkPlus}
                customStyle={{
                  margin: 0,
                  borderRadius: '12px',
                  maxHeight: '600px',
                  fontSize: '13px'
                }}
              >
                {generatedCode}
              </SyntaxHighlighter>
            </div>
          ) : (
            <div className="h-[600px] flex items-center justify-center border-2 border-dashed border-white/10 rounded-xl">
              <div className="text-center">
                <Code2 className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">
                  {!selectedTrace 
                    ? 'Select a trace to get started' 
                    : 'Click "Generate Test" to create test code'}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
