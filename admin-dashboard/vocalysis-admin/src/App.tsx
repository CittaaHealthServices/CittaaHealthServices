import { useState, useEffect } from 'react'
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

interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const [userRole, setUserRole] = useState<UserRole>('admin')
  const [_token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)

  // Check for existing session on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser)
        setToken(storedToken)
        setUser(parsedUser)
        setUserRole(parsedUser.role as UserRole)
        setIsAuthenticated(true)
        if (parsedUser.role === 'patient') {
          setCurrentPage('my-dashboard')
        }
      } catch (e) {
        // Invalid stored data, clear it
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
  }, [])

  const handleLogin = (role: UserRole, authToken: string, userData: User) => {
    setIsAuthenticated(true)
    setUserRole(role)
    setToken(authToken)
    setUser(userData)
    // Set default page based on role
    if (role === 'patient') {
      setCurrentPage('my-dashboard')
    } else {
      setCurrentPage('dashboard')
    }
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
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
        onLogout={handleLogout}
        userRole={userRole}
        userName={user?.full_name || 'User'}
      />
      <main className="flex-1 overflow-auto">
        {renderPage()}
      </main>
    </div>
  )
}

export default App
