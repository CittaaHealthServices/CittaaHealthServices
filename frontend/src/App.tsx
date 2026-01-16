import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import PatientDashboard from './pages/PatientDashboard'
import VoiceRecording from './pages/VoiceRecording'
import AnalysisResults from './pages/AnalysisResults'
import ClinicalReports from './pages/ClinicalReports'
import PsychologistDashboard from './pages/PsychologistDashboard'
import PatientDetails from './pages/PatientDetails'
import AdminDashboard from './pages/AdminDashboard'
import PendingApprovals from './pages/PendingApprovals'
import UserManagement from './pages/UserManagement'

// Component that renders the appropriate dashboard based on user role
function RoleDashboard() {
  const { user, loading } = useAuth()
  
  // Show loading state while auth is being checked
  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse text-primary-500">Loading dashboard...</div>
      </div>
    )
  }
  
  switch (user.role) {
    case 'psychologist':
      return <PsychologistDashboard />
    case 'admin':
    case 'super_admin':
    case 'hr_admin':
      return <AdminDashboard />
    default:
      return <PatientDashboard />
  }
}

function ProtectedRoute({ children, allowedRoles }: { children: React.ReactNode, allowedRoles?: string[] }) {
  const { user, isAuthenticated, loading } = useAuth()
  
  const getCorrectDashboard = () => {
    if (!user) return '/login'
    // All users go to /dashboard - RoleDashboard component renders the correct dashboard
    return '/dashboard'
  }
  
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
  
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to={getCorrectDashboard()} replace />
  }
  
  return <>{children}</>
}

function AppRoutes() {
  const { user, isAuthenticated } = useAuth()
  
  const getDashboardRoute = () => {
    if (!user) return '/login'
    // All users go to /dashboard - RoleDashboard component renders the correct dashboard
    return '/dashboard'
  }
  
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={isAuthenticated ? <Navigate to={getDashboardRoute()} replace /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to={getDashboardRoute()} replace /> : <Register />} />
      <Route path="/forgot-password" element={isAuthenticated ? <Navigate to={getDashboardRoute()} replace /> : <ForgotPassword />} />
      
      {/* Universal dashboard route - renders appropriate dashboard based on role */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Layout><RoleDashboard /></Layout>
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
        <ProtectedRoute allowedRoles={['admin', 'super_admin', 'hr_admin']}>
          <Layout><AdminDashboard /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/admin/approvals" element={
        <ProtectedRoute allowedRoles={['admin', 'super_admin']}>
          <Layout><PendingApprovals /></Layout>
        </ProtectedRoute>
      } />
      <Route path="/admin/users" element={
        <ProtectedRoute allowedRoles={['admin', 'super_admin', 'hr_admin']}>
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
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  )
}

export default App
