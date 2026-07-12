'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Sparkles, Download, CheckCircle2, Loader2, Search } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

const MOCK_CATEGORIES = {
  'Payment': ['stripe_create_charge', 'stripe_create_customer', 'stripe_create_subscription'],
  'Email': ['sendgrid_send_email', 'sendgrid_send_bulk'],
  'Calendar': ['google_calendar_create_event', 'google_calendar_list_events'],
  'Communication': ['slack_post_message', 'slack_upload_file', 'twilio_send_sms'],
  'Development': ['github_create_issue', 'github_create_pr'],
  'AI': ['openai_create_completion', 'openai_create_chat_completion'],
  'Cloud': ['aws_s3_upload', 'aws_lambda_invoke']
}

interface PrebuiltMock {
  name: string
  description: string
  category: string
  example_response: any
}

export default function PrebuiltMocksPage() {
  const router = useRouter()
  const [prebuiltMocks, setPrebuiltMocks] = useState<PrebuiltMock[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingMock, setLoadingMock] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('All')

  useEffect(() => {
    fetchPrebuiltMocks()
  }, [])

  const fetchPrebuiltMocks = async () => {
    try {
      setLoading(true)
      const data = await apiClient.get('/mocks/prebuilt')
      setPrebuiltMocks(Array.isArray(data) ? data : [])
    } catch (error: any) {
      console.error('Failed to fetch prebuilt mocks:', error)
      // Show user-friendly error
      if (error.message?.includes('Invalid API key') || error.message?.includes('401')) {
        alert('Please log in to view prebuilt mocks')
        window.location.href = '/signin'
      }
      setPrebuiltMocks([])
    } finally {
      setLoading(false)
    }
  }

  const loadMock = async (mockName: string) => {
    try {
      setLoadingMock(mockName)
      await apiClient.post(`/mocks/prebuilt/${mockName}`)
      router.push('/dashboard/mocks')
    } catch (error) {
      console.error('Failed to load mock:', error)
    } finally {
      setLoadingMock(null)
    }
  }

  const filteredMocks = prebuiltMocks.filter(mock => {
    const matchesSearch = mock.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         mock.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || mock.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const categories = ['All', ...Object.keys(MOCK_CATEGORIES)]

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-gradient-to-br from-violet-500/20 to-purple-600/20 rounded-xl">
            <Sparkles className="h-6 w-6 text-purple-400" />
          </div>
          <h1 className="text-3xl font-medium text-white">Pre-built Mocks</h1>
        </div>
        <p className="text-gray-400">Ready-to-use mocks for popular APIs and services</p>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search pre-built mocks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-black border border-white/10 rounded-xl text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none transition-colors"
          />
        </div>
      </div>

      {/* Category Filters */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
        {categories.map(category => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-xl font-medium whitespace-nowrap transition-all ${
              selectedCategory === category
                ? 'bg-gradient-to-r from-violet-500 to-purple-600 text-white'
                : 'bg-black border border-white/10 text-gray-400 hover:border-purple-500/50'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Mocks Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
        </div>
      ) : filteredMocks.length === 0 ? (
        <div className="bg-black border border-white/10 rounded-2xl p-12 text-center">
          <Sparkles className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No mocks found matching your criteria</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredMocks.map(mock => (
            <div
              key={mock.name}
              className="bg-black border border-white/10 rounded-2xl p-6 hover:border-purple-500/30 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-white mb-1">{mock.name}</h3>
                  <span className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-lg">
                    {mock.category}
                  </span>
                </div>
                <div className="p-2 bg-purple-500/10 rounded-lg">
                  <Sparkles className="h-5 w-5 text-purple-400" />
                </div>
              </div>

              <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                {mock.description || 'Pre-built mock for testing'}
              </p>

              <button
                onClick={() => loadMock(mock.name)}
                disabled={loadingMock === mock.name}
                className="w-full py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium rounded-xl hover:shadow-lg hover:shadow-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loadingMock === mock.name ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4" />
                    Load Mock
                  </>
                )}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
