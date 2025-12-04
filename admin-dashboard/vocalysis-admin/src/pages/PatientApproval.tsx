import { useState } from 'react'
import { 
  Search, 
  Filter, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Eye,
  ChevronLeft,
  ChevronRight,
  User,
  Mail,
  Phone,
  Calendar
} from 'lucide-react'

interface Patient {
  id: string
  name: string
  email: string
  phone: string
  registrationDate: string
  trialType: string
  status: 'pending' | 'approved' | 'rejected'
  ageRange: string
  gender: string
}

const mockPatients: Patient[] = [
  { id: 'P001', name: 'Rahul Sharma', email: 'rahul.s@email.com', phone: '+91 98765 43210', registrationDate: '2024-01-15', trialType: 'Clinical Trial A', status: 'pending', ageRange: '25-34', gender: 'Male' },
  { id: 'P002', name: 'Priya Patel', email: 'priya.p@email.com', phone: '+91 87654 32109', registrationDate: '2024-01-14', trialType: 'Clinical Trial B', status: 'pending', ageRange: '18-24', gender: 'Female' },
  { id: 'P003', name: 'Amit Kumar', email: 'amit.k@email.com', phone: '+91 76543 21098', registrationDate: '2024-01-13', trialType: 'Clinical Trial A', status: 'approved', ageRange: '35-44', gender: 'Male' },
  { id: 'P004', name: 'Sneha Reddy', email: 'sneha.r@email.com', phone: '+91 65432 10987', registrationDate: '2024-01-12', trialType: 'Clinical Trial C', status: 'rejected', ageRange: '25-34', gender: 'Female' },
  { id: 'P005', name: 'Vikram Singh', email: 'vikram.s@email.com', phone: '+91 54321 09876', registrationDate: '2024-01-11', trialType: 'Clinical Trial B', status: 'pending', ageRange: '45-54', gender: 'Male' },
  { id: 'P006', name: 'Ananya Gupta', email: 'ananya.g@email.com', phone: '+91 43210 98765', registrationDate: '2024-01-10', trialType: 'Clinical Trial A', status: 'approved', ageRange: '18-24', gender: 'Female' },
]

export function PatientApproval() {
  const [patients, setPatients] = useState(mockPatients)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)

  const filteredPatients = patients.filter(patient => {
    const matchesSearch = patient.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         patient.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         patient.id.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || patient.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleApprove = (patientId: string) => {
    setPatients(patients.map(p => 
      p.id === patientId ? { ...p, status: 'approved' as const } : p
    ))
    setSelectedPatient(null)
  }

  const handleReject = (patientId: string) => {
    setPatients(patients.map(p => 
      p.id === patientId ? { ...p, status: 'rejected' as const } : p
    ))
    setSelectedPatient(null)
  }

  const pendingCount = patients.filter(p => p.status === 'pending').length

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Patient Approval</h1>
          <p className="text-gray-600 mt-1">Manage clinical trial patient registrations</p>
        </div>
        <div className="flex items-center gap-2 bg-yellow-50 px-4 py-2 rounded-lg">
          <Clock className="w-5 h-5 text-yellow-600" />
          <span className="text-yellow-700 font-medium">{pendingCount} pending approvals</span>
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
                placeholder="Search by name, email, or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500"
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>

      {/* Patient Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Patient</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Contact</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Trial Type</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Registration</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Status</th>
              <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredPatients.map((patient) => (
              <tr key={patient.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <span className="text-green-700 font-medium">{patient.name.charAt(0)}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{patient.name}</p>
                      <p className="text-sm text-gray-500">{patient.id}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <p className="text-sm text-gray-900">{patient.email}</p>
                  <p className="text-sm text-gray-500">{patient.phone}</p>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-900">{patient.trialType}</span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-900">{patient.registrationDate}</span>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${
                    patient.status === 'approved' ? 'bg-green-100 text-green-700' :
                    patient.status === 'rejected' ? 'bg-red-100 text-red-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {patient.status === 'approved' && <CheckCircle className="w-3 h-3" />}
                    {patient.status === 'rejected' && <XCircle className="w-3 h-3" />}
                    {patient.status === 'pending' && <Clock className="w-3 h-3" />}
                    {patient.status.charAt(0).toUpperCase() + patient.status.slice(1)}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setSelectedPatient(patient)}
                      className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    {patient.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleApprove(patient.id)}
                          className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                          title="Approve"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleReject(patient.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Reject"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            Showing {filteredPatients.length} of {patients.length} patients
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

      {/* Patient Detail Modal */}
      {selectedPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-full max-w-lg mx-4 animate-slide-in">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Patient Details</h2>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <User className="w-8 h-8 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{selectedPatient.name}</h3>
                  <p className="text-gray-500">{selectedPatient.id}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">Email</p>
                    <p className="text-sm text-gray-900">{selectedPatient.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">Phone</p>
                    <p className="text-sm text-gray-900">{selectedPatient.phone}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Calendar className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">Registration Date</p>
                    <p className="text-sm text-gray-900">{selectedPatient.registrationDate}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <User className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">Demographics</p>
                    <p className="text-sm text-gray-900">{selectedPatient.gender}, {selectedPatient.ageRange}</p>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-blue-600 font-medium">Trial Type</p>
                <p className="text-sm text-blue-900">{selectedPatient.trialType}</p>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex gap-3">
              <button
                onClick={() => setSelectedPatient(null)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
              {selectedPatient.status === 'pending' && (
                <>
                  <button
                    onClick={() => handleReject(selectedPatient.id)}
                    className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleApprove(selectedPatient.id)}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Approve
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
