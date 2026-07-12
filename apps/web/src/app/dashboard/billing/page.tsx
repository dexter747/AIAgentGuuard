'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { CreditCard, Download, Check, AlertCircle, Calendar, Receipt, ChevronRight } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.overseex.com'

interface Subscription {
  plan: string
  status: string
  current_period_end: string
  cancel_at_period_end: boolean
}

interface Invoice {
  id: string
  amount: number
  status: string
  created_at: string
  pdf_url?: string
}

interface PaymentMethod {
  id: string
  brand: string
  last4: string
  exp_month: number
  exp_year: number
  is_default: boolean
}

export default function BillingPage() {
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch billing data
    const fetchBillingData = async () => {
      try {
        const token = localStorage.getItem('token')
        
        // Fetch subscription
        const subRes = await fetch(`${API_URL}/api/v1/billing/subscription`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (subRes.ok) {
          setSubscription(await subRes.json())
        } else {
          // Default subscription for demo
          setSubscription({
            plan: 'Free',
            status: 'active',
            current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
            cancel_at_period_end: false
          })
        }

        // Fetch invoices
        const invRes = await fetch(`${API_URL}/api/v1/billing/invoices`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (invRes.ok) {
          setInvoices(await invRes.json())
        }

        // Fetch payment methods
        const pmRes = await fetch(`${API_URL}/api/v1/billing/payment-methods`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (pmRes.ok) {
          setPaymentMethods(await pmRes.json())
        }

      } catch (error) {
        console.error('Error fetching billing data:', error)
        // Set default values
        setSubscription({
          plan: 'Free',
          status: 'active',
          current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          cancel_at_period_end: false
        })
      } finally {
        setLoading(false)
      }
    }

    fetchBillingData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const planColors: Record<string, string> = {
    'Free': 'bg-gray-500/20 text-gray-400',
    'Starter': 'bg-blue-500/20 text-blue-400',
    'Pro': 'bg-violet-500/20 text-violet-400',
    'Team': 'bg-purple-500/20 text-purple-400',
    'Enterprise': 'bg-amber-500/20 text-amber-400'
  }

  return (
    <div className="min-h-screen bg-black p-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-medium text-white">Billing & Payments</h1>
        <p className="text-gray-400 mt-1">Manage your subscription and payment methods</p>
      </motion.div>

      <div className="max-w-4xl space-y-6">
        {/* Current Plan */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-white">Current Plan</CardTitle>
                <CardDescription>Your subscription details</CardDescription>
              </div>
              <Badge className={planColors[subscription?.plan || 'Free']}>
                {subscription?.plan || 'Free'}
              </Badge>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {subscription?.status === 'active' ? (
                      <Check className="h-5 w-5 text-emerald-400" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-amber-400" />
                    )}
                    <span className="text-white font-medium">
                      {subscription?.status === 'active' ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  {subscription?.current_period_end && (
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <Calendar className="h-4 w-4" />
                      <span>
                        {subscription.cancel_at_period_end ? 'Cancels' : 'Renews'} on{' '}
                        {new Date(subscription.current_period_end).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>
                <Link href="/dashboard/upgrade">
                  <Button className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500">
                    Upgrade Plan
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Payment Methods */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-white/5 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-white">Payment Methods</CardTitle>
                <CardDescription>Manage your payment options</CardDescription>
              </div>
              <Button variant="outline" className="border-white/10 text-white hover:bg-white/5">
                <CreditCard className="h-4 w-4 mr-2" />
                Add Card
              </Button>
            </CardHeader>
            <CardContent>
              {paymentMethods.length > 0 ? (
                <div className="space-y-3">
                  {paymentMethods.map((pm) => (
                    <div
                      key={pm.id}
                      className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-8 rounded bg-white/10 flex items-center justify-center">
                          <CreditCard className="h-5 w-5 text-gray-400" />
                        </div>
                        <div>
                          <p className="text-white font-medium capitalize">
                            {pm.brand} •••• {pm.last4}
                          </p>
                          <p className="text-sm text-gray-400">
                            Expires {pm.exp_month}/{pm.exp_year}
                          </p>
                        </div>
                      </div>
                      {pm.is_default && (
                        <Badge className="bg-violet-500/20 text-violet-400">Default</Badge>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <CreditCard className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">No payment methods added</p>
                  <p className="text-sm text-gray-500">Add a card to upgrade your plan</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Billing History */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Billing History</CardTitle>
              <CardDescription>View and download your invoices</CardDescription>
            </CardHeader>
            <CardContent>
              {invoices.length > 0 ? (
                <div className="space-y-3">
                  {invoices.map((invoice) => (
                    <div
                      key={invoice.id}
                      className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                          <Receipt className="h-5 w-5 text-violet-400" />
                        </div>
                        <div>
                          <p className="text-white font-medium">
                            ${(invoice.amount / 100).toFixed(2)}
                          </p>
                          <p className="text-sm text-gray-400">
                            {new Date(invoice.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className={
                          invoice.status === 'paid' 
                            ? 'bg-emerald-500/20 text-emerald-400'
                            : 'bg-amber-500/20 text-amber-400'
                        }>
                          {invoice.status}
                        </Badge>
                        {invoice.pdf_url && (
                          <Button variant="ghost" size="sm" asChild>
                            <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                              <Download className="h-4 w-4" />
                            </a>
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Receipt className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">No invoices yet</p>
                  <p className="text-sm text-gray-500">Your billing history will appear here</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
