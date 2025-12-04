import { useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { Dashboard } from './pages/Dashboard'
import { PatientApproval } from './pages/PatientApproval'
import { PsychologistMapping } from './pages/PsychologistMapping'
import { CouponManagement } from './pages/CouponManagement'
import { UserManagement } from './pages/UserManagement'
import { Analytics } from './pages/Analytics'
import { Settings } from './pages/Settings'
import { LoginPage } from './pages/LoginPage'
import PatientPortal from './pages/PatientPortal'
import './App.css'

export type Page = 'dashboard' | 'patients' | 'psychologists' | 'coupons' | 'users' | 'analytics' | 'settings' | 'my-dashboard'
export type UserRole = 'admin' | 'psychologist' | 'patient' | 'researcher'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [userRole, setUserRole] = useState<UserRole>('admin')

  const handleLogin = (role: UserRole = 'admin') => {
    setIsAuthenticated(true)
    setUserRole(role)
    // Set default page based on role
    if (role === 'patient') {
      setCurrentPage('my-dashboard')
    } else {
      setCurrentPage('dashboard')
    }
  }

  if (!isAuthenticated) {
    return <LoginPage onLogin={handleLogin} />
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />
      case 'patients':
        return <PatientApproval />
      case 'psychologists':
        return <PsychologistMapping />
      case 'coupons':
        return <CouponManagement />
      case 'users':
        return <UserManagement />
      case 'analytics':
        return <Analytics />
      case 'settings':
        return <Settings />
      case 'my-dashboard':
        return <PatientPortal />
      default:
        // Default based on role
        return userRole === 'patient' ? <PatientPortal /> : <Dashboard />
    }
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar 
        currentPage={currentPage} 
        onPageChange={setCurrentPage}
        onLogout={() => setIsAuthenticated(false)}
      />
      <main className="flex-1 overflow-auto">
        {renderPage()}
      </main>
    </div>
  )
}

export default App
