"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  Mail,
  Send,
  CheckCircle2,
  Clock,
  XCircle,
  Eye,
  MoreHorizontal,
  Search,
  Filter,
  Plus,
  FileText,
  Users,
  RefreshCw,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'

export default function EmailsPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [emails, setEmails] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadEmails()
  }, [])

  const loadEmails = async () => {
    try {
      const data = await apiClient.listEmails()
      setEmails(data.emails || [])
    } catch (error: any) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        router.push('/')
      }
      console.error('Failed to load emails:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-medium text-white">Email Management</h1>
          <p className="text-muted-foreground mt-1">Manage email templates and delivery</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Sync
          </Button>
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Template
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Emails', value: emails.length.toString(), icon: Mail, color: 'rose' },
          { label: 'Delivered', value: emails.filter((e: any) => e.status === 'delivered').length.toString(), icon: CheckCircle2, color: 'emerald' },
          { label: 'Pending', value: emails.filter((e: any) => e.status === 'pending').length.toString(), icon: Clock, color: 'violet' },
          { label: 'Failed', value: emails.filter((e: any) => e.status === 'failed').length.toString(), icon: XCircle, color: 'amber' },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-2xl font-medium text-white mt-1">{stat.value}</p>
                  </div>
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    stat.color === 'violet' ? 'bg-violet-500/20' :
                    stat.color === 'emerald' ? 'bg-emerald-500/20' :
                    stat.color === 'violet' ? 'bg-violet-500/20' :
                    'bg-amber-500/20'
                  }`}>
                    <stat.icon className={`w-5 h-5 ${
                      stat.color === 'rose' ? 'text-rose-400' :
                      stat.color === 'emerald' ? 'text-emerald-400' :
                      stat.color === 'violet' ? 'text-violet-400' :
                      'text-amber-400'
                    }`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Email List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Email Management System Ready</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">
              <Mail className="w-12 h-12 text-rose-400 mx-auto mb-4" />
              <p className="text-lg text-white">Email service configured</p>
              <p className="text-sm text-muted-foreground mt-2">
                Email templates and delivery tracking available
              </p>
              {emails.length > 0 && (
                <p className="text-sm text-white mt-4">
                  {emails.length} emails in the system
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}