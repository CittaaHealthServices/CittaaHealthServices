import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { adminService } from '../services/api'
import { 
  ArrowLeft, Users, Search, Filter, Activity, AlertTriangle,
  MoreVertical, UserPlus, X, RefreshCw, Key
} from 'lucide-react'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  is_clinical_trial_participant: boolean
  trial_status: string
  created_at: string
  last_login: string
}

interface CreateUserForm {
  email: string
  full_name: string
  role: string
  phone: string
  send_welcome_email: boolean
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [totalUsers, setTotalUsers] = useState(0)
  const [selectedUser, setSelectedUser] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [createForm, setCreateForm] = useState<CreateUserForm>({
    email: '',
    full_name: '',
    role: 'patient',
    phone: '',
    send_welcome_email: true
  })

  useEffect(() => {
    loadUsers()
  }, [roleFilter])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const data = await adminService.getAllUsers(roleFilter || undefined, 100, 0)
      setUsers(data.users || [])
      setTotalUsers(data.total || 0)
    } catch (err) {
      setError('Failed to load users')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await adminService.updateUserRole(userId, newRole)
      loadUsers()
      setSelectedUser(null)
    } catch (err) {
      console.error('Failed to update role:', err)
    }
  }

  const handleDeactivate = async (userId: string) => {
    try {
      await adminService.deactivateUser(userId)
      loadUsers()
      setSelectedUser(null)
      setSuccess('User deactivated successfully')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      console.error('Failed to deactivate user:', err)
      setError('Failed to deactivate user')
    }
  }

  const handleReactivate = async (userId: string) => {
    try {
      await adminService.reactivateUser(userId)
      loadUsers()
      setSelectedUser(null)
      setSuccess('User reactivated successfully')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      console.error('Failed to reactivate user:', err)
      setError('Failed to reactivate user')
    }
  }

  const handleResetPassword = async (userId: string) => {
    try {
      const result = await adminService.resetUserPassword(userId)
      setSuccess(`Password reset successfully. New password: ${result.temporary_password}`)
      setSelectedUser(null)
      setTimeout(() => setSuccess(''), 10000) // Keep visible longer for password
    } catch (err) {
      console.error('Failed to reset password:', err)
      setError('Failed to reset password')
    }
  }

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setError('')
    try {
      const result = await adminService.createUser(createForm)
      setSuccess(`User created successfully! Temporary password: ${result.temporary_password}`)
      setShowCreateModal(false)
      setCreateForm({
        email: '',
        full_name: '',
        role: 'patient',
        phone: '',
        send_welcome_email: true
      })
      loadUsers()
      setTimeout(() => setSuccess(''), 10000) // Keep visible longer for password
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create user')
    } finally {
      setCreating(false)
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin': return 'bg-error/10 text-error'
      case 'admin': return 'bg-error/10 text-error'
      case 'hr_admin': return 'bg-warning/10 text-warning'
      case 'psychologist': return 'bg-primary-100 text-primary-600'
      case 'researcher': return 'bg-secondary-100 text-secondary-600'
      default: return 'bg-gray-100 text-gray-600'
    }
  }

  const filteredUsers = users.filter(user => {
    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      return (
        user.email?.toLowerCase().includes(search) ||
        user.full_name?.toLowerCase().includes(search)
      )
    }
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading users...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link 
            to="/admin/dashboard" 
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">User Management</h1>
            <p className="text-sm text-gray-500">Manage all system users and their roles</p>
          </div>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:opacity-90 transition-opacity"
        >
          <UserPlus className="w-5 h-5" />
          <span>Create User</span>
        </button>
      </div>

      {/* Stats */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Users className="w-5 h-5 text-primary-500" />
          </div>
          <div>
            <p className="font-semibold text-gray-800">{totalUsers} Total Users</p>
            <p className="text-sm text-gray-500">Across all roles</p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Roles</option>
              <option value="patient">Patient</option>
              <option value="psychologist">Psychologist</option>
              <option value="admin">Admin</option>
              <option value="hr_admin">HR Admin</option>
              <option value="super_admin">Super Admin</option>
              <option value="researcher">Researcher</option>
            </select>
          </div>
        </div>
      </div>

      {/* Success */}
      {success && (
        <div className="bg-green-50 rounded-xl p-4 border border-green-200 flex items-center space-x-2 text-green-600 animate-fadeIn">
          <Activity className="w-5 h-5" />
          <span>{success}</span>
          <button onClick={() => setSuccess('')} className="ml-auto">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 rounded-xl p-4 border border-red-200 flex items-center space-x-2 text-red-600 animate-fadeIn">
          <AlertTriangle className="w-5 h-5" />
          <span>{error}</span>
          <button onClick={() => setError('')} className="ml-auto">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                    No users found
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-white font-medium">
                            {user.full_name?.charAt(0) || user.email?.charAt(0) || 'U'}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {user.full_name || 'Unknown'}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded capitalize ${getRoleColor(user.role)}`}>
                        {user.role?.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.is_active ? (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-success/10 text-success">
                          <span className="w-1.5 h-1.5 bg-success rounded-full mr-1.5"></span>
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-500">
                          <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-1.5"></span>
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.last_login 
                        ? new Date(user.last_login).toLocaleDateString()
                        : 'Never'
                      }
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="relative">
                        <button
                          onClick={() => setSelectedUser(selectedUser === user.id ? null : user.id)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <MoreVertical className="w-4 h-4 text-gray-500" />
                        </button>
                        
                        {selectedUser === user.id && (
                          <>
                            <div 
                              className="fixed inset-0 z-10"
                              onClick={() => setSelectedUser(null)}
                            />
                            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-20 animate-fadeIn">
                              <div className="px-3 py-2 border-b border-gray-100">
                                <p className="text-xs text-gray-500">Change Role</p>
                              </div>
                              {['patient', 'psychologist', 'admin', 'hr_admin', 'researcher'].map((role) => (
                                <button
                                  key={role}
                                  onClick={() => handleRoleChange(user.id, role)}
                                  className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 capitalize ${
                                    user.role === role ? 'text-primary-500 font-medium' : 'text-gray-700'
                                  }`}
                                >
                                  {role.replace('_', ' ')}
                                </button>
                              ))}
                              <div className="border-t border-gray-100 mt-1 pt-1">
                                <button
                                  onClick={() => handleResetPassword(user.id)}
                                  className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                                >
                                  <Key className="w-4 h-4" />
                                  <span>Reset Password</span>
                                </button>
                                {user.is_active ? (
                                  <button
                                    onClick={() => handleDeactivate(user.id)}
                                    className="w-full text-left px-3 py-2 text-sm text-error hover:bg-red-50"
                                  >
                                    Deactivate User
                                  </button>
                                ) : (
                                  <button
                                    onClick={() => handleReactivate(user.id)}
                                    className="w-full text-left px-3 py-2 text-sm text-success hover:bg-green-50"
                                  >
                                    Reactivate User
                                  </button>
                                )}
                              </div>
                            </div>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 animate-slideUp">
            <div className="flex items-center justify-between p-6 border-b border-gray-100">
              <h2 className="text-xl font-semibold text-gray-800">Create New User</h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <form onSubmit={handleCreateUser} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={createForm.full_name}
                  onChange={(e) => setCreateForm({...createForm, full_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter full name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address *
                </label>
                <input
                  type="email"
                  required
                  value={createForm.email}
                  onChange={(e) => setCreateForm({...createForm, email: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter email address"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  value={createForm.phone}
                  onChange={(e) => setCreateForm({...createForm, phone: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter phone number"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role *
                </label>
                <select
                  value={createForm.role}
                  onChange={(e) => setCreateForm({...createForm, role: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="patient">Patient</option>
                  <option value="psychologist">Psychologist</option>
                  <option value="admin">Admin</option>
                  <option value="hr_admin">HR Admin</option>
                  <option value="researcher">Researcher</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="send_welcome_email"
                  checked={createForm.send_welcome_email}
                  onChange={(e) => setCreateForm({...createForm, send_welcome_email: e.target.checked})}
                  className="w-4 h-4 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
                />
                <label htmlFor="send_welcome_email" className="text-sm text-gray-700">
                  Send welcome email with login credentials
                </label>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {creating ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Creating...</span>
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-4 h-4" />
                      <span>Create User</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
