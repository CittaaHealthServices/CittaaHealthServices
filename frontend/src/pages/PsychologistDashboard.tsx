import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { psychologistService } from '../services/api'
import { 
  Users, AlertTriangle, Calendar, Activity,
  ChevronRight, Clock, Heart
} from 'lucide-react'

interface Patient {
  id: string
  email: string
  full_name: string
  phone: string
  age_range: string
  gender: string
  assignment_date: string
  latest_risk_level: string
  latest_mental_health_score: number | null
  total_sessions: number
}

interface DashboardData {
  total_patients: number
  risk_distribution: {
    low: number
    moderate: number
    high: number
    unknown: number
  }
  total_sessions: number
  upcoming_followups: Array<{
    assessment_id: string
    patient_id: string
    follow_up_date: string
  }>
}

export default function PsychologistDashboard() {
  const { user } = useAuth()
  const [patients, setPatients] = useState<Patient[]>([])
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [highRiskPatients, setHighRiskPatients] = useState<Patient[]>([])
  const [loading, setLoading] = useState(true)
  const [, setError] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [patientsRes, dashboardRes, highRiskRes] = await Promise.all([
        psychologistService.getAssignedPatients(),
        psychologistService.getDashboard(),
        psychologistService.getHighRiskPatients()
      ])
      setPatients(patientsRes.patients || [])
      setDashboardData(dashboardRes)
      setHighRiskPatients(highRiskRes.high_risk_patients || [])
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-success/10 text-success border-success/20'
      case 'moderate': return 'bg-warning/10 text-warning border-warning/20'
      case 'high': return 'bg-error/10 text-error border-error/20'
      default: return 'bg-gray-100 text-gray-500 border-gray-200'
    }
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

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-6 text-white">
        <div className="flex items-center space-x-2 mb-1">
          <span className="text-xl font-display italic text-white/90">Cittaa</span>
          <span className="text-white/60">|</span>
          <span className="text-white/80">Vocalysis</span>
        </div>
        <h1 className="text-2xl font-bold">
          Welcome, Dr. {user?.full_name?.split(' ')[0] || 'Psychologist'}
        </h1>
        <p className="mt-1 text-white/80">
          Manage your patients and clinical assessments
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Total Patients</span>
            <Users className="w-5 h-5 text-primary-400" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-800">
            {dashboardData?.total_patients || 0}
          </p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">High Risk</span>
            <AlertTriangle className="w-5 h-5 text-error" />
          </div>
          <p className="mt-3 text-2xl font-bold text-error">
            {dashboardData?.risk_distribution?.high || 0}
          </p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Total Sessions</span>
            <Calendar className="w-5 h-5 text-secondary-400" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-800">
            {dashboardData?.total_sessions || 0}
          </p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Upcoming Follow-ups</span>
            <Clock className="w-5 h-5 text-accent-400" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-800">
            {dashboardData?.upcoming_followups?.length || 0}
          </p>
        </div>
      </div>

      {/* High Risk Patients Alert */}
      {highRiskPatients.length > 0 && (
        <div className="bg-error/5 border border-error/20 rounded-xl p-5">
          <div className="flex items-center space-x-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-error" />
            <h3 className="font-semibold text-error">High Risk Patients Requiring Attention</h3>
          </div>
          <div className="space-y-3">
            {highRiskPatients.slice(0, 3).map((patient) => (
              <Link
                key={patient.id}
                to={`/psychologist/patient/${patient.id}`}
                className="flex items-center justify-between p-3 bg-white rounded-lg hover:shadow-md transition-shadow"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-error/10 rounded-full flex items-center justify-center">
                    <Heart className="w-5 h-5 text-error" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{patient.full_name || patient.email}</p>
                    <p className="text-xs text-gray-500">
                      Score: {patient.latest_mental_health_score?.toFixed(0) || 'N/A'}
                    </p>
                  </div>
                </div>
                <ChevronRight className="w-5 h-5 text-gray-400" />
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Patient List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-5 border-b border-gray-100">
          <h3 className="font-semibold text-gray-800">My Patients</h3>
        </div>
        {patients.length === 0 ? (
          <div className="p-12 text-center">
            <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No patients assigned yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {patients.map((patient) => (
              <Link
                key={patient.id}
                to={`/psychologist/patient/${patient.id}`}
                className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                    <span className="text-white font-medium">
                      {patient.full_name?.charAt(0) || patient.email?.charAt(0) || 'P'}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{patient.full_name || 'Unknown'}</p>
                    <p className="text-sm text-gray-500">{patient.email}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="text-xs text-gray-400">{patient.age_range || 'N/A'}</span>
                      <span className="text-xs text-gray-300">|</span>
                      <span className="text-xs text-gray-400 capitalize">{patient.gender || 'N/A'}</span>
                      <span className="text-xs text-gray-300">|</span>
                      <span className="text-xs text-gray-400">{patient.total_sessions} sessions</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-800">
                      Score: {patient.latest_mental_health_score?.toFixed(0) || 'N/A'}
                    </p>
                    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-medium capitalize ${getRiskColor(patient.latest_risk_level)}`}>
                      {patient.latest_risk_level || 'Unknown'}
                    </span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
