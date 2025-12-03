import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface User {
  id: string
  email: string
  full_name?: string
  phone?: string
  age_range?: string
  gender?: string
  language_preference: string
  role: string
  organization_id?: string
  consent_given: boolean
  is_active: boolean
  is_verified: boolean
  is_clinical_trial_participant: boolean
  trial_status?: string
  assigned_psychologist_id?: string
  created_at: string
  last_login?: string
}

export interface Prediction {
  id: string
  user_id: string
  voice_sample_id?: string
  normal_score?: number
  depression_score?: number
  anxiety_score?: number
  stress_score?: number
  overall_risk_level?: string
  mental_health_score?: number
  confidence?: number
  phq9_score?: number
  phq9_severity?: string
  gad7_score?: number
  gad7_severity?: string
  pss_score?: number
  pss_severity?: string
  wemwbs_score?: number
  wemwbs_severity?: string
  interpretations?: string[]
  recommendations?: string[]
  voice_features?: Record<string, number>
  predicted_at: string
}

export interface DashboardData {
  user_id: string
  current_risk_level: string
  risk_trend: string
  compliance_rate: number
  total_recordings: number
  recent_predictions: Prediction[]
  weekly_trend_data: TrendDataPoint[]
}

export interface TrendDataPoint {
  date: string
  depression: number
  anxiety: number
  stress: number
  mental_health_score: number
  sample_count: number
}

// Auth Service
export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },
  
  register: async (data: {
    email: string
    password: string
    full_name?: string
    phone?: string
    role?: string
    age_range?: string
    gender?: string
    language_preference?: string
    is_clinical_trial_participant?: boolean
  }) => {
    const response = await api.post('/auth/register', data)
    return response.data
  },
  
  getProfile: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
  
  updateProfile: async (data: Partial<User>) => {
    const response = await api.put('/auth/me', data)
    return response.data
  },
  
  updateConsent: async (consent_given: boolean) => {
    const response = await api.post('/auth/consent', { consent_given })
    return response.data
  }
}

// Voice Service
export const voiceService = {
  uploadVoice: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/voice/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
  
  analyzeVoice: async (sampleId: string) => {
    const response = await api.post(`/voice/analyze/${sampleId}`)
    return response.data
  },
  
  demoAnalyze: async (demoType?: string) => {
    const response = await api.post('/voice/demo-analyze', { demo_type: demoType })
    return response.data
  },
  
  getVoiceStatus: async (sampleId: string) => {
    const response = await api.get(`/voice/status/${sampleId}`)
    return response.data
  },
  
  getUserSamples: async (limit = 10) => {
    const response = await api.get(`/voice/samples?limit=${limit}`)
    return response.data
  }
}

// Predictions Service
export const predictionsService = {
  getUserPredictions: async (userId: string, limit = 10) => {
    const response = await api.get(`/predictions/${userId}?limit=${limit}`)
    return response.data
  },
  
  getLatestPrediction: async (userId: string) => {
    const response = await api.get(`/predictions/${userId}/latest`)
    return response.data
  },
  
  getPredictionTrends: async (userId: string, days = 30) => {
    const response = await api.get(`/predictions/${userId}/trends?days=${days}`)
    return response.data
  },
  
  getPredictionDetails: async (predictionId: string) => {
    const response = await api.get(`/predictions/${predictionId}/details`)
    return response.data
  }
}

// Dashboard Service
export const dashboardService = {
  getUserDashboard: async (userId: string): Promise<DashboardData> => {
    const response = await api.get(`/dashboard/${userId}`)
    return response.data
  },
  
  getDashboardSummary: async (userId: string) => {
    const response = await api.get(`/dashboard/${userId}/summary`)
    return response.data
  }
}

// Admin Service
export const adminService = {
  getAllUsers: async (role?: string, limit = 100, offset = 0) => {
    const params = new URLSearchParams()
    if (role) params.append('role', role)
    params.append('limit', limit.toString())
    params.append('offset', offset.toString())
    const response = await api.get(`/admin/users?${params}`)
    return response.data
  },
  
  getPendingApprovals: async () => {
    const response = await api.get('/admin/pending-approvals')
    return response.data
  },
  
  approveParticipant: async (userId: string) => {
    const response = await api.post(`/admin/approve-participant/${userId}`)
    return response.data
  },
  
  rejectParticipant: async (userId: string, reason?: string) => {
    const response = await api.post(`/admin/reject-participant/${userId}`, { reason })
    return response.data
  },
  
  assignPsychologist: async (patientId: string, psychologistId: string) => {
    const response = await api.post('/admin/assign-psychologist', {
      patient_id: patientId,
      psychologist_id: psychologistId
    })
    return response.data
  },
  
  getStatistics: async () => {
    const response = await api.get('/admin/statistics')
    return response.data
  },
  
  getOrganizationMetrics: async (orgId: string) => {
    const response = await api.get(`/admin/organization/${orgId}/metrics`)
    return response.data
  },
  
  updateUserRole: async (userId: string, newRole: string) => {
    const response = await api.put(`/admin/users/${userId}/role?new_role=${newRole}`)
    return response.data
  },
  
  deactivateUser: async (userId: string) => {
    const response = await api.delete(`/admin/users/${userId}`)
    return response.data
  }
}

// Psychologist Service
export const psychologistService = {
  getAssignedPatients: async () => {
    const response = await api.get('/psychologist/patients')
    return response.data
  },
  
  getPatientDetails: async (patientId: string) => {
    const response = await api.get(`/psychologist/patients/${patientId}`)
    return response.data
  },
  
  createAssessment: async (data: {
    patient_id: string
    phq9_score?: number
    gad7_score?: number
    pss_score?: number
    clinician_notes?: string
    diagnosis?: string
    treatment_plan?: string
    ground_truth_label?: string
    follow_up_date?: string
    session_duration_minutes?: number
  }) => {
    const response = await api.post('/psychologist/assessments', data)
    return response.data
  },
  
  getPatientAssessments: async (patientId: string) => {
    const response = await api.get(`/psychologist/assessments/${patientId}`)
    return response.data
  },
  
  getHighRiskPatients: async () => {
    const response = await api.get('/psychologist/high-risk-patients')
    return response.data
  },
  
  getDashboard: async () => {
    const response = await api.get('/psychologist/dashboard')
    return response.data
  }
}

export default api
