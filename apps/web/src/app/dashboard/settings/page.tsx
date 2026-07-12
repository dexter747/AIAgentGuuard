'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Key, 
  Copy, 
  Eye, 
  EyeOff, 
  Plus, 
  Trash2, 
  RefreshCw,
  Shield,
  User,
  Bell,
  CreditCard,
  Building2,
  Settings,
  ChevronRight,
  Check,
  AlertTriangle,
  Loader2
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'
import { apiClient } from '@/lib/api-client'

interface ApiKey {
  id: string
  name: string
  key: string
  created: string
  lastUsed: string | null
  status: 'active' | 'revoked'
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

export default function SettingsPage() {
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set())
  const [copiedKey, setCopiedKey] = useState<string | null>(null)
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [userProfile, setUserProfile] = useState<any>(null)
  const [usage, setUsage] = useState<any>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const [keys, profile] = await Promise.all([
          apiClient.apiKeys.list(),
          apiClient.get('/auth/me')
        ])
        setApiKeys(keys)
        setUserProfile(profile)
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const toggleKeyVisibility = (id: string) => {
    const newVisible = new Set(visibleKeys)
    if (newVisible.has(id)) {
      newVisible.delete(id)
    } else {
      newVisible.add(id)
    }
    setVisibleKeys(newVisible)
  }

  const copyToClipboard = async (key: string, id: string) => {
    await navigator.clipboard.writeText(key)
    setCopiedKey(id)
    setTimeout(() => setCopiedKey(null), 2000)
  }

  const createNewKey = async () => {
    try {
      const newKey = await apiClient.apiKeys.create(newKeyName || 'New API Key')
      setApiKeys([newKey, ...apiKeys])
      setNewKeyName('')
      setShowCreateModal(false)
    } catch (error) {
      console.error('Failed to create API key:', error)
    }
  }

  const revokeKey = async (id: string) => {
    try {
      await apiClient.apiKeys.revoke(id)
      setApiKeys(apiKeys.map(key => 
        key.id === id ? { ...key, status: 'revoked' as const } : key
      ))
    } catch (error) {
      console.error('Failed to revoke API key:', error)
    }
  }

  const deleteKey = async (id: string) => {
    try {
      await apiClient.apiKeys.delete(id)
      setApiKeys(apiKeys.filter(key => key.id !== id))
    } catch (error) {
      console.error('Failed to delete API key:', error)
    }
  }

  const maskKey = (key: string) => {
    return key.substring(0, 12) + '•'.repeat(20) + key.substring(key.length - 4)
  }

  return (
    <div className="min-h-screen p-8 bg-black">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-medium text-white">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your account, API keys, and preferences.</p>
      </motion.div>

      {/* Tabs */}
      <Tabs defaultValue="api-keys" className="space-y-6">
        <TabsList className="bg-white/5 border border-white/10 p-1">
          <TabsTrigger value="api-keys" className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-white gap-2">
            <Key className="h-4 w-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="profile" className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-white gap-2">
            <User className="h-4 w-4" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="notifications" className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-white gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="billing" className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-white gap-2">
            <CreditCard className="h-4 w-4" />
            Billing
          </TabsTrigger>
          <TabsTrigger value="team" className="data-[state=active]:bg-violet-500/20 data-[state=active]:text-white gap-2">
            <Building2 className="h-4 w-4" />
            Team
          </TabsTrigger>
        </TabsList>

        {/* API Keys Tab */}
        <TabsContent value="api-keys" className="space-y-6">
          {/* API Keys Header */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-medium text-white">API Keys</h2>
              <p className="text-sm text-muted-foreground">Manage your API keys for programmatic access.</p>
            </div>
            <Button onClick={() => setShowCreateModal(true)} className="gap-2">
              <Plus className="h-4 w-4" />
              Create New Key
            </Button>
          </div>

          {/* Warning */}
          <div className="flex items-start gap-4 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <AlertTriangle className="h-5 w-5 text-amber-400 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-amber-200">Keep your API keys secure</p>
              <p className="text-sm text-amber-200/70">
                Never share your API keys publicly or commit them to version control. 
                Use environment variables to store them securely.
              </p>
            </div>
          </div>

          {/* Create Key Modal */}
          {showCreateModal && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <Card className="bg-white/5 border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Create New API Key</CardTitle>
                  <CardDescription>Give your key a descriptive name to identify its purpose.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="keyName">Key Name</Label>
                    <Input
                      id="keyName"
                      placeholder="e.g., Production Server, CI/CD Pipeline"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      className="bg-white/5 border-white/10"
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button onClick={createNewKey}>Create Key</Button>
                    <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                      Cancel
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* API Keys List */}
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-4"
          >
            {apiKeys.map((apiKey) => (
              <motion.div key={apiKey.id} variants={item}>
                <Card className={cn(
                  "bg-white/5 border-white/10 transition-all hover:border-white/20",
                  apiKey.status === 'revoked' && "opacity-60"
                )}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 space-y-4">
                        <div className="flex items-center gap-3">
                          <div className={cn(
                            "p-2 rounded-lg",
                            apiKey.status === 'active' ? "bg-violet-500/20" : "bg-gray-500/20"
                          )}>
                            <Key className={cn(
                              "h-5 w-5",
                              apiKey.status === 'active' ? "text-violet-400" : "text-gray-400"
                            )} />
                          </div>
                          <div>
                            <h3 className="font-medium text-white">{apiKey.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <span className={cn(
                                "text-xs px-2 py-0.5 rounded-full",
                                apiKey.status === 'active' 
                                  ? "bg-emerald-500/20 text-emerald-400" 
                                  : "bg-red-500/20 text-red-400"
                              )}>
                                {apiKey.status === 'active' ? 'Active' : 'Revoked'}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                Created {apiKey.created}
                              </span>
                              {apiKey.lastUsed && (
                                <span className="text-xs text-muted-foreground">
                                  • Last used {apiKey.lastUsed}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* API Key Display */}
                        <div className="flex items-center gap-2">
                          <code className="flex-1 px-4 py-3 rounded-lg bg-black/30 text-sm font-mono text-gray-300 border border-white/10">
                            {visibleKeys.has(apiKey.id) ? apiKey.key : maskKey(apiKey.key)}
                          </code>
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => toggleKeyVisibility(apiKey.id)}
                            className="shrink-0"
                          >
                            {visibleKeys.has(apiKey.id) ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                          <Button
                            variant="outline"
                            size="icon"
                            onClick={() => copyToClipboard(apiKey.key, apiKey.id)}
                            className="shrink-0"
                          >
                            {copiedKey === apiKey.id ? (
                              <Check className="h-4 w-4 text-emerald-400" />
                            ) : (
                              <Copy className="h-4 w-4" />
                            )}
                          </Button>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 ml-4">
                        {apiKey.status === 'active' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => revokeKey(apiKey.id)}
                            className="text-amber-400 hover:text-amber-300 hover:bg-amber-500/10"
                          >
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Revoke
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deleteKey(apiKey.id)}
                          className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          {/* Usage Example */}
          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white text-lg">Quick Start</CardTitle>
              <CardDescription>Use your API key to authenticate requests.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg bg-black/30 border border-white/10 overflow-hidden">
                <div className="flex items-center gap-2 px-4 py-2 bg-white/5 border-b border-white/10">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  <span className="ml-2 text-xs text-muted-foreground">example.py</span>
                </div>
                <pre className="p-4 text-sm overflow-x-auto">
                  <code className="text-gray-300">{`import overseex

# Initialize with your API key
client = overseex.Client(
    api_key="ag_live_your_key_here"
)

# Or use environment variable
# export OVERSEEX_API_KEY=ag_live_your_key_here
client = overseex.Client()

# Start monitoring your agents
@client.trace
def my_agent(input: str):
    # Your agent logic here
    return result`}</code>
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Profile Information</CardTitle>
              <CardDescription>Update your personal details and preferences.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="firstName">Full Name</Label>
                  <Input 
                    id="firstName" 
                    defaultValue={userProfile?.full_name || 'User'} 
                    className="bg-white/5 border-white/10" 
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    defaultValue={userProfile?.email || ''} 
                    className="bg-white/5 border-white/10" 
                    disabled
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="company">Organization</Label>
                <Input 
                  id="company" 
                  defaultValue={userProfile?.org_name || 'Organization'} 
                  className="bg-white/5 border-white/10" 
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Input 
                  id="role" 
                  defaultValue={userProfile?.role || 'Member'} 
                  className="bg-white/5 border-white/10" 
                  disabled
                />
              </div>
              <Button>Save Changes</Button>
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Change Password</CardTitle>
              <CardDescription>Update your password to keep your account secure.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="currentPassword">Current Password</Label>
                <Input id="currentPassword" type="password" className="bg-white/5 border-white/10" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="newPassword">New Password</Label>
                <Input id="newPassword" type="password" className="bg-white/5 border-white/10" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <Input id="confirmPassword" type="password" className="bg-white/5 border-white/10" />
              </div>
              <Button>Update Password</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Email Notifications</CardTitle>
              <CardDescription>Choose what updates you want to receive via email.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {[
                { id: 'agent-alerts', label: 'Agent Health Alerts', description: 'Get notified when an agent fails or becomes unhealthy', enabled: true },
                { id: 'test-failures', label: 'Test Failures', description: 'Receive alerts when automated tests fail', enabled: true },
                { id: 'weekly-reports', label: 'Weekly Reports', description: 'Get a weekly summary of your agent performance', enabled: false },
                { id: 'billing', label: 'Billing Updates', description: 'Receive invoices and billing notifications', enabled: true },
                { id: 'product-updates', label: 'Product Updates', description: 'Stay informed about new features and improvements', enabled: false },
              ].map((notification) => (
                <div key={notification.id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">{notification.label}</p>
                    <p className="text-sm text-muted-foreground">{notification.description}</p>
                  </div>
                  <Switch defaultChecked={notification.enabled} />
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Slack Integration</CardTitle>
              <CardDescription>Connect your Slack workspace to receive alerts.</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="gap-2">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
                </svg>
                Connect Slack
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Billing Tab */}
        <TabsContent value="billing" className="space-y-6">
          {/* Current Plan */}
          <Card className="bg-gradient-to-br from-violet-500/20 to-purple-500/10 border-violet-500/30">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-violet-300">Current Plan</p>
                  <h3 className="text-2xl font-medium text-white mt-1">Free Plan</h3>
                  <p className="text-muted-foreground mt-1">60 req/min • 1,000 req/hour</p>
                </div>
                <Button variant="outline">Upgrade to Pro</Button>
              </div>
            </CardContent>
          </Card>

          {/* Usage */}
          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Usage This Month</CardTitle>
              <CardDescription>Your current resource usage and limits.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {[
                { label: 'API Requests (Today)', used: apiKeys.length * 120, limit: 10000, percent: (apiKeys.length * 120 / 10000) * 100 },
                { label: 'Active Agents', used: 0, limit: 'Unlimited', percent: null },
                { label: 'API Keys', used: apiKeys.filter(k => k.status === 'active').length, limit: 10, percent: (apiKeys.filter(k => k.status === 'active').length / 10) * 100 },
                { label: 'Trace Retention', used: 7, limit: 7, percent: 100 },
              ].map((usage) => (
                <div key={usage.label} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-white">{usage.label}</span>
                    <span className="text-muted-foreground">
                      {usage.used.toLocaleString()} / {typeof usage.limit === 'number' ? usage.limit.toLocaleString() : usage.limit}
                      {usage.label === 'Trace Retention' && ' days'}
                    </span>
                  </div>
                  {usage.percent !== null && (
                    <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full"
                        style={{ width: `${usage.percent}%` }}
                      />
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Payment Method */}
          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Payment Method</CardTitle>
              <CardDescription>Manage your payment information.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10">
                <div className="flex items-center gap-4">
                  <div className="p-2 rounded-lg bg-white/10">
                    <CreditCard className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-white">No payment method</p>
                    <p className="text-sm text-muted-foreground">Add card to upgrade to Pro</p>
                  </div>
                </div>
                <Button variant="outline" size="sm">Add Card</Button>
              </div>
            </CardContent>
          </Card>

          {/* Invoices */}
          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Billing History</CardTitle>
              <CardDescription>View and download your past invoices.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-6 text-center text-muted-foreground">
                <p className="text-sm">No billing history yet</p>
                <p className="text-xs mt-2">Invoices will appear here after upgrading to a paid plan</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Team Tab */}
        <TabsContent value="team" className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-medium text-white">Team Members</h2>
              <p className="text-sm text-muted-foreground">Manage who has access to your organization.</p>
            </div>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Invite Member
            </Button>
          </div>

          <Card className="bg-white/5 border-white/10">
            <CardContent className="p-0">
              <div className="divide-y divide-white/10">
                {[
                  { name: 'John Doe', email: 'john@example.com', role: 'Owner', avatar: 'JD' },
                  { name: 'Jane Smith', email: 'jane@example.com', role: 'Admin', avatar: 'JS' },
                  { name: 'Mike Wilson', email: 'mike@example.com', role: 'Member', avatar: 'MW' },
                ].map((member, i) => (
                  <div key={i} className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white font-medium text-sm">
                        {member.avatar}
                      </div>
                      <div>
                        <p className="font-medium text-white">{member.name}</p>
                        <p className="text-sm text-muted-foreground">{member.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xs px-2 py-1 rounded-full bg-violet-500/20 text-violet-400">
                        {member.role}
                      </span>
                    </div>
                  </div>
                ))}
                <div className="p-6 text-center text-muted-foreground">
                  <p className="text-sm">No team members yet</p>
                  <p className="text-xs mt-2">Invite team members to collaborate on your agents</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-white/5 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Organization Settings</CardTitle>
              <CardDescription>Update your organization details.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="orgName">Organization Name</Label>
                <Input 
                  id="orgName" 
                  defaultValue={userProfile?.org_name || 'Organization'} 
                  className="bg-white/5 border-white/10" 
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="orgSlug">Organization ID</Label>
                <div className="flex">
                  <Input 
                    id="orgSlug" 
                    defaultValue={userProfile?.org_id || ''} 
                    className="bg-white/5 border-white/10 font-mono text-sm" 
                    disabled
                  />
                </div>
              </div>
              <Button>Save Changes</Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}