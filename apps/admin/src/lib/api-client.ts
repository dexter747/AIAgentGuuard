/**
 * API Client for Admin Dashboard
 */
import axios from 'axios'

// IMPORTANT: Always use HTTPS in production
const API_URL = (() => {
  let url = process.env.NEXT_PUBLIC_API_URL || 'https://api.overseex.com'
  
  // Force HTTPS when on HTTPS page (prevent mixed content errors)
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    url = url.replace('http://', 'https://')
  }
  
  return url
})()

class AdminAPIClient {
  private token: string | null = null

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('admin_token')
    }
  }

  private getHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    }
  }

  setToken(token: string) {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('admin_token', token)
    }
  }

  clearToken() {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
    }
  }

  // Auth
  async login(email: string, password: string) {
    const response = await axios.post(`${API_URL}/api/v1/auth/login`, {
      email,
      password
    }, {
      headers: { 'Content-Type': 'application/json' }
    })

    if (response.data.user && !response.data.user.is_admin) {
      throw new Error('Admin access required')
    }

    this.setToken(response.data.access_token)
    return response.data
  }

  async getCurrentUser() {
    const response = await axios.get(`${API_URL}/api/v1/users/me`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Dashboard
  async getDashboardStats() {
    const response = await axios.get(`${API_URL}/api/v1/admin/stats`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getSystemStatus() {
    const response = await axios.get(`${API_URL}/api/v1/admin/system-status`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getActivityLogs(limit = 10) {
    const response = await axios.get(`${API_URL}/api/v1/admin/activity?limit=${limit}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getLogs(params?: { limit?: number; offset?: number; level?: string }) {
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', params.limit.toString())
    if (params?.offset) query.append('offset', params.offset.toString())
    if (params?.level) query.append('level', params.level)

    const response = await axios.get(`${API_URL}/api/v1/admin/logs?${query}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getApiKeys(params?: { limit?: number; offset?: number }) {
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', params.limit.toString())
    if (params?.offset) query.append('offset', params.offset.toString())

    const response = await axios.get(`${API_URL}/api/v1/admin/api-keys?${query}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getAgents(params?: { limit?: number; offset?: number }) {
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', params.limit.toString())
    if (params?.offset) query.append('offset', params.offset.toString())

    const response = await axios.get(`${API_URL}/api/v1/admin/agents?${query}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getAnalytics() {
    const response = await axios.get(`${API_URL}/api/v1/admin/analytics`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Users
  async listUsers(params?: { limit?: number; offset?: number; search?: string; status?: string }) {
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', params.limit.toString())
    if (params?.offset) query.append('offset', params.offset.toString())
    if (params?.search) query.append('search', params.search)
    if (params?.status) query.append('status', params.status)

    const response = await axios.get(`${API_URL}/api/v1/admin/users?${query}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getUser(userId: string) {
    const response = await axios.get(`${API_URL}/api/v1/admin/users/${userId}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async updateUser(userId: string, data: any) {
    const query = new URLSearchParams()
    if (data.name) query.append('name', data.name)
    if (data.full_name) query.append('name', data.full_name)
    if (data.is_active !== undefined) query.append('is_active', data.is_active.toString())
    if (data.is_admin !== undefined) query.append('role', data.is_admin ? 'admin' : 'user')
    if (data.role) query.append('role', data.role)

    const response = await axios.put(`${API_URL}/api/v1/admin/users/${userId}?${query}`, {}, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async deleteUser(userId: string) {
    const response = await axios.delete(`${API_URL}/api/v1/admin/users/${userId}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Organizations
  async listOrganizations(params?: { limit?: number; offset?: number }) {
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', params.limit.toString())
    if (params?.offset) query.append('offset', params.offset.toString())

    const response = await axios.get(`${API_URL}/api/v1/admin/organizations?${query}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getOrganization(orgId: string) {
    const response = await axios.get(`${API_URL}/api/v1/admin/organizations/${orgId}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async updateOrganization(orgId: string, data: any) {
    const query = new URLSearchParams()
    if (data.name) query.append('name', data.name)
    if (data.plan) query.append('plan', data.plan)

    const response = await axios.put(`${API_URL}/api/v1/admin/organizations/${orgId}?${query}`, {}, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async deleteOrganization(orgId: string) {
    const response = await axios.delete(`${API_URL}/api/v1/admin/organizations/${orgId}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Billing
  async getBillingStats() {
    const response = await axios.get(`${API_URL}/api/v1/admin/billing`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async getSubscriptions(params?: { limit?: number; offset?: number }) {
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', params.limit.toString())
    if (params?.offset) query.append('offset', params.offset.toString())

    const response = await axios.get(`${API_URL}/api/v1/admin/subscriptions?${query}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Email Management
  async listEmails(params?: { limit?: number; offset?: number; status?: string }) {
    const query = new URLSearchParams()
    if (params?.limit) query.append('limit', params.limit.toString())
    if (params?.offset) query.append('offset', params.offset.toString())
    if (params?.status) query.append('status', params.status)

    const response = await axios.get(`${API_URL}/api/v1/admin/emails?${query}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async sendTestEmail(to: string, template: string) {
    const response = await axios.post(`${API_URL}/api/v1/admin/emails/test`, {
      to,
      template
    }, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Settings
  async getSettings() {
    const response = await axios.get(`${API_URL}/api/v1/admin/settings`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async updateSettings(settings: any) {
    const response = await axios.put(`${API_URL}/api/v1/admin/settings`, settings, {
      headers: this.getHeaders()
    })
    return response.data
  }

  // Contact Queries
  async getContactQueries(unreadOnly = false) {
    const response = await axios.get(`${API_URL}/api/v1/contact/queries?unread_only=${unreadOnly}`, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async markContactQueryAsRead(queryId: string) {
    const response = await axios.patch(`${API_URL}/api/v1/contact/queries/${queryId}/read`, {}, {
      headers: this.getHeaders()
    })
    return response.data
  }

  async deleteContactQuery(queryId: string) {
    const response = await axios.delete(`${API_URL}/api/v1/contact/queries/${queryId}`, {
      headers: this.getHeaders()
    })
    return response.data
  }
}

export const apiClient = new AdminAPIClient()
export default apiClient
