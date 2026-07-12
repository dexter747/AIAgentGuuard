"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Shield,
  LayoutDashboard,
  Users,
  Building2,
  CreditCard,
  Settings,
  Bell,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Activity,
  FileText,
  Mail,
  Search,
  MessageSquare,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
  { icon: Users, label: 'Users', href: '/dashboard/users' },
  { icon: Building2, label: 'Organizations', href: '/dashboard/organizations' },
  { icon: CreditCard, label: 'Billing', href: '/dashboard/billing' },
  { icon: Activity, label: 'Analytics', href: '/dashboard/analytics' },
  { icon: Mail, label: 'Emails', href: '/dashboard/emails' },
  { icon: MessageSquare, label: 'Contact Queries', href: '/dashboard/contact-queries' },
  { icon: FileText, label: 'Logs', href: '/dashboard/logs' },
  { icon: Settings, label: 'Settings', href: '/dashboard/settings' },
]

interface AdminUser {
  id: string
  email: string
  full_name: string
  role: string
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)
  const [adminUser, setAdminUser] = useState<AdminUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const pathname = usePathname()
  const router = useRouter()

  useEffect(() => {
    // Check for admin authentication
    const token = localStorage.getItem('admin_token')
    const userStr = localStorage.getItem('admin_user')

    if (!token || !userStr) {
      router.push('/')
      return
    }

    try {
      const user = JSON.parse(userStr)
      // Check if user has admin privileges (using is_admin flag from backend)
      if (!user.is_admin) {
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_user')
        router.push('/')
        return
      }
      setAdminUser(user)
    } catch {
      router.push('/')
      return
    }

    setIsLoading(false)
  }, [router])

  const handleSignOut = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
    router.push('/')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <motion.div
          className="w-8 h-8 border-2 border-violet-500/30 border-t-violet-500 rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Animated Background */}
      <div className="fixed inset-0 pointer-events-none bg-black">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-600/5 rounded-full blur-[150px]" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/5 rounded-full blur-[150px]" />
      </div>

      <div className="relative flex min-h-screen">
        {/* Sidebar */}
        <motion.aside
          initial={false}
          animate={{ width: collapsed ? 80 : 280 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className="fixed left-0 top-0 bottom-0 z-50 flex flex-col border-r border-white/10 bg-black/80 backdrop-blur-xl"
        >
          {/* Logo */}
          <div className="flex items-center h-16 px-4 border-b border-white/10">
            <Link href="/dashboard" className="flex items-center gap-3">
              <div className={`flex items-center justify-center ${!collapsed ? "h-10 w-10" : "h-8 w-8"} rounded-xl bg-gradient-to-br from-violet-500 to-purple-600`}>
                <Shield className="w-5 h-5 text-white" />
              </div>
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="text-lg font-medium text-white whitespace-nowrap"
                  >
                    OverseeX
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 py-4 px-3 space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
              return (
                <Tooltip key={item.href} delayDuration={collapsed ? 0 : 1000}>
                  <TooltipTrigger asChild>
                    <Link
                      href={item.href}
                      className={cn(
                        "relative flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200",
                        isActive
                          ? "text-white"
                          : "text-gray-400 hover:text-white hover:bg-white/5"
                      )}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="activeNav"
                          className="absolute inset-0 rounded-xl bg-gradient-to-r from-violet-500/20 to-purple-500/20 border border-violet-500/30"
                          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                        />
                      )}
                      <item.icon className={cn(
                        "relative z-10 w-5 h-5 flex-shrink-0",
                        isActive && "text-violet-400"
                      )} />
                      <AnimatePresence>
                        {!collapsed && (
                          <motion.span
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -10 }}
                            className="relative z-10 text-sm font-medium whitespace-nowrap"
                          >
                            {item.label}
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </Link>
                  </TooltipTrigger>
                  {collapsed && (
                    <TooltipContent side="right">
                      {item.label}
                    </TooltipContent>
                  )}
                </Tooltip>
              )
            })}
          </nav>

          {/* Bottom Section */}
          <div className="p-3 border-t border-white/10">
            <div className={cn(
              "flex items-center gap-3 p-3 rounded-xl bg-white/5",
              collapsed && "justify-center"
            )}>
              <Avatar className="w-9 h-9 bg-gradient-to-br from-violet-500 to-purple-600">
                <AvatarFallback className="bg-transparent text-white">
                  {adminUser?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'SA'}
                </AvatarFallback>
              </Avatar>
              <AnimatePresence>
                {!collapsed && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="flex-1 min-w-0"
                  >
                    <p className="text-sm font-medium text-white truncate">{adminUser?.full_name || 'Admin'}</p>
                    <p className="text-xs text-gray-500 truncate">{adminUser?.email || 'admin@overseex.com'}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Collapse Button */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-zinc-900 border border-white/10 flex items-center justify-center text-gray-400 hover:text-white transition-colors"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </motion.aside>

        {/* Main Content */}
        <main className={cn(
          "flex-1 transition-all duration-300",
          collapsed ? "ml-20" : "ml-[280px]"
        )}>
          {/* Top Header */}
          <header className="sticky top-0 z-40 h-16 border-b border-white/10 bg-black/80 backdrop-blur-xl">
            <div className="flex items-center justify-between h-full px-6">
              <div className="flex items-center gap-4 flex-1">
                <div className="relative max-w-md w-full">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <Input
                    placeholder="Search users, orgs, transactions..."
                    className="pl-10 bg-white/5 border-white/10 text-white placeholder:text-gray-500"
                  />
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon" className="relative text-gray-400 hover:text-white">
                      <Bell className="w-5 h-5" />
                      <span className="absolute top-1 right-1 w-2 h-2 bg-violet-500 rounded-full" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Notifications</TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon" onClick={handleSignOut} className="text-gray-400 hover:text-white">
                      <LogOut className="w-5 h-5" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>Sign out</TooltipContent>
                </Tooltip>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}