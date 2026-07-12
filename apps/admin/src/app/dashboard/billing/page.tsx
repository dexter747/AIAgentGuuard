"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  DollarSign,
  TrendingUp,
  CreditCard,
  Download,
  Building2,
  Users,
  CheckCircle2,
  Clock,
  XCircle,
  Search,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'

interface Subscription {
  id: string
  organization: string
  plan: string
  status: string
  user_count: number
  created_at: string
}

interface BillingStats {
  total_revenue: number
  monthly_recurring: number
  total_subscriptions: number
  active_trials: number
}

export default function BillingPage() {
  const router = useRouter()
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [billingStats, setBillingStats] = useState<BillingStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [statsData, subsData] = await Promise.all([
        apiClient.getBillingStats(),
        apiClient.getSubscriptions()
      ])
      setBillingStats(statsData)
      setSubscriptions(subsData.subscriptions || [])
    } catch (error: any) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        router.push('/')
      }
      console.error('Failed to load billing data:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredSubs = subscriptions.filter(sub =>
    sub.organization.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  // Calculate plan-based revenue
  const getPlanPrice = (plan: string) => {
    switch (plan.toLowerCase()) {
      case 'pro': return 29
      case 'team': return 99
      case 'enterprise': return 299
      default: return 0
    }
  }

  const totalMRR = subscriptions.reduce((sum, sub) => sum + getPlanPrice(sub.plan), 0)
  const proCount = subscriptions.filter(s => s.plan.toLowerCase() === 'pro').length
  const teamCount = subscriptions.filter(s => s.plan.toLowerCase() === 'team').length
  const enterpriseCount = subscriptions.filter(s => s.plan.toLowerCase() === 'enterprise').length
  const freeCount = subscriptions.filter(s => s.plan.toLowerCase() === 'free' || !s.plan).length

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
          <h1 className="text-3xl font-medium text-white">Billing & Revenue</h1>
          <p className="text-muted-foreground mt-1">Financial overview and subscriptions</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Revenue Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Monthly Recurring Revenue', value: formatCurrency(totalMRR), icon: DollarSign, color: 'bg-emerald-500/20 text-emerald-400' },
          { label: 'Total Subscriptions', value: subscriptions.length, icon: CreditCard, color: 'bg-violet-500/20 text-violet-400' },
          { label: 'Paid Plans', value: proCount + teamCount + enterpriseCount, icon: TrendingUp, color: 'bg-rose-500/20 text-rose-400' },
          { label: 'Free Plans', value: freeCount, icon: Users, color: 'bg-amber-500/20 text-amber-400' },
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
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${stat.color.split(' ')[0]}`}>
                    <stat.icon className={`w-5 h-5 ${stat.color.split(' ')[1]}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Plan Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Plan Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { plan: 'Free', count: freeCount, price: '$0/mo', color: 'bg-gray-500' },
                { plan: 'Pro', count: proCount, price: '$29/mo', color: 'bg-violet-500' },
                { plan: 'Team', count: teamCount, price: '$99/mo', color: 'bg-rose-500' },
                { plan: 'Enterprise', count: enterpriseCount, price: '$299/mo', color: 'bg-amber-500' },
              ].map((item) => (
                <div key={item.plan} className="p-4 rounded-xl bg-white/5">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-3 h-3 rounded-full ${item.color}`} />
                    <span className="font-medium text-white">{item.plan}</span>
                  </div>
                  <p className="text-2xl font-medium text-white">{item.count}</p>
                  <p className="text-sm text-muted-foreground">{item.price}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Subscriptions Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader className="border-b border-white/10">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <CardTitle>All Subscriptions</CardTitle>
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Search organizations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Organization</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Plan</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Users</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">MRR</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Since</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSubs.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-4 py-12 text-center text-muted-foreground">
                        No subscriptions found
                      </td>
                    </tr>
                  ) : (
                    filteredSubs.map((sub) => (
                      <tr
                        key={sub.id}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                              <Building2 className="w-5 h-5 text-white" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-white">{sub.organization}</p>
                              <p className="text-xs text-muted-foreground">ID: {sub.id.slice(0, 8)}...</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                            sub.plan.toLowerCase() === 'pro' ? 'bg-violet-500/20 text-violet-400' :
                            sub.plan.toLowerCase() === 'team' ? 'bg-rose-500/20 text-rose-400' :
                            sub.plan.toLowerCase() === 'enterprise' ? 'bg-amber-500/20 text-amber-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {sub.plan.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            <span className="text-sm text-emerald-400">{sub.status}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <Users className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm text-white">{sub.user_count}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm font-medium text-white">
                          {formatCurrency(getPlanPrice(sub.plan))}
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">{formatDate(sub.created_at)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between px-4 py-3 border-t border-white/10">
              <p className="text-sm text-muted-foreground">
                Showing {filteredSubs.length} subscriptions
              </p>
              <p className="text-sm text-white font-medium">
                Total MRR: {formatCurrency(totalMRR)}
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
