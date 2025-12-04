import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { adminService } from '../services/api'
import { 
  ArrowLeft, UserCog, Search, Activity, AlertTriangle,
  RefreshCw, User, UserCheck, X, Check
} from 'lucide-react'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  assigned_psychologist_id?: string
}

interface Psychologist {
  id: string
  email: string
  full_name: string
  phone?: string
}

export default function PsychologistAssignments() {
  const [patients, setPatients] = useState<User[]>([])
  const [psychologists, setPsychologists] = useState<Psychologist[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null)
  const [assigning, setAssigning] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [usersData, psychData] = await Promise.all([
        adminService.getAllUsers('patient', 100, 0),
        adminService.getAllPsychologists()
      ])
      setPatients(usersData.users || [])
      setPsychologists(psychData.psychologists || [])
    } catch (err) {
      setError('Failed to load data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleAssign = async (patientId: string, psychologistId: string) => {
    try {
      setAssigning(true)
      await adminService.assignPsychologist(patientId, psychologistId)
      setSuccess('Psychologist assigned successfully')
      setSelectedPatient(null)
      loadData()
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError('Failed to assign psychologist')
      console.error(err)
    } finally {
      setAssigning(false)
    }
  }

  const getPsychologistName = (psychId: string | undefined) => {
    if (!psychId) return null
    const psych = psychologists.find(p => p.id === psychId)
    return psych ? psych.full_name || psych.email : 'Unknown'
  }

  const filteredPatients = patients.filter(patient => {
    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      return (
        patient.email?.toLowerCase().includes(search) ||
        patient.full_name?.toLowerCase().includes(search)
      )
    }
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading assignments...</p>
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
            <h1 className="text-2xl font-bold text-gray-800">Psychologist Assignments</h1>
            <p className="text-sm text-gray-500">Assign psychologists to patients</p>
          </div>
        </div>
        <button
          onClick={loadData}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <User className="w-5 h-5 text-primary-500" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">{patients.length}</p>
              <p className="text-sm text-gray-500">Total Patients</p>
            </div>
          </div>
        </div>
        <div className="bg-green-50 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <UserCheck className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">
                {patients.filter(p => p.assigned_psychologist_id).length}
              </p>
              <p className="text-sm text-gray-500">Assigned</p>
            </div>
          </div>
        </div>
        <div className="bg-blue-50 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <UserCog className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">{psychologists.length}</p>
              <p className="text-sm text-gray-500">Psychologists</p>
            </div>
          </div>
        </div>
      </div>

      {/* Success */}
      {success && (
        <div className="bg-green-50 rounded-xl p-4 border border-green-200 flex items-center space-x-2 text-green-600 animate-fadeIn">
          <Check className="w-5 h-5" />
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

      {/* Search */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search patients by name or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Patients Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Patient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assigned Psychologist
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredPatients.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                    <UserCog className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>No patients found</p>
                  </td>
                </tr>
              ) : (
                filteredPatients.map((patient) => (
                  <tr key={patient.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-white font-medium">
                            {patient.full_name?.charAt(0) || patient.email?.charAt(0) || 'P'}
                          </span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {patient.full_name || 'Unknown'}
                          </div>
                          <div className="text-sm text-gray-500">{patient.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {patient.is_active ? (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-green-100 text-green-700">
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-500">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {patient.assigned_psychologist_id ? (
                        <div className="flex items-center space-x-2">
                          <UserCheck className="w-4 h-4 text-green-500" />
                          <span className="text-sm text-gray-900">
                            {getPsychologistName(patient.assigned_psychologist_id)}
                          </span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">Not assigned</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="relative">
                        <button
                          onClick={() => setSelectedPatient(selectedPatient === patient.id ? null : patient.id)}
                          className="px-3 py-1 text-sm bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 transition-colors"
                        >
                          {patient.assigned_psychologist_id ? 'Reassign' : 'Assign'}
                        </button>
                        
                        {selectedPatient === patient.id && (
                          <>
                            <div 
                              className="fixed inset-0 z-10"
                              onClick={() => setSelectedPatient(null)}
                            />
                            <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-20 animate-fadeIn">
                              <div className="px-3 py-2 border-b border-gray-100">
                                <p className="text-xs text-gray-500">Select Psychologist</p>
                              </div>
                              {psychologists.length === 0 ? (
                                <div className="px-3 py-4 text-sm text-gray-500 text-center">
                                  No psychologists available
                                </div>
                              ) : (
                                psychologists.map((psych) => (
                                  <button
                                    key={psych.id}
                                    onClick={() => handleAssign(patient.id, psych.id)}
                                    disabled={assigning}
                                    className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center space-x-2 ${
                                      patient.assigned_psychologist_id === psych.id ? 'bg-primary-50 text-primary-600' : 'text-gray-700'
                                    }`}
                                  >
                                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                      <span className="text-blue-600 text-xs font-medium">
                                        {psych.full_name?.charAt(0) || psych.email?.charAt(0) || 'P'}
                                      </span>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                      <p className="font-medium truncate">{psych.full_name || 'Unknown'}</p>
                                      <p className="text-xs text-gray-500 truncate">{psych.email}</p>
                                    </div>
                                    {patient.assigned_psychologist_id === psych.id && (
                                      <Check className="w-4 h-4 text-primary-500" />
                                    )}
                                  </button>
                                ))
                              )}
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
    </div>
  )
}
