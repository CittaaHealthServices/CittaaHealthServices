import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { adminService } from '../services/api'
import { 
  Users, UserCheck, Activity,
  ChevronRight, BarChart3, Shield, FileText, RefreshCw
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

export default function AdminDashboard() {
  const { user } = useAuth()
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [, setError] = useState('')
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [logsLoading, setLogsLoading] = useState(false)

  useEffect(() => {
    loadStatistics()
    loadAuditLogs()
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
