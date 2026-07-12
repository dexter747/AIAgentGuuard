"use client"

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, ArrowRight, Lock, Users, Building2, Zap, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api-client'

export default function AdminLoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const data = await apiClient.login(email, password)
      
      // Store user data
      localStorage.setItem('admin_user', JSON.stringify(data.user))
      
      // Redirect to dashboard
      window.location.href = '/dashboard'
    } catch (err: any) {
      // Handle different error formats
      let errorMessage = 'Login failed'
      
      if (err.response?.data?.detail) {
        // FastAPI error format
        if (Array.isArray(err.response.data.detail)) {
          // Validation errors
          errorMessage = err.response.data.detail.map((e: any) => e.msg).join(', ')
        } else if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail
        } else {
          errorMessage = JSON.stringify(err.response.data.detail)
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-black">
      {/* Animated Background */}
      <div className="fixed inset-0 bg-black">
        <div className="absolute top-1/4 -left-1/4 w-1/2 h-1/2 bg-violet-600/10 rounded-full blur-[150px] animate-pulse" />
        <div className="absolute bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-purple-600/10 rounded-full blur-[150px] animate-pulse delay-1000" />
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at center, rgba(139,92,246,0.03) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }} />
      </div>

      <div className="relative z-10 min-h-screen flex">
        {/* Left Side - Branding */}
        <div className="hidden lg:flex lg:w-1/2 flex-col justify-center px-16">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center gap-3 mb-8">
              <img 
                src="/logo.jpeg" 
                alt="OverseeX" 
                className="h-14 w-auto"
              />
              <span className="text-3xl font-medium text-white">OverseeX</span>
            </div>

            <h1 className="text-5xl font-medium text-white mb-6 leading-tight">
              Admin Control Center
            </h1>
            <p className="text-xl text-gray-400 mb-12">
              Manage your AI agent security infrastructure with complete visibility and control.
            </p>

            {/* Feature Cards */}
            <div className="space-y-4">
              {[
                { icon: Users, title: "User Management", desc: "Control access across all organizations" },
                { icon: Building2, title: "Organization Overview", desc: "Monitor all registered organizations" },
                { icon: Zap, title: "Real-time Analytics", desc: "Live platform statistics and insights" },
              ].map((feature, i) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + i * 0.1 }}
                  className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500/20 to-purple-500/20 flex items-center justify-center">
                    <feature.icon className="w-5 h-5 text-violet-400" />
                  </div>
                  <div>
                    <p className="font-medium text-white">{feature.title}</p>
                    <p className="text-sm text-gray-500">{feature.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right Side - Login Form */}
        <div className="flex-1 flex items-center justify-center px-8 py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-md"
          >
            {/* Mobile Logo */}
            <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
              <img 
                src="/logo.jpeg" 
                alt="OverseeX" 
                className="h-12 w-auto"
              />
              <span className="text-3xl font-medium text-white">OverseeX</span>
            </div>

            <Card className="border-white/10 bg-black/50 backdrop-blur-sm">
              <CardHeader className="text-center pb-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center mx-auto mb-4 shadow-xl shadow-violet-500/30">
                  <Lock className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-2xl text-white">Admin Login</CardTitle>
                <CardDescription className="text-gray-400">
                  Enter your credentials to access the admin portal
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleLogin} className="space-y-4">
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center gap-2 text-red-400"
                    >
                      <AlertCircle className="w-4 h-4" />
                      <span className="text-sm">{error}</span>
                    </motion.div>
                  )}

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-400">Email</label>
                    <Input
                      type="email"
                      placeholder="admin@overseex.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="bg-white/5 border-white/10 text-white placeholder:text-gray-500 focus:border-violet-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-400">Password</label>
                    <Input
                      type="password"
                      placeholder="••••••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="bg-white/5 border-white/10 text-white placeholder:text-gray-500 focus:border-violet-500"
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-12 text-base bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white border-0"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <motion.div
                        className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      />
                    ) : (
                      <>
                        Sign In
                        <ArrowRight className="ml-2 w-5 h-5" />
                      </>
                    )}
                  </Button>

                  <div className="text-center pt-4">
                    <a href="#" className="text-sm text-violet-400 hover:text-violet-300 transition-colors">
                      Forgot your password?
                    </a>
                  </div>
                </form>
              </CardContent>
            </Card>

            <p className="text-center text-xs text-gray-600 mt-6">
              Protected by OverseeX Security • Authorized Personnel Only
            </p>
          </motion.div>
        </div>
      </div>
    </main>
  )
}
