import { useState } from 'react'
import { 
  Search, 
  Plus, 
  UserPlus,
  Users,
  Mail,
  Award,
  X
} from 'lucide-react'

interface Psychologist {
  id: string
  name: string
  email: string
  phone: string
  specialization: string
  rciNumber: string
  assignedPatients: number
  maxPatients: number
  status: 'active' | 'inactive'
}

interface Patient {
  id: string
  name: string
  email: string
  assignedTo: string | null
}

const mockPsychologists: Psychologist[] = [
  { id: 'PSY001', name: 'Dr. Meera Krishnan', email: 'meera.k@cittaa.in', phone: '+91 98765 43210', specialization: 'Clinical Psychology', rciNumber: 'RCI/2020/1234', assignedPatients: 12, maxPatients: 20, status: 'active' },
  { id: 'PSY002', name: 'Dr. Rajesh Iyer', email: 'rajesh.i@cittaa.in', phone: '+91 87654 32109', specialization: 'Counseling Psychology', rciNumber: 'RCI/2019/5678', assignedPatients: 8, maxPatients: 15, status: 'active' },
  { id: 'PSY003', name: 'Dr. Priya Menon', email: 'priya.m@cittaa.in', phone: '+91 76543 21098', specialization: 'Health Psychology', rciNumber: 'RCI/2021/9012', assignedPatients: 15, maxPatients: 15, status: 'active' },
  { id: 'PSY004', name: 'Dr. Arun Nair', email: 'arun.n@cittaa.in', phone: '+91 65432 10987', specialization: 'Clinical Psychology', rciNumber: 'RCI/2018/3456', assignedPatients: 0, maxPatients: 20, status: 'inactive' },
]

const mockPatients: Patient[] = [
  { id: 'P001', name: 'Rahul Sharma', email: 'rahul.s@email.com', assignedTo: 'PSY001' },
  { id: 'P002', name: 'Priya Patel', email: 'priya.p@email.com', assignedTo: null },
  { id: 'P003', name: 'Amit Kumar', email: 'amit.k@email.com', assignedTo: 'PSY002' },
  { id: 'P004', name: 'Sneha Reddy', email: 'sneha.r@email.com', assignedTo: null },
  { id: 'P005', name: 'Vikram Singh', email: 'vikram.s@email.com', assignedTo: 'PSY001' },
]

export function PsychologistMapping() {
  const [psychologists] = useState(mockPsychologists)
  const [patients, setPatients] = useState(mockPatients)
  const [searchQuery, setSearchQuery] = useState('')
  const [showAssignModal, setShowAssignModal] = useState(false)
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)

  const unassignedPatients = patients.filter(p => !p.assignedTo)

  const handleAssign = (patientId: string, psychologistId: string) => {
    setPatients(patients.map(p => 
      p.id === patientId ? { ...p, assignedTo: psychologistId } : p
    ))
    setShowAssignModal(false)
    setSelectedPatient(null)
  }

  const handleUnassign = (patientId: string) => {
    setPatients(patients.map(p => 
      p.id === patientId ? { ...p, assignedTo: null } : p
    ))
  }

  const getPsychologistName = (id: string | null) => {
    if (!id) return 'Unassigned'
    const psy = psychologists.find(p => p.id === id)
    return psy?.name || 'Unknown'
  }

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Psychologist-Patient Mapping</h1>
          <p className="text-gray-600 mt-1">Manage patient assignments to psychologists</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-orange-50 px-4 py-2 rounded-lg">
            <Users className="w-5 h-5 text-orange-600" />
            <span className="text-orange-700 font-medium">{unassignedPatients.length} unassigned</span>
          </div>
          <button className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
            <Plus className="w-4 h-4" />
            Add Psychologist
          </button>
        </div>
      </div>

      {/* Psychologists Grid */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Psychologists</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {psychologists.map((psy) => (
            <div key={psy.id} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 card-hover">
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-700 font-semibold text-lg">{psy.name.charAt(0)}</span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  psy.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                }`}>
                  {psy.status}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900">{psy.name}</h3>
              <p className="text-sm text-gray-500 mb-3">{psy.specialization}</p>
              
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-gray-600">
                  <Mail className="w-4 h-4" />
                  <span className="truncate">{psy.email}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Award className="w-4 h-4" />
                  <span>{psy.rciNumber}</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Patients</span>
                  <span className="text-sm font-medium">{psy.assignedPatients}/{psy.maxPatients}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      psy.assignedPatients >= psy.maxPatients ? 'bg-red-500' :
                      psy.assignedPatients >= psy.maxPatients * 0.8 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${(psy.assignedPatients / psy.maxPatients) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Patient Assignments */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Patient Assignments</h2>
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search patients..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          </div>
        </div>

        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-600">Patient</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-600">Email</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-600">Assigned To</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {patients
              .filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
              .map((patient) => (
              <tr key={patient.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-700 text-sm font-medium">{patient.name.charAt(0)}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{patient.name}</p>
                      <p className="text-xs text-gray-500">{patient.id}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">{patient.email}</td>
                <td className="px-6 py-4">
                  <span className={`text-sm ${patient.assignedTo ? 'text-gray-900' : 'text-orange-600'}`}>
                    {getPsychologistName(patient.assignedTo)}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        setSelectedPatient(patient)
                        setShowAssignModal(true)
                      }}
                      className="flex items-center gap-1 px-3 py-1.5 text-sm text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    >
                      <UserPlus className="w-4 h-4" />
                      {patient.assignedTo ? 'Reassign' : 'Assign'}
                    </button>
                    {patient.assignedTo && (
                      <button
                        onClick={() => handleUnassign(patient.id)}
                        className="flex items-center gap-1 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <X className="w-4 h-4" />
                        Remove
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Assign Modal */}
      {showAssignModal && selectedPatient && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl w-full max-w-md mx-4 animate-slide-in">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Assign Psychologist</h2>
              <p className="text-gray-500 mt-1">Select a psychologist for {selectedPatient.name}</p>
            </div>
            <div className="p-6 space-y-3 max-h-80 overflow-y-auto">
              {psychologists
                .filter(p => p.status === 'active' && p.assignedPatients < p.maxPatients)
                .map((psy) => (
                <button
                  key={psy.id}
                  onClick={() => handleAssign(selectedPatient.id, psy.id)}
                  className="w-full flex items-center gap-4 p-4 border border-gray-200 rounded-xl hover:border-green-500 hover:bg-green-50 transition-colors text-left"
                >
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-700 font-semibold">{psy.name.charAt(0)}</span>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{psy.name}</p>
                    <p className="text-sm text-gray-500">{psy.specialization}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{psy.assignedPatients}/{psy.maxPatients}</p>
                    <p className="text-xs text-gray-500">patients</p>
                  </div>
                </button>
              ))}
            </div>
            <div className="p-6 border-t border-gray-200">
              <button
                onClick={() => {
                  setShowAssignModal(false)
                  setSelectedPatient(null)
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
