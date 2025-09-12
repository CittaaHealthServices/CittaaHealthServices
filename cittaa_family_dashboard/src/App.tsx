import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { AuthProvider } from '@/contexts/AuthContext'
import { FamilyProvider } from '@/contexts/FamilyContext'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import DashboardPage from '@/pages/DashboardPage'
import ChildProfilePage from '@/pages/ChildProfilePage'
import ConsentManagementPage from '@/pages/ConsentManagementPage'
import ActivityMonitoringPage from '@/pages/ActivityMonitoringPage'
import EducationalProgressPage from '@/pages/EducationalProgressPage'
import MobileProfilePage from '@/pages/MobileProfilePage'
import CompliancePage from '@/pages/CompliancePage'
import AddChildPage from '@/pages/AddChildPage'
import ProtectedRoute from '@/components/ProtectedRoute'

function App() {
  return (
    <AuthProvider>
      <FamilyProvider>
        <Router>
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/child/:childId"
                element={
                  <ProtectedRoute>
                    <ChildProfilePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/consent"
                element={
                  <ProtectedRoute>
                    <ConsentManagementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/activity"
                element={
                  <ProtectedRoute>
                    <ActivityMonitoringPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/education"
                element={
                  <ProtectedRoute>
                    <EducationalProgressPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/mobile-profiles"
                element={
                  <ProtectedRoute>
                    <MobileProfilePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/compliance"
                element={
                  <ProtectedRoute>
                    <CompliancePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/child/new"
                element={
                  <ProtectedRoute>
                    <AddChildPage />
                  </ProtectedRoute>
                }
              />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </FamilyProvider>
    </AuthProvider>
  )
}

export default App
