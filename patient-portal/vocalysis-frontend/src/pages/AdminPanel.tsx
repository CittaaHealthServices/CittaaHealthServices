import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  Users, 
  UserCheck, 
  UserX, 
  Calendar, 
  Activity, 
  Settings,
  Search,
  Filter,
  Download,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  BarChart3,
  PieChart
} from 'lucide-react'
import axios from 'axios'

interface Participant {
  id: string
  user_id: string
  age: number
  gender: string
  phone: string
  institution: string
  consent_given: boolean
  consent_timestamp: string
  medical_history?: string
  current_medications?: string
  emergency_contact_name: string
  emergency_contact_phone: string
  preferred_language: string
  enrollment_date: string
  trial_status: string
  approval_status: string
  approved_by?: string
  approval_date?: string
  rejection_reason?: string
  voice_samples_collected: number
  target_samples: number
  baseline_established: boolean
  assigned_psychologist?: string
  assignment_date?: string
  clinical_notes?: string
  created_at: string
  updated_at: string
}

interface AdminStats {
  totalParticipants: number
  pendingApprovals: number
  activeTrials: number
  completedAnalyses: number
}

export default function AdminPanel() {
  const { user } = useAuth()
  const [participants, setParticipants] = useState<Participant[]>([])
  const [pendingParticipants, setPendingParticipants] = useState<Participant[]>([])
  const [stats, setStats] = useState<AdminStats>({
    totalParticipants: 0,
    pendingApprovals: 0,
    activeTrials: 0,
    completedAnalyses: 0
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'overview' | 'approvals' | 'participants' | 'analytics'>('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedParticipant, setSelectedParticipant] = useState<Participant | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [pendingRes] = await Promise.all([
        axios.get('/api/v1/participants/pending')
      ])

      setPendingParticipants(pendingRes.data)
      
      setStats({
        totalParticipants: pendingRes.data.length,
        pendingApprovals: pendingRes.data.filter((p: Participant) => p.approval_status === 'pending').length,
        activeTrials: pendingRes.data.filter((p: Participant) => p.trial_status === 'active').length,
        completedAnalyses: 0 // Would need to fetch from voice analysis reports
      })
    } catch (error) {
      console.error('Failed to fetch data:', error)
      setError('Failed to load admin data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const approveParticipant = async (participantId: string) => {
    setActionLoading(participantId)
    try {
      await axios.put(`/api/v1/participants/${participantId}/approve`)
      await fetchData()
      setShowModal(false)
      setSelectedParticipant(null)
    } catch (error) {
      console.error('Failed to approve participant:', error)
      setError('Failed to approve participant. Please try again.')
    } finally {
      setActionLoading(null)
    }
  }

  const rejectParticipant = async (participantId: string, reason: string) => {
    setActionLoading(participantId)
    try {
      await axios.put(`/api/v1/participants/${participantId}/reject`, { reason })
      await fetchData()
      setShowModal(false)
      setSelectedParticipant(null)
    } catch (error) {
      console.error('Failed to reject participant:', error)
      setError('Failed to reject participant. Please try again.')
    } finally {
      setActionLoading(null)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-600 bg-yellow-50'
      case 'approved':
        return 'text-green-600 bg-green-50'
      case 'rejected':
        return 'text-red-600 bg-red-50'
      case 'active':
        return 'text-blue-600 bg-blue-50'
      case 'completed':
        return 'text-gray-600 bg-gray-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const filteredParticipants = pendingParticipants.filter(participant =>
    participant.user_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    participant.institution.toLowerCase().includes(searchTerm.toLowerCase()) ||
    participant.emergency_contact_name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Admin Panel</h1>
        <p className="text-indigo-100">
          Manage clinical trial participants and system settings
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Participants</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalParticipants}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Approvals</p>
              <p className="text-3xl font-bold text-gray-900">{stats.pendingApprovals}</p>
            </div>
            <div className="p-3 bg-yellow-50 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Trials</p>
              <p className="text-3xl font-bold text-gray-900">{stats.activeTrials}</p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Completed Analyses</p>
              <p className="text-3xl font-bold text-gray-900">{stats.completedAnalyses}</p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <Calendar className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('approvals')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'approvals'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Pending Approvals ({stats.pendingApprovals})
            </button>
            <button
              onClick={() => setActiveTab('participants')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'participants'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              All Participants
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'analytics'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Analytics
            </button>
          </nav>
        </div>

        <div className="p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    <div className="flex items-center text-sm">
                      <UserCheck className="w-4 h-4 text-green-600 mr-2" />
                      <span className="text-gray-600">3 participants approved today</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <Users className="w-4 h-4 text-blue-600 mr-2" />
                      <span className="text-gray-600">5 new registrations this week</span>
                    </div>
                    <div className="flex items-center text-sm">
                      <Activity className="w-4 h-4 text-purple-600 mr-2" />
                      <span className="text-gray-600">12 voice analyses completed</span>
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Database Status</span>
                      <span className="flex items-center text-green-600">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Healthy
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">API Response Time</span>
                      <span className="text-gray-900">245ms</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Active Sessions</span>
                      <span className="text-gray-900">23</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-start">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
                  <div>
                    <h4 className="text-sm font-medium text-yellow-800">Action Required</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      {stats.pendingApprovals} participants are waiting for approval. Review and approve eligible participants to maintain trial progress.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'approvals' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Pending Participant Approvals
                </h3>
                <div className="flex items-center space-x-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      placeholder="Search participants..."
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              {filteredParticipants.filter(p => p.approval_status === 'pending').length > 0 ? (
                <div className="space-y-4">
                  {filteredParticipants
                    .filter(p => p.approval_status === 'pending')
                    .map((participant) => (
                      <div
                        key={participant.id}
                        className="bg-white border border-gray-200 rounded-lg p-6"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h4 className="text-lg font-medium text-gray-900">
                                Participant ID: {participant.user_id.slice(-8)}
                              </h4>
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(participant.approval_status)}`}>
                                {participant.approval_status.toUpperCase()}
                              </span>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm text-gray-600">
                              <div>
                                <span className="font-medium">Age:</span> {participant.age}
                              </div>
                              <div>
                                <span className="font-medium">Gender:</span> {participant.gender}
                              </div>
                              <div>
                                <span className="font-medium">Institution:</span> {participant.institution}
                              </div>
                              <div>
                                <span className="font-medium">Language:</span> {participant.preferred_language}
                              </div>
                              <div>
                                <span className="font-medium">Enrolled:</span> {new Date(participant.enrollment_date).toLocaleDateString()}
                              </div>
                              <div>
                                <span className="font-medium">Consent:</span> 
                                <span className={participant.consent_given ? 'text-green-600' : 'text-red-600'}>
                                  {participant.consent_given ? ' Given' : ' Not Given'}
                                </span>
                              </div>
                            </div>

                            {participant.medical_history && (
                              <div className="mt-3">
                                <span className="text-sm font-medium text-gray-700">Medical History:</span>
                                <p className="text-sm text-gray-600 mt-1">{participant.medical_history}</p>
                              </div>
                            )}
                          </div>

                          <div className="ml-6 flex flex-col space-y-2">
                            <button
                              onClick={() => {
                                setSelectedParticipant(participant)
                                setShowModal(true)
                              }}
                              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 border border-blue-300 rounded hover:bg-blue-50"
                            >
                              <Eye className="w-4 h-4 inline mr-1" />
                              View Details
                            </button>
                            
                            <button
                              onClick={() => approveParticipant(participant.id)}
                              disabled={actionLoading === participant.id}
                              className="px-3 py-1 text-sm text-white bg-green-600 hover:bg-green-700 rounded disabled:opacity-50"
                            >
                              {actionLoading === participant.id ? (
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                              ) : (
                                <>
                                  <CheckCircle className="w-4 h-4 inline mr-1" />
                                  Approve
                                </>
                              )}
                            </button>
                            
                            <button
                              onClick={() => rejectParticipant(participant.id, 'Does not meet criteria')}
                              disabled={actionLoading === participant.id}
                              className="px-3 py-1 text-sm text-white bg-red-600 hover:bg-red-700 rounded disabled:opacity-50"
                            >
                              <XCircle className="w-4 h-4 inline mr-1" />
                              Reject
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <UserCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No pending approvals
                  </h3>
                  <p className="text-gray-500">
                    All participant registrations have been reviewed
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'participants' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  All Participants
                </h3>
                <button className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </button>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Participant
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Institution
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Samples
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Enrolled
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredParticipants.map((participant) => (
                        <tr key={participant.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                ID: {participant.user_id.slice(-8)}
                              </div>
                              <div className="text-sm text-gray-500">
                                {participant.age}y, {participant.gender}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(participant.approval_status)}`}>
                              {participant.approval_status.toUpperCase()}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {participant.institution}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {participant.voice_samples_collected}/{participant.target_samples}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(participant.enrollment_date).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button
                              onClick={() => {
                                setSelectedParticipant(participant)
                                setShowModal(true)
                              }}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">
                System Analytics
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h4 className="text-md font-medium text-gray-900 mb-4">Enrollment Trends</h4>
                  <div className="h-64 flex items-center justify-center text-gray-500">
                    <div className="text-center">
                      <BarChart3 className="w-12 h-12 mx-auto mb-2" />
                      <p>Chart visualization would go here</p>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h4 className="text-md font-medium text-gray-900 mb-4">Approval Status Distribution</h4>
                  <div className="h-64 flex items-center justify-center text-gray-500">
                    <div className="text-center">
                      <PieChart className="w-12 h-12 mx-auto mb-2" />
                      <p>Pie chart visualization would go here</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal for participant details */}
      {showModal && selectedParticipant && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Participant Details
                </h3>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">User ID</label>
                    <p className="text-sm text-gray-900">{selectedParticipant.user_id}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Age</label>
                    <p className="text-sm text-gray-900">{selectedParticipant.age}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Gender</label>
                    <p className="text-sm text-gray-900">{selectedParticipant.gender}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Phone</label>
                    <p className="text-sm text-gray-900">{selectedParticipant.phone}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Institution</label>
                    <p className="text-sm text-gray-900">{selectedParticipant.institution}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Language</label>
                    <p className="text-sm text-gray-900">{selectedParticipant.preferred_language}</p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Emergency Contact</label>
                  <p className="text-sm text-gray-900">
                    {selectedParticipant.emergency_contact_name} - {selectedParticipant.emergency_contact_phone}
                  </p>
                </div>

                {selectedParticipant.medical_history && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Medical History</label>
                    <p className="text-sm text-gray-900">{selectedParticipant.medical_history}</p>
                  </div>
                )}

                {selectedParticipant.current_medications && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Current Medications</label>
                    <p className="text-sm text-gray-900">{selectedParticipant.current_medications}</p>
                  </div>
                )}

                <div className="flex items-center space-x-4 pt-4">
                  <button
                    onClick={() => approveParticipant(selectedParticipant.id)}
                    disabled={actionLoading === selectedParticipant.id}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                  >
                    {actionLoading === selectedParticipant.id ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    ) : (
                      'Approve Participant'
                    )}
                  </button>
                  <button
                    onClick={() => rejectParticipant(selectedParticipant.id, 'Does not meet criteria')}
                    disabled={actionLoading === selectedParticipant.id}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                  >
                    Reject Participant
                  </button>
                  <button
                    onClick={() => setShowModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
