"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  Settings,
  Shield,
  Mail,
  Bell,
  Key,
  Globe,
  Database,
  Palette,
  Save,
  RotateCcw,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiClient } from '@/lib/api-client'

const settingsSections = [
  { id: 'general', label: 'General', icon: Settings },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'email', label: 'Email', icon: Mail },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'api', label: 'API Keys', icon: Key },
  { id: 'integrations', label: 'Integrations', icon: Globe },
  { id: 'database', label: 'Database', icon: Database },
  { id: 'appearance', label: 'Appearance', icon: Palette },
]

export default function SettingsPage() {
  const router = useRouter()
  const [activeSection, setActiveSection] = useState('general')
  const [isSaving, setIsSaving] = useState(false)
  const [settings, setSettings] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const data = await apiClient.getSettings()
      setSettings(data)
    } catch (error: any) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        router.push('/')
      }
      console.error('Failed to load settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await apiClient.updateSettings(settings)
    } catch (error) {
      console.error('Failed to save settings:', error)
    } finally {
      setTimeout(() => setIsSaving(false), 1500)
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
          <h1 className="text-3xl font-medium text-white">Settings</h1>
          <p className="text-muted-foreground mt-1">Manage platform configuration</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? (
              <motion.div
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full mr-2"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Save Changes
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-1"
        >
          <Card>
            <CardContent className="p-4">
              <nav className="space-y-1">
                {settingsSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                      activeSection === section.id
                        ? 'bg-gradient-to-r from-rose-500/20 to-pink-500/20 text-white border border-rose-500/30'
                        : 'text-muted-foreground hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <section.icon className={`w-5 h-5 ${
                      activeSection === section.id ? 'text-rose-400' : ''
                    }`} />
                    <span className="text-sm font-medium">{section.label}</span>
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </motion.div>

        {/* Settings Content */}
        <motion.div
          key={activeSection}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-3"
        >
          {activeSection === 'general' && (
            <Card>
              <CardHeader>
                <CardTitle>General Settings</CardTitle>
                <CardDescription>Basic platform configuration options</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">Platform Name</label>
                    <Input defaultValue="OverseeX" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">Support Email</label>
                    <Input defaultValue="support@overseex.com" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">Default Timezone</label>
                    <Input defaultValue="UTC" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">Date Format</label>
                    <Input defaultValue="YYYY-MM-DD" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === 'security' && (
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
                <CardDescription>Configure security policies and authentication</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                    <div>
                      <p className="font-medium text-white">Two-Factor Authentication</p>
                      <p className="text-sm text-muted-foreground">Require 2FA for all admin accounts</p>
                    </div>
                    <div className="w-12 h-6 bg-emerald-500 rounded-full relative cursor-pointer">
                      <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                    <div>
                      <p className="font-medium text-white">Session Timeout</p>
                      <p className="text-sm text-muted-foreground">Auto-logout after inactivity</p>
                    </div>
                    <Input defaultValue="30" className="w-20" />
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-xl bg-white/5">
                    <div>
                      <p className="font-medium text-white">IP Whitelist</p>
                      <p className="text-sm text-muted-foreground">Restrict admin access to specific IPs</p>
                    </div>
                    <div className="w-12 h-6 bg-secondary rounded-full relative cursor-pointer">
                      <div className="absolute left-1 top-1 w-4 h-4 bg-muted-foreground rounded-full" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === 'email' && (
            <Card>
              <CardHeader>
                <CardTitle>Email Configuration</CardTitle>
                <CardDescription>SMTP and email service settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">SMTP Host</label>
                    <Input defaultValue="smtp.sendgrid.net" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">SMTP Port</label>
                    <Input defaultValue="587" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">SMTP Username</label>
                    <Input defaultValue="apikey" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">SMTP Password</label>
                    <Input type="password" defaultValue="••••••••••••" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">From Email</label>
                    <Input defaultValue="noreply@overseex.com" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">From Name</label>
                    <Input defaultValue="OverseeX" />
                  </div>
                </div>
                <Button variant="outline" className="mt-4">
                  <Mail className="w-4 h-4 mr-2" />
                  Send Test Email
                </Button>
              </CardContent>
            </Card>
          )}

          {activeSection === 'api' && (
            <Card>
              <CardHeader>
                <CardTitle>API Configuration</CardTitle>
                <CardDescription>Manage API keys and rate limits</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-white/5">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-white">Production API Key</p>
                      <Button variant="outline" size="sm">Regenerate</Button>
                    </div>
                    <Input defaultValue="ag_prod_xxxx••••••••••••xxxx" readOnly className="font-mono" />
                  </div>
                  <div className="p-4 rounded-xl bg-white/5">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-white">Test API Key</p>
                      <Button variant="outline" size="sm">Regenerate</Button>
                    </div>
                    <Input defaultValue="ag_test_xxxx••••••••••••xxxx" readOnly className="font-mono" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-white/10">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">Rate Limit (requests/min)</label>
                    <Input defaultValue="1000" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white">Max Request Size (MB)</label>
                    <Input defaultValue="10" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {(activeSection === 'notifications' || activeSection === 'integrations' || 
            activeSection === 'database' || activeSection === 'appearance') && (
            <Card>
              <CardHeader>
                <CardTitle className="capitalize">{activeSection} Settings</CardTitle>
                <CardDescription>Configure {activeSection} options</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <div className="w-16 h-16 rounded-2xl bg-rose-500/20 flex items-center justify-center mb-4">
                    {activeSection === 'notifications' && <Bell className="w-8 h-8 text-rose-400" />}
                    {activeSection === 'integrations' && <Globe className="w-8 h-8 text-rose-400" />}
                    {activeSection === 'database' && <Database className="w-8 h-8 text-rose-400" />}
                    {activeSection === 'appearance' && <Palette className="w-8 h-8 text-rose-400" />}
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Coming Soon</h3>
                  <p className="text-muted-foreground max-w-md">
                    The {activeSection} settings are currently being developed and will be available in the next release.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  )
}