import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import PatientDashboard from './pages/PatientDashboard'
import VoiceRecording from './pages/VoiceRecording'
import AnalysisResults from './pages/AnalysisResults'
import ClinicalReports from './pages/ClinicalReports'
import PsychologistDashboard from './pages/PsychologistDashboard'
import PatientDetails from './pages/PatientDetails'
import AdminDashboard from './pages/AdminDashboard'
import PendingApprovals from './pages/PendingApprovals'
import UserManagement from './pages/UserManagement'

// Define admin roles - accept both old 'admin' and new 'super_admin'/'hr_admin' roles
const ADMIN_ROLES = ['super_admin', 'hr_admin', 'admin']

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode, allowedRoles?: string[] }) {
  const { user, isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-pulse text-primary-500">Loading...</div>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  // If user's role is not in allowedRoles, redirect to root (which will route to correct dashboard)
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />
  }
  
  return <>{children}</>
}

function AppRoutes() {
  const { user, isAuthenticated } = useAuth()
  
  const getDashboardRoute = () => {
    if (!user) return '/login'
    if (user.role === 'psychologist') return '/psychologist/dashboard'
    if (ADMIN_ROLES.includes(user.role)) return '/admin/dashboard'
    return '/dashboard'
  }
  
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={isAuthenticated ? <Navigate to={getDashboardRoute()} replace /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to={getDashboardRoute()} replace /> : <Register />} />
      
      {/* Patient routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute allowedRoles={['patient', 'researcher']}>
          <Layout><PatientDashboard /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/record" element={
        <ProtectedRoute allowedRoles={['patient', 'researcher']}>
          <Layout><VoiceRecording /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/results/:predictionId" element={
        <ProtectedRoute>
          <Layout><AnalysisResults /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/reports" element={
        <ProtectedRoute>
          <Layout><ClinicalReports /></Layout>
        </ProtectedRoute>
      } />
      
      {/* Psychologist routes */}
      <Route path="/psychologist/dashboard" element={
        <ProtectedRoute allowedRoles={['psychologist']}>
          <Layout><PsychologistDashboard /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/psychologist/patient/:patientId" element={
        <ProtectedRoute allowedRoles={['psychologist']}>
          <Layout><PatientDetails /></Layout>
        </ProtectedRoute>
      } />
      
      {/* Admin routes */}
      <Route path="/admin/dashboard" element={
        <ProtectedRoute allowedRoles={ADMIN_ROLES}>
          <Layout><AdminDashboard /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/admin/approvals" element={
        <ProtectedRoute allowedRoles={ADMIN_ROLES}>
          <Layout><PendingApprovals /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/admin/users" element={
        <ProtectedRoute allowedRoles={ADMIN_ROLES}>
          <Layout><UserManagement /></Layout>
        </ProtectedRoute>
      } />
      
      {/* Default redirect */}
      <Route path="/" element={<Navigate to={isAuthenticated ? getDashboardRoute() : '/login'} replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  )
}

export default App
