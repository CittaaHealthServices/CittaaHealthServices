import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { adminService } from '../services/api'
import { 
  ArrowLeft, UserCheck, Activity, AlertTriangle,
  Mail, Phone, Calendar, CheckCircle, XCircle
} from 'lucide-react'

interface PendingUser {
  id: string
  email: string
  full_name: string
  phone: string
  age_range: string
  gender: string
  created_at: string
}

export default function PendingApprovals() {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [processingId, setProcessingId] = useState<string | null>(null)

  useEffect(() => {
    loadPendingApprovals()
  }, [])

  const loadPendingApprovals = async () => {
    try {
      setLoading(true)
      const data = await adminService.getPendingApprovals()
      setPendingUsers(data.pending_users || [])
    } catch (err) {
      setError('Failed to load pending approvals')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (userId: string) => {
    try {
      setProcessingId(userId)
      await adminService.approveParticipant(userId)
      setPendingUsers(prev => prev.filter(u => u.id !== userId))
    } catch (err) {
      console.error('Failed to approve participant:', err)
    } finally {
      setProcessingId(null)
    }
  }

  const handleReject = async (userId: string) => {
    try {
      setProcessingId(userId)
      await adminService.rejectParticipant(userId, 'Does not meet criteria')
      setPendingUsers(prev => prev.filter(u => u.id !== userId))
    } catch (err) {
      console.error('Failed to reject participant:', err)
    } finally {
      setProcessingId(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading pending approvals...</p>
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
          <h1 className="text-2xl font-bold text-gray-800">Pending Approvals</h1>
          <p className="text-sm text-gray-500">Review and approve clinical trial participants</p>
        </div>
      </div>

      {/* Stats */}
      <div className="bg-gradient-to-r from-warning/10 to-warning/5 rounded-xl p-4 border border-warning/20">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-warning/20 rounded-lg flex items-center justify-center">
            <UserCheck className="w-5 h-5 text-warning" />
          </div>
          <div>
            <p className="font-semibold text-gray-800">{pendingUsers.length} Pending Approvals</p>
            <p className="text-sm text-gray-500">Clinical trial participant requests awaiting review</p>
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

      {/* Pending Users List */}
      {pendingUsers.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center shadow-sm border border-gray-100">
          <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-800 mb-2">All Caught Up!</h3>
          <p className="text-gray-500">No pending approvals at the moment</p>
          <Link
            to="/admin/dashboard"
            className="inline-flex items-center mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {pendingUsers.map((user) => (
            <div
              key={user.id}
              className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start space-x-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-lg font-bold">
                      {user.full_name?.charAt(0) || user.email?.charAt(0) || 'U'}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">{user.full_name || 'Unknown'}</h3>
                    <div className="flex flex-wrap items-center gap-3 mt-1 text-sm text-gray-500">
                      <span className="flex items-center">
                        <Mail className="w-4 h-4 mr-1" />
                        {user.email}
                      </span>
                      {user.phone && (
                        <span className="flex items-center">
                          <Phone className="w-4 h-4 mr-1" />
                          {user.phone}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {user.age_range || 'Age N/A'}
                      </span>
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded capitalize">
                        {user.gender || 'Gender N/A'}
                      </span>
                      <span className="text-xs bg-primary-50 text-primary-600 px-2 py-1 rounded flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleReject(user.id)}
                    disabled={processingId === user.id}
                    className={`
                      flex items-center px-4 py-2 rounded-lg font-medium
                      border-2 border-error/30 text-error
                      hover:bg-error/10 transition-colors
                      ${processingId === user.id ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    Reject
                  </button>
                  <button
                    onClick={() => handleApprove(user.id)}
                    disabled={processingId === user.id}
                    className={`
                      flex items-center px-4 py-2 rounded-lg font-medium
                      bg-success text-white
                      hover:bg-success/90 transition-colors
                      ${processingId === user.id ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                  >
                    {processingId === user.id ? (
                      <Activity className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <CheckCircle className="w-4 h-4 mr-2" />
                    )}
                    Approve
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
        <h4 className="font-medium text-gray-800 mb-2">Approval Guidelines</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>- Verify participant meets age requirements (18+)</li>
          <li>- Ensure contact information is valid</li>
          <li>- Check for duplicate registrations</li>
          <li>- Approved participants will receive email notification</li>
        </ul>
      </div>
    </div>
  )
}
