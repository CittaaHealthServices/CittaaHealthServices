import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { adminService } from '../services/api'
import { 
  ArrowLeft, Users, Search, Filter, Activity, AlertTriangle,
  MoreVertical, UserPlus, X, Plus
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
  assigned_psychologist_id?: string
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [totalUsers, setTotalUsers] = useState(0)
  const [selectedUser, setSelectedUser] = useState<string | null>(null)
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [assigningPatient, setAssigningPatient] = useState<User | null>(null)
  const [psychologists, setPsychologists] = useState<User[]>([])
  const [selectedPsychologist, setSelectedPsychologist] = useState<string>('')
  const [assignLoading, setAssignLoading] = useState(false)
  
  // Add User Modal State
  const [showAddUserModal, setShowAddUserModal] = useState(false)
  const [addUserLoading, setAddUserLoading] = useState(false)
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'patient',
    phone: ''
  })

  useEffect(() => {
    loadUsers()
  }, [roleFilter])

  useEffect(() => {
    // Load psychologists for assignment modal
    const loadPsychologists = async () => {
      try {
        const data = await adminService.getAllUsers('psychologist', 100, 0)
        setPsychologists(data.users || [])
      } catch (err) {
        console.error('Failed to load psychologists:', err)
      }
    }
    loadPsychologists()
  }, [])

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
      } catch (err) {
        console.error('Failed to deactivate user:', err)
      }
    }

    const openAssignModal = (patient: User) => {
      setAssigningPatient(patient)
      setSelectedPsychologist('')
      setShowAssignModal(true)
      setSelectedUser(null)
    }

    const handleAssignPsychologist = async () => {
      if (!assigningPatient || !selectedPsychologist) return
    
      try {
        setAssignLoading(true)
        await adminService.assignPsychologist(assigningPatient.id, selectedPsychologist)
        setShowAssignModal(false)
        setAssigningPatient(null)
        setSelectedPsychologist('')
        loadUsers()
      } catch (err) {
        console.error('Failed to assign psychologist:', err)
        setError('Failed to assign psychologist')
      } finally {
        setAssignLoading(false)
      }
    }

    const handleAddUser = async () => {
      if (!newUser.email || !newUser.password || !newUser.full_name) {
        setError('Please fill in all required fields')
        return
      }
    
      try {
        setAddUserLoading(true)
        setError('')
        await adminService.createUser(newUser)
        setShowAddUserModal(false)
        setNewUser({ email: '', password: '', full_name: '', role: 'patient', phone: '' })
        loadUsers()
      } catch (err: any) {
        console.error('Failed to create user:', err)
        setError(err.response?.data?.detail || 'Failed to create user')
      } finally {
        setAddUserLoading(false)
      }
    }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin': return 'bg-error/10 text-error'
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
              <option value="hr_admin">HR Admin</option>
              <option value="super_admin">Super Admin</option>
              <option value="researcher">Researcher</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 rounded-xl p-4 border border-red-200 flex items-center space-x-2 text-red-600">
          <AlertTriangle className="w-5 h-5" />
          <span>{error}</span>
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
                                                            {['patient', 'psychologist', 'hr_admin', 'researcher'].map((role) => (
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
                                                            {user.role === 'patient' && (
                                                              <div className="border-t border-gray-100 mt-1 pt-1">
                                                                <button
                                                                  onClick={() => openAssignModal(user)}
                                                                  className="w-full text-left px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 flex items-center space-x-2"
                                                                >
                                                                  <UserPlus className="w-4 h-4" />
                                                                  <span>Assign Psychologist</span>
                                                                </button>
                                                              </div>
                                                            )}
                                                            <div className="border-t border-gray-100 mt-1 pt-1">
                                                              <button
                                                                onClick={() => handleDeactivate(user.id)}
                                                                className="w-full text-left px-3 py-2 text-sm text-error hover:bg-red-50"
                                                              >
                                                                Deactivate User
                                                              </button>
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

      {/* Add User Button */}
      <div className="fixed bottom-6 right-6">
        <button
          onClick={() => setShowAddUserModal(true)}
          className="bg-primary-500 text-white p-4 rounded-full shadow-lg hover:bg-primary-600 transition-all hover:scale-105 flex items-center space-x-2"
        >
          <Plus className="w-6 h-6" />
          <span className="pr-2">Add User</span>
        </button>
      </div>

      {/* Add User Modal */}
      {showAddUserModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 animate-slideUp">
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <h3 className="text-lg font-semibold text-gray-800">Add New User</h3>
              <button
                onClick={() => setShowAddUserModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                <input
                  type="text"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter full name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter email address"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter password"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Role *</label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="patient">Patient</option>
                  <option value="psychologist">Psychologist</option>
                  <option value="hr_admin">HR Admin</option>
                  <option value="researcher">Researcher</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone (Optional)</label>
                <input
                  type="tel"
                  value={newUser.phone}
                  onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Enter phone number"
                />
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 p-4 border-t border-gray-100">
              <button
                onClick={() => setShowAddUserModal(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAddUser}
                disabled={addUserLoading || !newUser.email || !newUser.password || !newUser.full_name}
                className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {addUserLoading ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    <span>Creating...</span>
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    <span>Create User</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Assign Psychologist Modal */}
      {showAssignModal && assigningPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 animate-slideUp">
            <div className="flex items-center justify-between p-4 border-b border-gray-100">
              <h3 className="text-lg font-semibold text-gray-800">Assign Psychologist</h3>
              <button
                onClick={() => setShowAssignModal(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="p-4 space-y-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm text-gray-500">Assigning psychologist to:</p>
                <p className="font-medium text-gray-800">{assigningPatient.full_name || assigningPatient.email}</p>
                <p className="text-sm text-gray-500">{assigningPatient.email}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Psychologist
                </label>
                <select
                  value={selectedPsychologist}
                  onChange={(e) => setSelectedPsychologist(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Choose a psychologist...</option>
                  {psychologists.map((psych) => (
                    <option key={psych.id} value={psych.id}>
                      {psych.full_name || psych.email}
                    </option>
                  ))}
                </select>
              </div>
              
              {psychologists.length === 0 && (
                <p className="text-sm text-warning text-center">
                  No psychologists available. Please add psychologist users first.
                </p>
              )}
            </div>
            
            <div className="flex items-center justify-end space-x-3 p-4 border-t border-gray-100">
              <button
                onClick={() => setShowAssignModal(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAssignPsychologist}
                disabled={!selectedPsychologist || assignLoading}
                className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {assignLoading ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    <span>Assigning...</span>
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" />
                    <span>Assign</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
