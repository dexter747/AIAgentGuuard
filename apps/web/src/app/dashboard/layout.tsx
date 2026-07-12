'use client'

import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Activity,
  Bot,
  TestTube,
  Brain,
  Bell,
  Network,
  Settings,
  Shield,
  LogOut,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Sparkles,
  Key,
  User,
  CreditCard,
  ArrowUpCircle,
  HeartPulse,
  Boxes,
  TrendingDown,
  Book,
  Layers
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Traces', href: '/dashboard/traces', icon: Activity },
  { name: 'Agents', href: '/dashboard/agents', icon: Bot },
  { name: 'Coordination', href: '/dashboard/coordination', icon: Network },
  { name: 'Patterns', href: '/dashboard/patterns', icon: Layers },
  { name: 'Tests', href: '/dashboard/tests', icon: TestTube },
  { name: 'Health Monitoring', href: '/dashboard/health', icon: HeartPulse },
  { name: 'Mocks', href: '/dashboard/mocks', icon: Boxes },
  { name: 'Regressions', href: '/dashboard/regressions', icon: TrendingDown },
  { name: 'AI Insights', href: '/dashboard/insights', icon: Brain },
  { name: 'Webhooks', href: '/dashboard/webhooks', icon: Bell },
  { name: 'API Keys', href: '/dashboard/settings', icon: Key },
]

interface UserData {
  id: string
  email: string
  full_name?: string
  org_id?: string
  plan?: string
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const router = useRouter()
  const [collapsed, setCollapsed] = useState(false)
  const [user, setUser] = useState<UserData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (!token) {
      router.push('/signin')
      return
    }

    if (userData) {
      try {
        setUser(JSON.parse(userData))
      } catch {
        router.push('/signin')
      }
    }
    
    setLoading(false)
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/signin')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-violet-500/20 border-t-violet-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const userInitials = user.full_name 
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()
    : user.email.slice(0, 2).toUpperCase()

  return (
    <TooltipProvider>
      <div className="flex h-screen bg-black overflow-hidden">
        {/* Sidebar */}
        <motion.aside 
          initial={false}
          animate={{ width: collapsed ? 80 : 280 }}
          className="relative flex flex-col border-r border-white/10 bg-black"
        >
          {/* Logo */}
          <div className="p-6 flex items-center justify-between">
            <Link href="/dashboard" className="flex items-center gap-3">
              <img 
                src="/logo.jpeg" 
                alt="OverseeX" 
                className={!collapsed ? "h-10 w-auto" : "h-8 w-auto"}
              />
              {!collapsed && (
                <motion.span 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-xl font-medium text-white"
                >
                  OverseeX
                </motion.span>
              )}
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== '/dashboard' && pathname?.startsWith(item.href))
              
              return (
                <Tooltip key={item.name} delayDuration={0}>
                  <TooltipTrigger asChild>
                    <Link
                      href={item.href}
                      className={cn(
                        "relative flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group",
                        isActive
                          ? "text-white"
                          : "text-gray-500 hover:text-white hover:bg-white/5"
                      )}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="activeNav"
                          className="absolute inset-0 bg-violet-500/10 rounded-xl border border-violet-500/30"
                          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                        />
                      )}
                      <item.icon className={cn(
                        "h-5 w-5 relative z-10 transition-colors",
                        isActive ? "text-violet-400" : "text-gray-500 group-hover:text-violet-400"
                      )} />
                      {!collapsed && (
                        <span className="relative z-10">{item.name}</span>
                      )}
                      {isActive && !collapsed && (
                        <Sparkles className="h-4 w-4 text-violet-400 ml-auto relative z-10" />
                      )}
                    </Link>
                  </TooltipTrigger>
                  {collapsed && (
                    <TooltipContent side="right">
                      {item.name}
                    </TooltipContent>
                  )}
                </Tooltip>
              )
            })}
          </nav>

          {/* Bottom section */}
          <div className="p-3 border-t border-white/10">
            {/* User Profile Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={cn(
                  "w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 transition-all",
                  collapsed && "justify-center"
                )}>
                  <Avatar className="h-9 w-9">
                    <AvatarImage src="" />
                    <AvatarFallback className="bg-gradient-to-br from-violet-500 to-purple-600 text-white text-sm">
                      {userInitials}
                    </AvatarFallback>
                  </Avatar>
                  {!collapsed && (
                    <>
                      <div className="flex-1 min-w-0 text-left">
                        <p className="text-sm font-medium text-white truncate">
                          {user.full_name || user.email}
                        </p>
                        <p className="text-xs text-gray-500 truncate">
                          {user.plan || 'Free'} Plan
                        </p>
                      </div>
                      <ChevronDown className="h-4 w-4 text-gray-500" />
                    </>
                  )}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent 
                align={collapsed ? "center" : "end"} 
                className="w-56 bg-black border-white/10"
              >
                <DropdownMenuLabel className="text-white">My Account</DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-white/10" />
                <DropdownMenuItem asChild>
                  <Link href="/dashboard/profile" className="flex items-center gap-2 cursor-pointer text-gray-300 hover:text-white">
                    <User className="h-4 w-4" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/dashboard/settings" className="flex items-center gap-2 cursor-pointer text-gray-300 hover:text-white">
                    <Settings className="h-4 w-4" />
                    Settings
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/dashboard/billing" className="flex items-center gap-2 cursor-pointer text-gray-300 hover:text-white">
                    <CreditCard className="h-4 w-4" />
                    Billing & Payments
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/dashboard/upgrade" className="flex items-center gap-2 cursor-pointer text-violet-400 hover:text-violet-300">
                    <ArrowUpCircle className="h-4 w-4" />
                    Upgrade Plan
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-white/10" />
                <DropdownMenuItem asChild>
                  <a href="/docs" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 cursor-pointer text-gray-300 hover:text-white">
                    <Book className="h-4 w-4" />
                    API Documentation
                  </a>
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-white/10" />
                <DropdownMenuItem 
                  onClick={handleLogout}
                  className="flex items-center gap-2 cursor-pointer text-red-400 hover:text-red-300"
                >
                  <LogOut className="h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Collapse button */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="absolute -right-3 top-20 p-1.5 rounded-full bg-black border border-white/10 text-gray-500 hover:text-white transition-colors"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </motion.aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto bg-black">
          {children}
        </main>
      </div>
    </TooltipProvider>
  )
}
