"use client"

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Users,
  Building2,
  DollarSign,
  Shield,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  MoreHorizontal,
  RefreshCw,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { apiClient } from '@/lib/api-client'

// Stats Card Component
function StatsCard({ title, value, change, changeType, icon: Icon, color }: {
  title: string
  value: string | number
  change: number
  changeType: 'increase' | 'decrease'
  icon: any
  color: string
}) {
  const colors: Record<string, string> = {
    violet: 'from-violet-500 to-purple-600 shadow-violet-500/30',
    emerald: 'from-emerald-500 to-teal-600 shadow-emerald-500/30',
    purple: 'from-purple-500 to-indigo-600 shadow-purple-500/30',
    amber: 'from-amber-500 to-orange-600 shadow-amber-500/30',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="relative overflow-hidden group hover:border-white/20 transition-all duration-300 bg-black/50 border-white/10">
        <div className={`absolute inset-0 bg-gradient-to-br ${colors[color]} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-gray-400 mb-1">{title}</p>
              <p className="text-3xl font-medium text-white">{value}</p>
              <div className="flex items-center gap-1 mt-2">
                {changeType === 'increase' ? (
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-400" />
                )}
                <span className={changeType === 'increase' ? 'text-emerald-400' : 'text-red-400'}>
                  {change}%
                </span>
                <span className="text-gray-500 text-sm">vs last month</span>
              </div>
            </div>
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors[color]} flex items-center justify-center shadow-lg`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

interface DashboardStats {
  total_users: number
  total_organizations: number
  monthly_revenue: number
  active_guards: number
  users_change: number
  orgs_change: number
  revenue_change: number
  guards_change: number
}

interface RecentUser {
  id: string
  full_name: string
  email: string
  organization: string
  plan: string
  status: string
}

interface SystemStatus {
  name: string
  status: 'operational' | 'degraded' | 'down'
  uptime: number
}

interface ActivityLog {
  type: 'user' | 'alert' | 'payment' | 'system'
  message: string
  time: string
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentUsers, setRecentUsers] = useState<RecentUser[]>([])
  const [systemStatus, setSystemStatus] = useState<SystemStatus[]>([])
  const [activities, setActivities] = useState<ActivityLog[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [adminUser, setAdminUser] = useState<any>(null)

  useEffect(() => {
    const userStr = localStorage.getItem('admin_user')
    if (userStr) {
      setAdminUser(JSON.parse(userStr))
    }
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setIsLoading(true)

    try {
      // Fetch all data in parallel
      const [statsData, usersData, statusData, activityData] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.listUsers({ limit: 5 }),
        apiClient.getSystemStatus(),
        apiClient.getActivityLogs(10)
      ])

      setStats(statsData)
      setRecentUsers(Array.isArray(usersData) ? usersData : usersData.users || [])
      setSystemStatus(statusData)
      setActivities(activityData)
    } catch (error: any) {
      console.error('Failed to fetch dashboard data:', error)
      
      // If unauthorized, redirect to login
      if (error.response?.status === 401 || error.response?.status === 403) {
        apiClient.clearToken()
        window.location.href = '/'
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Fallback data if API fails
  const displayStats = stats || {
    total_users: 0,
    total_organizations: 0,
    monthly_revenue: 0,
    active_guards: 0,
    users_change: 0,
    orgs_change: 0,
    revenue_change: 0,
    guards_change: 0
  }

  const displayUsers = recentUsers.length > 0 ? recentUsers : []
  
  const displayStatus = systemStatus.length > 0 ? systemStatus : [
    { name: 'API Gateway', status: 'operational' as const, uptime: 99.99 },
    { name: 'Guard Engine', status: 'operational' as const, uptime: 99.97 },
    { name: 'Database', status: 'operational' as const, uptime: 99.95 },
    { name: 'Email Service', status: 'operational' as const, uptime: 99.90 },
  ]

  const displayActivities = activities.length > 0 ? activities : []

  const statCards = [
    { 
      title: 'Total Users', 
      value: displayStats.total_users.toLocaleString(), 
      change: Math.abs(displayStats.users_change), 
      changeType: displayStats.users_change >= 0 ? 'increase' as const : 'decrease' as const, 
      icon: Users, 
      color: 'violet' 
    },
    { 
      title: 'Organizations', 
      value: displayStats.total_organizations.toLocaleString(), 
      change: Math.abs(displayStats.orgs_change), 
      changeType: displayStats.orgs_change >= 0 ? 'increase' as const : 'decrease' as const, 
      icon: Building2, 
      color: 'purple' 
    },
    { 
      title: 'Monthly Revenue', 
      value: `$${displayStats.monthly_revenue.toLocaleString()}`, 
      change: Math.abs(displayStats.revenue_change), 
      changeType: displayStats.revenue_change >= 0 ? 'increase' as const : 'decrease' as const, 
      icon: DollarSign, 
      color: 'emerald' 
    },
    { 
      title: 'Active Guards', 
      value: displayStats.active_guards.toLocaleString(), 
      change: Math.abs(displayStats.guards_change), 
      changeType: displayStats.guards_change >= 0 ? 'increase' as const : 'decrease' as const, 
      icon: Shield, 
      color: 'amber' 
    },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-medium text-white">Dashboard</h1>
          <p className="text-gray-400 mt-1">Welcome back, {adminUser?.full_name || 'Admin'}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            onClick={fetchDashboardData}
            className="border-white/10 text-gray-300 hover:bg-white/5"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 border-0">
            <Activity className="w-4 h-4 mr-2" />
            View Analytics
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <StatsCard {...stat} />
          </motion.div>
        ))}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Users */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2"
        >
          <Card className="bg-black/50 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-white">Recent Users</CardTitle>
              <Button variant="ghost" size="sm" className="text-violet-400 hover:text-violet-300">
                View All
                <ArrowUpRight className="w-4 h-4 ml-1" />
              </Button>
            </CardHeader>
            <CardContent>
              {displayUsers.length > 0 ? (
                <div className="space-y-4">
                  {displayUsers.map((user, i) => (
                    <div key={user.id || i} className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors">
                      <div className="flex items-center gap-3">
                        <Avatar className="bg-gradient-to-br from-violet-500 to-purple-600">
                          <AvatarFallback className="bg-transparent text-white">
                            {user.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-white">{user.full_name}</p>
                          <p className="text-sm text-gray-500">{user.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right hidden sm:block">
                          <p className="text-sm text-white">{user.organization}</p>
                          <p className="text-xs text-gray-500">{user.plan}</p>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          user.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' :
                          user.status === 'pending' ? 'bg-amber-500/20 text-amber-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {user.status}
                        </span>
                        <Button variant="ghost" size="icon" className="w-8 h-8 text-gray-400 hover:text-white">
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  {isLoading ? 'Loading users...' : 'No recent users found'}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* System Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="h-full bg-black/50 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">System Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {displayStatus.map((service, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {service.status === 'operational' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : service.status === 'degraded' ? (
                        <AlertTriangle className="w-4 h-4 text-amber-400" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-red-400" />
                      )}
                      <span className="text-sm text-white">{service.name}</span>
                    </div>
                    <span className={`text-xs ${
                      service.status === 'operational' ? 'text-emerald-400' : 
                      service.status === 'degraded' ? 'text-amber-400' : 'text-red-400'
                    }`}>
                      {service.uptime}% uptime
                    </span>
                  </div>
                  <Progress value={service.uptime} className="h-1.5 bg-white/10" />
                </div>
              ))}
              <div className="pt-4 border-t border-white/10">
                <p className="text-sm text-gray-500">
                  Last checked: {new Date().toLocaleTimeString()}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Activity Feed */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card className="bg-black/50 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white">Recent Activity</CardTitle>
            <Button variant="ghost" size="sm" className="text-violet-400 hover:text-violet-300">View All</Button>
          </CardHeader>
          <CardContent>
            {displayActivities.length > 0 ? (
              <div className="space-y-4">
                {displayActivities.map((activity, i) => (
                  <div key={i} className="flex items-start gap-4 p-3 rounded-xl hover:bg-white/5 transition-colors">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      activity.type === 'user' ? 'bg-violet-500/20' :
                      activity.type === 'alert' ? 'bg-amber-500/20' :
                      activity.type === 'payment' ? 'bg-emerald-500/20' :
                      'bg-purple-500/20'
                    }`}>
                      {activity.type === 'user' && <Users className="w-5 h-5 text-violet-400" />}
                      {activity.type === 'alert' && <AlertTriangle className="w-5 h-5 text-amber-400" />}
                      {activity.type === 'payment' && <DollarSign className="w-5 h-5 text-emerald-400" />}
                      {activity.type === 'system' && <Shield className="w-5 h-5 text-purple-400" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-white">{activity.message}</p>
                      <div className="flex items-center gap-1 mt-1">
                        <Clock className="w-3 h-3 text-gray-500" />
                        <span className="text-xs text-gray-500">{activity.time}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                {isLoading ? 'Loading activity...' : 'No recent activity'}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}