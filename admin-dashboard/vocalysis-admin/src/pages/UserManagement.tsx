import { useState } from 'react'
import { 
  Search, 
  Filter,
  MoreVertical,
  Mail,
  Shield,
  User,
  Crown,
  Building,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'

interface UserData {
  id: string
  name: string
  email: string
  phone: string
  role: 'patient' | 'psychologist' | 'admin' | 'premium_user' | 'corporate_user'
  subscription: string
  status: 'active' | 'inactive' | 'suspended'
  platform: 'iOS' | 'Android' | 'Web'
  lastActive: string
  createdAt: string
  voiceAnalyses: number
}

const mockUsers: UserData[] = [
  { id: 'U001', name: 'Rahul Sharma', email: 'rahul.s@email.com', phone: '+91 98765 43210', role: 'premium_user', subscription: 'Premium Individual', status: 'active', platform: 'iOS', lastActive: '2 hours ago', createdAt: '2024-01-15', voiceAnalyses: 45 },
  { id: 'U002', name: 'Dr. Meera Krishnan', email: 'meera.k@cittaa.in', phone: '+91 87654 32109', role: 'psychologist', subscription: 'Staff', status: 'active', platform: 'Web', lastActive: '30 min ago', createdAt: '2023-11-01', voiceAnalyses: 0 },
  { id: 'U003', name: 'Priya Patel', email: 'priya.p@email.com', phone: '+91 76543 21098', role: 'patient', subscription: 'Free Trial', status: 'active', platform: 'Android', lastActive: '1 day ago', createdAt: '2024-01-20', voiceAnalyses: 12 },
  { id: 'U004', name: 'Admin User', email: 'admin@cittaa.in', phone: '+91 65432 10987', role: 'admin', subscription: 'Staff', status: 'active', platform: 'Web', lastActive: 'Just now', createdAt: '2023-06-01', voiceAnalyses: 0 },
  { id: 'U005', name: 'TechCorp HR', email: 'hr@techcorp.com', phone: '+91 54321 09876', role: 'corporate_user', subscription: 'Corporate', status: 'active', platform: 'Web', lastActive: '5 hours ago', createdAt: '2024-01-10', voiceAnalyses: 234 },
  { id: 'U006', name: 'Amit Kumar', email: 'amit.k@email.com', phone: '+91 43210 98765', role: 'premium_user', subscription: 'Premium Plus', status: 'inactive', platform: 'iOS', lastActive: '1 week ago', createdAt: '2023-12-01', voiceAnalyses: 89 },
  { id: 'U007', name: 'Sneha Reddy', email: 'sneha.r@email.com', phone: '+91 32109 87654', role: 'patient', subscription: 'Free', status: 'suspended', platform: 'Android', lastActive: '2 weeks ago', createdAt: '2024-01-05', voiceAnalyses: 3 },
]

export function UserManagement() {
  const [users] = useState(mockUsers)
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRole = roleFilter === 'all' || user.role === roleFilter
    const matchesStatus = statusFilter === 'all' || user.status === statusFilter
    return matchesSearch && matchesRole && matchesStatus
  })

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin': return <Shield className="w-4 h-4 text-red-500" />
      case 'psychologist': return <User className="w-4 h-4 text-blue-500" />
      case 'premium_user': return <Crown className="w-4 h-4 text-yellow-500" />
      case 'corporate_user': return <Building className="w-4 h-4 text-purple-500" />
      default: return <User className="w-4 h-4 text-gray-500" />
    }
  }

  const getRoleBadge = (role: string) => {
    const styles: Record<string, string> = {
      admin: 'bg-red-100 text-red-700',
      psychologist: 'bg-blue-100 text-blue-700',
      premium_user: 'bg-yellow-100 text-yellow-700',
      corporate_user: 'bg-purple-100 text-purple-700',
      patient: 'bg-gray-100 text-gray-700'
    }
    return styles[role] || styles.patient
  }

  const totalUsers = users.length
  const activeUsers = users.filter(u => u.status === 'active').length
  const premiumUsers = users.filter(u => u.role === 'premium_user' || u.role === 'corporate_user').length

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600 mt-1">Manage all users across platforms</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-600">Total Users</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{totalUsers}</p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-600">Active Users</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{activeUsers}</p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-600">Premium Users</p>
          <p className="text-2xl font-bold text-yellow-600 mt-1">{premiumUsers}</p>
        </div>
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <p className="text-sm text-gray-600">Total Analyses</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{users.reduce((sum, u) => sum + u.voiceAnalyses, 0)}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-6">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500"
            >
              <option value="all">All Roles</option>
              <option value="patient">Patient</option>
              <option value="premium_user">Premium User</option>
              <option value="corporate_user">Corporate User</option>
              <option value="psychologist">Psychologist</option>
              <option value="admin">Admin</option>
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="suspended">Suspended</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">User</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Role</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Subscription</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Platform</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Analyses</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Status</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Last Active</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredUsers.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <span className="text-green-700 font-medium">{user.name.charAt(0)}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{user.name}</p>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Mail className="w-3 h-3" />
                        <span>{user.email}</span>
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${getRoleBadge(user.role)}`}>
                    {getRoleIcon(user.role)}
                    {user.role.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-900">{user.subscription}</span>
                </td>
                <td className="px-6 py-4">
                  <span className={`text-sm ${
                    user.platform === 'iOS' ? 'text-blue-600' :
                    user.platform === 'Android' ? 'text-green-600' :
                    'text-gray-600'
                  }`}>
                    {user.platform}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm font-medium text-gray-900">{user.voiceAnalyses}</span>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                    user.status === 'active' ? 'bg-green-100 text-green-700' :
                    user.status === 'inactive' ? 'bg-gray-100 text-gray-600' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {user.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-500">{user.lastActive}</span>
                </td>
                <td className="px-6 py-4">
                  <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Showing {filteredUsers.length} of {users.length} users
          </p>
          <div className="flex items-center gap-2">
            <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 bg-green-600 text-white rounded-lg text-sm">1</span>
            <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
