"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Building2,
  Search,
  Download,
  Plus,
  Users,
  Shield,
  Eye,
  Edit,
  Trash2,
  TrendingUp,
  X,
  Key,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'

interface Organization {
  id: string
  name: string
  plan?: string
  created_at: string
  user_count?: number
}

export default function OrganizationsPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  
  // Modal states
  const [showViewModal, setShowViewModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null)
  const [editForm, setEditForm] = useState({ name: '', plan: 'free' })
  const [actionLoading, setActionLoading] = useState(false)

  useEffect(() => {
    loadOrganizations()
  }, [])

  const loadOrganizations = async () => {
    try {
      const data = await apiClient.listOrganizations()
      setOrganizations(data.organizations || [])
      setTotal(data.total || 0)
    } catch (error: any) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        router.push('/')
      }
      console.error('Failed to load organizations:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredOrgs = organizations.filter(org =>
    org.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const handleView = (org: Organization) => {
    setSelectedOrg(org)
    setShowViewModal(true)
  }

  const handleEdit = (org: Organization) => {
    setSelectedOrg(org)
    setEditForm({
      name: org.name,
      plan: org.plan || 'free'
    })
    setShowEditModal(true)
  }

  const handleSaveEdit = async () => {
    if (!selectedOrg) return
    setActionLoading(true)
    try {
      await apiClient.updateOrganization(selectedOrg.id, editForm)
      await loadOrganizations()
      setShowEditModal(false)
      setSelectedOrg(null)
    } catch (error) {
      console.error('Failed to update organization:', error)
      alert('Failed to update organization')
    } finally {
      setActionLoading(false)
    }
  }

  const proPlans = organizations.filter(o => o.plan?.toLowerCase() === 'pro').length
  const freePlans = organizations.filter(o => o.plan?.toLowerCase() === 'free' || !o.plan).length
  const totalUserCount = organizations.reduce((sum, org) => sum + (org.user_count || 0), 0)

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
          <h1 className="text-3xl font-medium text-white">Organizations</h1>
          <p className="text-muted-foreground mt-1">Manage all platform organizations</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Organizations', value: total, icon: Building2, color: 'bg-rose-500/20 text-rose-400' },
          { label: 'Pro Plans', value: proPlans, icon: TrendingUp, color: 'bg-violet-500/20 text-violet-400' },
          { label: 'Free Plans', value: freePlans, icon: Shield, color: 'bg-emerald-500/20 text-emerald-400' },
          { label: 'Total Users', value: totalUserCount, icon: Users, color: 'bg-amber-500/20 text-amber-400' },
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

      {/* Organizations Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Card>
          <CardHeader className="border-b border-white/10">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
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
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Users</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Created</th>
                    <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOrgs.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="px-4 py-12 text-center text-muted-foreground">
                        No organizations found
                      </td>
                    </tr>
                  ) : (
                    filteredOrgs.map((org) => (
                      <tr
                        key={org.id}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                              <Building2 className="w-5 h-5 text-white" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-white">{org.name}</p>
                              <p className="text-xs text-muted-foreground">ID: {org.id.slice(0, 8)}...</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 rounded-md text-xs font-medium ${
                            org.plan?.toLowerCase() === 'pro' ? 'bg-rose-500/20 text-rose-400' :
                            org.plan?.toLowerCase() === 'team' ? 'bg-violet-500/20 text-violet-400' :
                            'bg-blue-500/20 text-blue-400'
                          }`}>
                            {org.plan?.toUpperCase() || 'FREE'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <Users className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm text-white">{org.user_count || 0}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">{formatDate(org.created_at)}</td>
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <Button variant="ghost" size="icon" className="w-8 h-8" onClick={() => handleView(org)} title="View">
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="icon" className="w-8 h-8" onClick={() => handleEdit(org)} title="Edit">
                              <Edit className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between px-4 py-3 border-t border-white/10">
              <p className="text-sm text-muted-foreground">
                Showing {filteredOrgs.length} of {total} organizations
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* View Modal */}
      <AnimatePresence>
        {showViewModal && selectedOrg && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowViewModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0a0a0a] border border-white/10 rounded-xl w-full max-w-md p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-medium text-white">Organization Details</h2>
                <Button variant="ghost" size="icon" onClick={() => setShowViewModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-4">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                    <Building2 className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-white">{selectedOrg.name}</h3>
                    <p className="text-muted-foreground text-sm">ID: {selectedOrg.id}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-white/5">
                    <p className="text-xs text-muted-foreground">Plan</p>
                    <p className="text-sm text-white mt-1">{selectedOrg.plan?.toUpperCase() || 'FREE'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-white/5">
                    <p className="text-xs text-muted-foreground">Users</p>
                    <p className="text-sm text-white mt-1">{selectedOrg.user_count || 0}</p>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-white/5">
                  <p className="text-xs text-muted-foreground">Created At</p>
                  <p className="text-sm text-white mt-1">{formatDate(selectedOrg.created_at)}</p>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Edit Modal */}
      <AnimatePresence>
        {showEditModal && selectedOrg && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowEditModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0a0a0a] border border-white/10 rounded-xl w-full max-w-md p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-medium text-white">Edit Organization</h2>
                <Button variant="ghost" size="icon" onClick={() => setShowEditModal(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-muted-foreground">Organization Name</label>
                  <Input
                    value={editForm.name}
                    onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Plan</label>
                  <select
                    value={editForm.plan}
                    onChange={(e) => setEditForm(prev => ({ ...prev, plan: e.target.value }))}
                    className="mt-1 w-full h-10 rounded-md border border-white/10 bg-transparent px-3 text-white"
                  >
                    <option value="free" className="bg-[#0a0a0a]">Free</option>
                    <option value="pro" className="bg-[#0a0a0a]">Pro</option>
                    <option value="team" className="bg-[#0a0a0a]">Team</option>
                    <option value="enterprise" className="bg-[#0a0a0a]">Enterprise</option>
                  </select>
                </div>
                <div className="flex gap-3 pt-4">
                  <Button variant="outline" className="flex-1" onClick={() => setShowEditModal(false)}>
                    Cancel
                  </Button>
                  <Button className="flex-1" onClick={handleSaveEdit} disabled={actionLoading}>
                    {actionLoading ? 'Saving...' : 'Save Changes'}
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
