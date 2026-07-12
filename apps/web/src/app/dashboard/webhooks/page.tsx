'use client'

import { useState, useEffect } from 'react'
import { Bell, Plus, Trash2, ExternalLink, CheckCircle, XCircle, Clock, RefreshCw, X, Copy, Eye, EyeOff, Play, Loader2 } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface Webhook {
  id: string
  url: string
  events: string[]
  is_active: boolean
  secret: string
  created_at: string
}

interface WebhookDelivery {
  webhook_id: string
  event: string
  response_status: number | null
  error: string | null
  delivered_at: string
  duration_ms: number | null
}

const availableEvents = [
  { value: 'trace.created', label: 'Trace Created', description: 'When a new trace is recorded' },
  { value: 'trace.error', label: 'Trace Error', description: 'When a trace completes with an error' },
  { value: 'test.passed', label: 'Test Passed', description: 'When an automated test passes' },
  { value: 'test.failed', label: 'Test Failed', description: 'When an automated test fails' },
  { value: 'coordination.issue_detected', label: 'Coordination Issue', description: 'When a multi-agent coordination issue is detected' },
  { value: 'rate_limit.exceeded', label: 'Rate Limit Exceeded', description: 'When API rate limit is exceeded' },
  { value: 'agent.created', label: 'Agent Created', description: 'When a new agent is registered' },
  { value: 'agent.health_changed', label: 'Agent Health Changed', description: 'When agent health status changes' }
]

export default function WebhooksPage() {
  const [webhooks, setWebhooks] = useState<Webhook[]>([])
  const [deliveries, setDeliveries] = useState<WebhookDelivery[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedWebhook, setSelectedWebhook] = useState<Webhook | null>(null)
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  useEffect(() => {
    async function fetchWebhooks() {
      try {
        setLoading(true)
        const data = await apiClient.webhooks.list()
        setWebhooks(data)
      } catch (error) {
        console.error('Failed to fetch webhooks:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchWebhooks()
    const interval = setInterval(fetchWebhooks, 30000) // Refresh every 30s

    return () => clearInterval(interval)
  }, [])
  const toggleSecret = (id: string) => {
    setShowSecrets(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const deleteWebhook = async (id: string) => {
    if (confirm('Are you sure you want to delete this webhook?')) {
      try {
        await apiClient.webhooks.delete(id)
        setWebhooks(webhooks.filter(w => w.id !== id))
        if (selectedWebhook?.id === id) {
          setSelectedWebhook(null)
        }
      } catch (error) {
        console.error('Failed to delete webhook:', error)
      }
    }
  }

  const testWebhook = async (id: string) => {
    try {
      await apiClient.webhooks.test(id)
      // Refresh webhooks to get updated data
      const data = await apiClient.webhooks.list()
      setWebhooks(data)
      alert('Test webhook sent successfully!')
    } catch (error) {
      console.error('Failed to test webhook:', error)
      alert('Failed to send test webhook')
    }
  }

  const getDeliveryStatus = (delivery: WebhookDelivery) => {
    if (delivery.error) {
      return <XCircle className="h-5 w-5 text-red-500" />
    }
    if (delivery.response_status && delivery.response_status >= 200 && delivery.response_status < 300) {
      return <CheckCircle className="h-5 w-5 text-green-500" />
    }
    return <Clock className="h-5 w-5 text-yellow-500" />
  }

  const webhookDeliveries = selectedWebhook 
    ? deliveries.filter(d => d.webhook_id === selectedWebhook.id)
    : deliveries

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="bg-black shadow border-b border-white/10">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-medium tracking-tight text-white">
              Webhooks
            </h1>
            <p className="mt-1 text-sm text-gray-400">
              Receive real-time notifications when events occur
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700 transition-colors"
          >
            <Plus className="h-5 w-5" />
            Add Webhook
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Webhooks List */}
          <div className="lg:col-span-2">
            <div className="bg-black rounded-xl shadow border border-white/10">
              <div className="px-6 py-4 border-b border-white/10">
                <h2 className="text-lg font-medium text-white">Active Webhooks</h2>
              </div>
              
              {webhooks.length > 0 ? (
                <div className="divide-y divide-white/10">
                  {webhooks.map(webhook => (
                    <div 
                      key={webhook.id}
                      className={`p-6 cursor-pointer hover:bg-white/5 transition-colors ${selectedWebhook?.id === webhook.id ? 'bg-violet-500/10' : ''}`}
                      onClick={() => setSelectedWebhook(webhook)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div className={`p-2 rounded-lg ${webhook.is_active ? 'bg-green-500/20' : 'bg-gray-500/20'}`}>
                            <Bell className={`h-5 w-5 ${webhook.is_active ? 'text-green-400' : 'text-gray-400'}`} />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium text-white truncate max-w-xs">
                                {webhook.url}
                              </p>
                              <a 
                                href={webhook.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="text-gray-400 hover:text-gray-300"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </div>
                            <div className="mt-2 flex flex-wrap gap-1">
                              {webhook.events.map(event => (
                                <span 
                                  key={event}
                                  className="px-2 py-0.5 text-xs bg-violet-500/20 text-violet-300 rounded"
                                >
                                  {event}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              testWebhook(webhook.id)
                            }}
                            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                            title="Test webhook"
                          >
                            <Play className="h-4 w-4 text-gray-400" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              deleteWebhook(webhook.id)
                            }}
                            className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
                            title="Delete webhook"
                          >
                            <Trash2 className="h-4 w-4 text-red-400" />
                          </button>
                        </div>
                      </div>

                      {/* Secret */}
                      <div className="mt-4 flex items-center gap-2">
                        <span className="text-sm text-gray-400">Secret:</span>
                        <code className="px-2 py-1 bg-black rounded text-sm font-mono text-gray-300 border border-white/10">
                          {showSecrets[webhook.id] ? webhook.secret : '••••••••••••••••'}
                        </code>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            toggleSecret(webhook.id)
                          }}
                          className="p-1 hover:bg-white/10 rounded"
                        >
                          {showSecrets[webhook.id] ? (
                            <EyeOff className="h-4 w-4 text-gray-400" />
                          ) : (
                            <Eye className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            copyToClipboard(webhook.secret)
                          }}
                          className="p-1 hover:bg-white/10 rounded"
                        >
                          <Copy className="h-4 w-4 text-gray-400" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 text-center">
                  <Bell className="h-12 w-12 mx-auto mb-4 text-gray-600" />
                  <p className="text-lg font-medium text-white">No webhooks configured</p>
                  <p className="text-sm text-gray-400 mt-1">Add a webhook to receive real-time notifications</p>
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="mt-4 px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700"
                  >
                    Add Your First Webhook
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Deliveries */}
          <div className="lg:col-span-1">
            <div className="bg-black rounded-xl shadow sticky top-6 border border-white/10">
              <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
                <h2 className="text-lg font-medium text-white">Recent Deliveries</h2>
                {selectedWebhook && (
                  <button
                    onClick={() => setSelectedWebhook(null)}
                    className="text-sm text-violet-400 hover:text-violet-300"
                  >
                    Show all
                  </button>
                )}
              </div>
              
              {webhookDeliveries.length > 0 ? (
                <div className="divide-y divide-white/10 max-h-96 overflow-y-auto">
                  {webhookDeliveries.map((delivery, idx) => (
                    <div key={idx} className="p-4">
                      <div className="flex items-start gap-3">
                        {getDeliveryStatus(delivery)}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white">{delivery.event}</p>
                          <p className="text-xs text-gray-400">
                            {new Date(delivery.delivered_at).toLocaleString()}
                          </p>
                          {delivery.duration_ms && (
                            <p className="text-xs text-gray-500">{delivery.duration_ms}ms</p>
                          )}
                          {delivery.error && (
                            <p className="text-xs text-red-400 mt-1">{delivery.error}</p>
                          )}
                        </div>
                        <span className={`px-2 py-0.5 text-xs rounded ${
                          delivery.response_status && delivery.response_status < 300
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {delivery.response_status || 'Failed'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-gray-400">
                  <Clock className="h-8 w-8 mx-auto mb-2 text-gray-600" />
                  <p className="text-sm">No recent deliveries</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateWebhookModal 
          onClose={() => setShowCreateModal(false)}
          onCreate={(webhook) => {
            setWebhooks([...webhooks, webhook])
            setShowCreateModal(false)
          }}
        />
      )}
    </div>
  )
}

function CreateWebhookModal({ 
  onClose, 
  onCreate 
}: { 
  onClose: () => void
  onCreate: (webhook: Webhook) => void 
}) {
  const [url, setUrl] = useState('')
  const [events, setEvents] = useState<string[]>([])
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  const toggleEvent = (event: string) => {
    if (events.includes(event)) {
      setEvents(events.filter(e => e !== event))
    } else {
      setEvents([...events, event])
    }
  }

  const handleSubmit = async () => {
    try {
      setCreating(true)
      setError('')
      
      // Call the API to create the webhook
      const createdWebhook = await apiClient.webhooks.create({
        url,
        events
      })
      
      onCreate(createdWebhook)
    } catch (err) {
      console.error('Failed to create webhook:', err)
      setError(err instanceof Error ? err.message : 'Failed to create webhook')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-black rounded-xl shadow-2xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto border border-violet-500/30">
        <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center">
          <h2 className="text-lg font-medium text-white">Add Webhook</h2>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded">
            <X className="h-5 w-5 text-gray-400" />
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Payload URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/webhooks/overseex"
              className="w-full px-3 py-2 bg-black border border-white/10 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 text-white placeholder:text-gray-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              We'll send a POST request to this URL when events occur
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-3">Events</label>
            <div className="space-y-2">
              {availableEvents.map(event => (
                <label
                  key={event.value}
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    events.includes(event.value) 
                      ? 'border-violet-500 bg-violet-500/20' 
                      : 'border-white/10 hover:border-violet-500/20 bg-black'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={events.includes(event.value)}
                    onChange={() => toggleEvent(event.value)}
                    className="mt-0.5 h-4 w-4 text-violet-600 focus:ring-violet-500 border-gray-600 rounded"
                  />
                  <div>
                    <p className="font-medium text-white">{event.label}</p>
                    <p className="text-sm text-gray-400">{event.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
          
          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}
        </div>
        
        <div className="px-6 py-4 border-t border-white/10 flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={creating}
            className="px-4 py-2 border border-white/10 rounded-lg hover:bg-white/5 text-white disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!url || events.length === 0 || creating}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700 disabled:opacity-50"
          >
            {creating && <Loader2 className="h-4 w-4 animate-spin" />}
            {creating ? 'Creating...' : 'Create Webhook'}
          </button>
        </div>
      </div>
    </div>
  )
}
