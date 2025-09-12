import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})

export const childLogin = (payload: { password: string; biometric_data?: string | null }) =>
  api.post('/api/auth/child-login', payload)

export const getFamilyOverview = () => api.get('/api/analytics/family-overview')
export const getChildActivities = (childId: string) => api.get(`/api/analytics/children/${childId}/activities`)

export const getCulturalContent = (region: string) =>
  api.get(`/api/content/cultural`, { params: { region } })
export const getBlockedSuggestions = () => api.get('/api/content/suggestions')

export const getDevices = () => api.get('/api/devices')
export const syncDevice = (deviceId: string) => api.post(`/api/devices/${deviceId}/sync`, {})

export const getSchoolReport = () => api.get('/api/institutions/school/report')
export const getHospitalSessions = () => api.get('/api/institutions/hospital/sessions')

export const getVpnStatus = () => api.get('/api/security/vpn-status')

export const getComplianceStatus = () => api.get('/api/analytics/compliance-status')

export const startPasswordRecovery = (email: string) => api.post('/api/auth/forgot-password', { email })
export const verifySecurityQuestion = (answer: string) =>
  api.post('/api/auth/verify-security-question', { answer })
export const verifyEmergencyOtp = (phone: string, otp: string) =>
  api.post('/api/auth/verify-otp', { phone, otp })
export const resetChildPassword = (newPassword: string, biometricsApproved: boolean) =>
  api.post('/api/auth/reset-child-password', { newPassword, biometricsApproved })

export const downloadMobileProfile = (platform: 'ios' | 'android') =>
  api.get(`/api/devices/mobile-profile`, { params: { platform }, responseType: 'blob' })

export const generateMobileProfile = (childId: string, platform: 'ios' | 'android', familySettings: Record<string, unknown> = {}, childData: Record<string, unknown> = {}) =>
  api.post(`/api/mobile/generate-profile/${childId}`, { platform, family_settings: familySettings, child_data: childData })

export const downloadProfileByToken = (profileToken: string) =>
  api.get(`/api/mobile/download-profile/${encodeURIComponent(profileToken)}`, { responseType: 'blob' })

export const activateMobileProfile = (payload: { child_id: string; platform: 'ios' | 'android'; device_fingerprint: string; biometric_setup?: boolean }) =>
  api.post('/api/mobile/activate-profile', payload)

export default api
