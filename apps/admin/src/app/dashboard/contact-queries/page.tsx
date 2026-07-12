"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Mail,
  Phone,
  Calendar,
  CheckCircle2,
  Circle,
  Trash2,
  RefreshCw,
  Filter,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/lib/api-client'

interface ContactQuery {
  id: string
  name: string
  email: string
  phone: string | null
  subject: string
  message: string
  is_read: boolean
  created_at: string
}

export default function ContactQueriesPage() {
  const [queries, setQueries] = useState<ContactQuery[]>([])
  const [loading, setLoading] = useState(true)
  const [showUnreadOnly, setShowUnreadOnly] = useState(false)
  const [selectedQuery, setSelectedQuery] = useState<ContactQuery | null>(null)

  const fetchQueries = async () => {
    setLoading(true)
    try {
      const data = await apiClient.getContactQueries(showUnreadOnly)
      setQueries(data)
    } catch (error) {
      console.error('Failed to fetch contact queries:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQueries()
  }, [showUnreadOnly])

  const markAsRead = async (id: string) => {
    try {
      await apiClient.markContactQueryAsRead(id)
      fetchQueries()
      if (selectedQuery?.id === id) {
        setSelectedQuery({ ...selectedQuery, is_read: true })
      }
    } catch (error) {
      console.error('Failed to mark as read:', error)
    }
  }

  const deleteQuery = async (id: string) => {
    if (!confirm('Are you sure you want to delete this query?')) return
    
    try {
      await apiClient.deleteContactQuery(id)
      fetchQueries()
      if (selectedQuery?.id === id) {
        setSelectedQuery(null)
      }
    } catch (error) {
      console.error('Failed to delete query:', error)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const unreadCount = queries.filter(q => !q.is_read).length

  return (
    <div className="p-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-medium text-white">Contact Queries</h1>
          <p className="text-gray-400 mt-1">
            Manage customer inquiries and messages
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant={showUnreadOnly ? "default" : "outline"}
            onClick={() => setShowUnreadOnly(!showUnreadOnly)}
            className="flex items-center gap-2"
          >
            <Filter className="w-4 h-4" />
            {showUnreadOnly ? 'Show All' : 'Unread Only'}
            {unreadCount > 0 && (
              <span className="ml-1 px-2 py-0.5 bg-purple-600 text-white text-xs rounded-full">
                {unreadCount}
              </span>
            )}
          </Button>
          <Button
            variant="outline"
            onClick={fetchQueries}
            className="flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Queries List */}
        <div className="lg:col-span-1 space-y-3">
          <Card className="bg-black/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-lg">Messages ({queries.length})</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {loading ? (
                <div className="p-8 text-center text-gray-400">
                  <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
                  Loading...
                </div>
              ) : queries.length === 0 ? (
                <div className="p-8 text-center text-gray-400">
                  <Mail className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>No queries found</p>
                </div>
              ) : (
                <div className="max-h-[600px] overflow-y-auto">
                  {queries.map((query) => (
                    <motion.div
                      key={query.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className={`p-4 border-b border-white/5 cursor-pointer transition-colors hover:bg-white/5 ${
                        selectedQuery?.id === query.id ? 'bg-white/10' : ''
                      }`}
                      onClick={() => setSelectedQuery(query)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {query.is_read ? (
                            <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                          ) : (
                            <Circle className="w-4 h-4 text-purple-400 flex-shrink-0" />
                          )}
                          <span className={`font-medium ${!query.is_read ? 'text-white' : 'text-gray-400'}`}>
                            {query.name}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-400 truncate mb-1">{query.subject}</p>
                      <p className="text-xs text-gray-500">{formatDate(query.created_at)}</p>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Query Details */}
        <div className="lg:col-span-2">
          {selectedQuery ? (
            <Card className="bg-black/50 border-white/10">
              <CardHeader className="border-b border-white/5">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {selectedQuery.is_read ? (
                        <CheckCircle2 className="w-5 h-5 text-green-400" />
                      ) : (
                        <Circle className="w-5 h-5 text-purple-400" />
                      )}
                      <CardTitle className="text-xl">{selectedQuery.subject}</CardTitle>
                    </div>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-400">
                      <div className="flex items-center gap-2">
                        <Mail className="w-4 h-4" />
                        <a href={`mailto:${selectedQuery.email}`} className="hover:text-white">
                          {selectedQuery.email}
                        </a>
                      </div>
                      {selectedQuery.phone && (
                        <div className="flex items-center gap-2">
                          <Phone className="w-4 h-4" />
                          <a href={`tel:${selectedQuery.phone}`} className="hover:text-white">
                            {selectedQuery.phone}
                          </a>
                        </div>
                      )}
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        {formatDate(selectedQuery.created_at)}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {!selectedQuery.is_read && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => markAsRead(selectedQuery.id)}
                      >
                        Mark as Read
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => deleteQuery(selectedQuery.id)}
                      className="text-red-400 border-red-400/20 hover:bg-red-400/10"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-400 mb-2 block">From</label>
                    <p className="text-white">{selectedQuery.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-400 mb-2 block">Message</label>
                    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                      <p className="text-white whitespace-pre-wrap">{selectedQuery.message}</p>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-white/5">
                    <a
                      href={`mailto:${selectedQuery.email}?subject=Re: ${selectedQuery.subject}`}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                    >
                      <Mail className="w-4 h-4" />
                      Reply via Email
                    </a>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="bg-black/50 border-white/10 h-full min-h-[500px] flex items-center justify-center">
              <CardContent className="text-center">
                <Mail className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p className="text-gray-400">Select a message to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
