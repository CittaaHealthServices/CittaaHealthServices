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
import './App.css'

export type Page = 'dashboard' | 'patients' | 'psychologists' | 'coupons' | 'users' | 'analytics' | 'settings'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />
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
      default:
        return <Dashboard />
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
