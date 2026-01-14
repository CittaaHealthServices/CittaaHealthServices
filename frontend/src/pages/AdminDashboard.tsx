import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { adminService } from '../services/api'
import { 
  Users, UserCheck, Activity,
  ChevronRight, BarChart3, Shield, FileText, RefreshCw,
  Mail, Bell, Send, Settings, CheckCircle, XCircle
} from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

interface AuditLog {
  id: string
  action: string
  performed_by_email: string
  target_email?: string
  details?: Record<string, unknown>
  timestamp: string
}

interface Statistics {
  users: {
    total: number
    active: number
    by_role: Record<string, number>
  }
  clinical_trial: {
    total_participants: number
    approved: number
    pending: number
  }
  voice_analysis: {
    total_samples: number
    total_predictions: number
    recent_samples_7d: number
    recent_predictions_7d: number
  }
  risk_distribution: Record<string, number>
}

interface EmailSettings {
  reminder_enabled: boolean
  reminder_frequency: string
  reminder_time: string
  reminder_types: {
    daily_recording: boolean
    baseline_incomplete: boolean
    weekly_summary: boolean
  }
  notification_types: {
    registration: boolean
    trial_approval: boolean
    analysis_results: boolean
    high_risk_alert: boolean
  }
  smtp_configured: boolean
}

export default function AdminDashboard() {
  const { user } = useAuth()
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [, setError] = useState('')
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [logsLoading, setLogsLoading] = useState(false)
  const [emailSettings, setEmailSettings] = useState<EmailSettings | null>(null)
  const [emailLoading, setEmailLoading] = useState(false)
  const [sendingReminder, setSendingReminder] = useState(false)
  const [testEmailSending, setTestEmailSending] = useState(false)
  const [emailMessage, setEmailMessage] = useState<{type: 'success' | 'error', text: string} | null>(null)

  useEffect(() => {
    loadStatistics()
    loadAuditLogs()
    loadEmailSettings()
  }, [])

  const loadStatistics = async () => {
    try {
      setLoading(true)
      const data = await adminService.getStatistics()
      setStatistics(data)
    } catch (err) {
      setError('Failed to load statistics')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const loadAuditLogs = async () => {
    try {
      setLogsLoading(true)
      const data = await adminService.getAuditLogs(10, 0)
      setAuditLogs(data.logs || [])
    } catch (err) {
      console.error('Failed to load audit logs:', err)
    } finally {
      setLogsLoading(false)
    }
  }

  const loadEmailSettings = async () => {
    try {
      setEmailLoading(true)
      const data = await adminService.getEmailSettings()
      setEmailSettings(data)
    } catch (err) {
      console.error('Failed to load email settings:', err)
    } finally {
      setEmailLoading(false)
    }
  }

  const updateEmailSettings = async (newSettings: Partial<EmailSettings>) => {
    try {
      const updated = { ...emailSettings, ...newSettings }
      await adminService.updateEmailSettings(updated)
      setEmailSettings(updated as EmailSettings)
      setEmailMessage({ type: 'success', text: 'Email settings updated successfully' })
      setTimeout(() => setEmailMessage(null), 3000)
    } catch (err) {
      console.error('Failed to update email settings:', err)
      setEmailMessage({ type: 'error', text: 'Failed to update email settings' })
      setTimeout(() => setEmailMessage(null), 3000)
    }
  }

  const sendTestEmail = async (emailType: string) => {
    try {
      setTestEmailSending(true)
      const result = await adminService.sendTestEmail(emailType)
      if (result.success) {
        setEmailMessage({ type: 'success', text: result.message })
      } else {
        setEmailMessage({ type: 'error', text: result.message })
      }
      setTimeout(() => setEmailMessage(null), 5000)
    } catch (err) {
      console.error('Failed to send test email:', err)
      setEmailMessage({ type: 'error', text: 'Failed to send test email' })
      setTimeout(() => setEmailMessage(null), 3000)
    } finally {
      setTestEmailSending(false)
    }
  }

  const sendReminders = async (reminderType: string) => {
    try {
      setSendingReminder(true)
      // Get users for this reminder type and send emails
      const users = await adminService.getUsersForReminder(reminderType)
      setEmailMessage({ type: 'success', text: `Reminders queued for ${users.count} users` })
      setTimeout(() => setEmailMessage(null), 5000)
    } catch (err) {
      console.error('Failed to send reminders:', err)
      setEmailMessage({ type: 'error', text: 'Failed to send reminders' })
      setTimeout(() => setEmailMessage(null), 3000)
    } finally {
      setSendingReminder(false)
    }
  }

  const formatAction = (action: string) => {
    return action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Prepare chart data
  const roleData = statistics?.users?.by_role ? Object.entries(statistics.users.by_role).map(([role, count]) => ({
    name: role.replace('_', ' ').charAt(0).toUpperCase() + role.replace('_', ' ').slice(1),
    value: count
  })) : []

  const riskData = statistics?.risk_distribution ? Object.entries(statistics.risk_distribution).map(([level, count]) => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    value: count,
    color: level === 'low' ? '#27AE60' : level === 'moderate' ? '#F39C12' : level === 'high' ? '#E74C3C' : '#9CA3AF'
  })) : []

  const COLORS = ['#8B5A96', '#7BB3A8', '#FF8C42', '#27AE60', '#E74C3C']

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-6 text-white">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-xl font-display italic text-white/90">Cittaa</span>
          <span className="text-white/60">|</span>
          <span className="text-white/80">Vocalysis Admin</span>
        </div>
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <p className="mt-1 text-white/80">
          System overview and management for {user?.role === 'super_admin' ? 'Super Admin' : 'HR Admin'}
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Total Users</span>
            <Users className="w-5 h-5 text-primary-400" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-800">
            {statistics?.users?.total || 0}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            {statistics?.users?.active || 0} active
          </p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Pending Approvals</span>
            <UserCheck className="w-5 h-5 text-warning" />
          </div>
          <p className="mt-3 text-2xl font-bold text-warning">
            {statistics?.clinical_trial?.pending || 0}
          </p>
          <Link to="/admin/approvals" className="text-xs text-primary-500 hover:underline mt-1 inline-block">
            View pending
          </Link>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Voice Samples</span>
            <Activity className="w-5 h-5 text-secondary-400" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-800">
            {statistics?.voice_analysis?.total_samples || 0}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            +{statistics?.voice_analysis?.recent_samples_7d || 0} this week
          </p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Total Predictions</span>
            <BarChart3 className="w-5 h-5 text-accent-400" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-800">
            {statistics?.voice_analysis?.total_predictions || 0}
          </p>
          <p className="text-xs text-gray-400 mt-1">
            +{statistics?.voice_analysis?.recent_predictions_7d || 0} this week
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Users by Role */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-800 mb-4">Users by Role</h3>
          {roleData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={roleData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {roleData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-400">
              No user data available
            </div>
          )}
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-800 mb-4">Risk Distribution</h3>
          {riskData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={riskData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-400">
              No risk data available
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/admin/approvals"
            className="flex items-center p-4 rounded-lg border-2 border-dashed border-warning/30 hover:border-warning hover:bg-warning/5 transition-all duration-200"
          >
            <div className="w-12 h-12 bg-warning/10 rounded-lg flex items-center justify-center mr-4">
              <UserCheck className="w-6 h-6 text-warning" />
            </div>
            <div>
              <p className="font-medium text-gray-800">Pending Approvals</p>
              <p className="text-sm text-gray-500">{statistics?.clinical_trial?.pending || 0} waiting</p>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400 ml-auto" />
          </Link>

          <Link
            to="/admin/users"
            className="flex items-center p-4 rounded-lg border-2 border-dashed border-primary-200 hover:border-primary-400 hover:bg-primary-50 transition-all duration-200"
          >
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mr-4">
              <Users className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <p className="font-medium text-gray-800">User Management</p>
              <p className="text-sm text-gray-500">Manage all users</p>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400 ml-auto" />
          </Link>

          <div className="flex items-center p-4 rounded-lg border-2 border-dashed border-secondary-200 hover:border-secondary-400 hover:bg-secondary-50 transition-all duration-200 cursor-pointer">
            <div className="w-12 h-12 bg-secondary-100 rounded-lg flex items-center justify-center mr-4">
              <Shield className="w-6 h-6 text-secondary-500" />
            </div>
            <div>
              <p className="font-medium text-gray-800">System Settings</p>
              <p className="text-sm text-gray-500">Configure system</p>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400 ml-auto" />
          </div>
        </div>
      </div>

      {/* Clinical Trial Stats */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-6">
        <h3 className="font-semibold text-gray-800 mb-4">Clinical Trial Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-primary-600">
              {statistics?.clinical_trial?.total_participants || 0}
            </p>
            <p className="text-sm text-gray-600">Total Participants</p>
          </div>
          <div className="bg-white rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-success">
              {statistics?.clinical_trial?.approved || 0}
            </p>
            <p className="text-sm text-gray-600">Approved</p>
          </div>
          <div className="bg-white rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-warning">
              {statistics?.clinical_trial?.pending || 0}
            </p>
            <p className="text-sm text-gray-600">Pending Approval</p>
          </div>
        </div>
      </div>

      {/* Email Settings */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Mail className="w-5 h-5 text-primary-500" />
            <h3 className="font-semibold text-gray-800">Email & Reminder Settings</h3>
          </div>
          <div className="flex items-center space-x-2">
            {emailSettings?.smtp_configured ? (
              <span className="flex items-center text-xs text-green-600">
                <CheckCircle className="w-4 h-4 mr-1" />
                SMTP Configured
              </span>
            ) : (
              <span className="flex items-center text-xs text-red-500">
                <XCircle className="w-4 h-4 mr-1" />
                SMTP Not Configured
              </span>
            )}
          </div>
        </div>

        {emailMessage && (
          <div className={`mb-4 p-3 rounded-lg ${emailMessage.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {emailMessage.text}
          </div>
        )}

        {emailLoading ? (
          <div className="flex items-center justify-center py-8">
            <Activity className="w-8 h-8 text-primary-400 animate-spin" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Reminder Settings */}
            <div className="border-b border-gray-100 pb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
                <Bell className="w-4 h-4 mr-2" />
                Reminder Settings
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Reminders Enabled</label>
                  <button
                    onClick={() => updateEmailSettings({ reminder_enabled: !emailSettings?.reminder_enabled })}
                    className={`w-full px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      emailSettings?.reminder_enabled 
                        ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {emailSettings?.reminder_enabled ? 'Enabled' : 'Disabled'}
                  </button>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Frequency</label>
                  <select
                    value={emailSettings?.reminder_frequency || 'daily'}
                    onChange={(e) => updateEmailSettings({ reminder_frequency: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="twice_daily">Twice Daily</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Reminder Time</label>
                  <input
                    type="time"
                    value={emailSettings?.reminder_time || '09:00'}
                    onChange={(e) => updateEmailSettings({ reminder_time: e.target.value })}
                    className="w-full px-4 py-2 rounded-lg border border-gray-200 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Reminder Types */}
            <div className="border-b border-gray-100 pb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Reminder Types</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <label className="flex items-center space-x-2 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailSettings?.reminder_types?.daily_recording || false}
                    onChange={(e) => updateEmailSettings({ 
                      reminder_types: { ...emailSettings?.reminder_types, daily_recording: e.target.checked } as EmailSettings['reminder_types']
                    })}
                    className="w-4 h-4 text-primary-500 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Daily Recording Reminder</span>
                </label>
                <label className="flex items-center space-x-2 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailSettings?.reminder_types?.baseline_incomplete || false}
                    onChange={(e) => updateEmailSettings({ 
                      reminder_types: { ...emailSettings?.reminder_types, baseline_incomplete: e.target.checked } as EmailSettings['reminder_types']
                    })}
                    className="w-4 h-4 text-primary-500 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Baseline Incomplete</span>
                </label>
                <label className="flex items-center space-x-2 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailSettings?.reminder_types?.weekly_summary || false}
                    onChange={(e) => updateEmailSettings({ 
                      reminder_types: { ...emailSettings?.reminder_types, weekly_summary: e.target.checked } as EmailSettings['reminder_types']
                    })}
                    className="w-4 h-4 text-primary-500 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Weekly Summary</span>
                </label>
              </div>
            </div>

            {/* Notification Types */}
            <div className="border-b border-gray-100 pb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Notification Types</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <label className="flex items-center space-x-2 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailSettings?.notification_types?.registration || false}
                    onChange={(e) => updateEmailSettings({ 
                      notification_types: { ...emailSettings?.notification_types, registration: e.target.checked } as EmailSettings['notification_types']
                    })}
                    className="w-4 h-4 text-primary-500 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Registration</span>
                </label>
                <label className="flex items-center space-x-2 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailSettings?.notification_types?.trial_approval || false}
                    onChange={(e) => updateEmailSettings({ 
                      notification_types: { ...emailSettings?.notification_types, trial_approval: e.target.checked } as EmailSettings['notification_types']
                    })}
                    className="w-4 h-4 text-primary-500 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Trial Approval</span>
                </label>
                <label className="flex items-center space-x-2 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailSettings?.notification_types?.analysis_results || false}
                    onChange={(e) => updateEmailSettings({ 
                      notification_types: { ...emailSettings?.notification_types, analysis_results: e.target.checked } as EmailSettings['notification_types']
                    })}
                    className="w-4 h-4 text-primary-500 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Analysis Results</span>
                </label>
                <label className="flex items-center space-x-2 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailSettings?.notification_types?.high_risk_alert || false}
                    onChange={(e) => updateEmailSettings({ 
                      notification_types: { ...emailSettings?.notification_types, high_risk_alert: e.target.checked } as EmailSettings['notification_types']
                    })}
                    className="w-4 h-4 text-primary-500 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">High Risk Alert</span>
                </label>
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => sendTestEmail('welcome')}
                disabled={testEmailSending}
                className="flex items-center px-4 py-2 bg-primary-100 text-primary-700 rounded-lg text-sm font-medium hover:bg-primary-200 transition-colors disabled:opacity-50"
              >
                <Send className="w-4 h-4 mr-2" />
                {testEmailSending ? 'Sending...' : 'Send Test Email'}
              </button>
              <button
                onClick={() => sendReminders('daily_recording')}
                disabled={sendingReminder}
                className="flex items-center px-4 py-2 bg-secondary-100 text-secondary-700 rounded-lg text-sm font-medium hover:bg-secondary-200 transition-colors disabled:opacity-50"
              >
                <Bell className="w-4 h-4 mr-2" />
                {sendingReminder ? 'Sending...' : 'Send Daily Reminders Now'}
              </button>
              <button
                onClick={loadEmailSettings}
                className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh Settings
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Audit Logs */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-primary-500" />
            <h3 className="font-semibold text-gray-800">Recent Audit Logs</h3>
          </div>
          <button
            onClick={loadAuditLogs}
            disabled={logsLoading}
            className="flex items-center space-x-1 text-sm text-primary-500 hover:text-primary-600 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${logsLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
        
        {logsLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-pulse flex flex-col items-center">
              <Activity className="w-8 h-8 text-primary-400 animate-spin" />
              <p className="mt-2 text-sm text-gray-500">Loading logs...</p>
            </div>
          </div>
        ) : auditLogs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-2 font-medium text-gray-600">Action</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-600">Performed By</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-600">Target</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-600">Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-2">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        log.action === 'user_created' ? 'bg-green-100 text-green-700' :
                        log.action === 'password_reset' ? 'bg-blue-100 text-blue-700' :
                        log.action === 'role_changed' ? 'bg-purple-100 text-purple-700' :
                        log.action === 'reminders_sent' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {formatAction(log.action)}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-gray-700">{log.performed_by_email}</td>
                    <td className="py-3 px-2 text-gray-500">{log.target_email || '-'}</td>
                    <td className="py-3 px-2 text-gray-500">{formatTimestamp(log.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No audit logs yet</p>
            <p className="text-sm">Actions like user creation and password resets will appear here</p>
          </div>
        )}
      </div>
    </div>
  )
}
