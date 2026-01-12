import { ReactNode, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { 
  Home, Mic, FileText, Users, Settings, LogOut, Menu, X, 
  Activity, UserCheck, ChevronDown
} from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getNavItems = () => {
    const baseItems = [
      { path: '/dashboard', icon: Home, label: 'Dashboard' },
    ]

    if (user?.role === 'patient' || user?.role === 'researcher') {
      return [
        ...baseItems,
        { path: '/record', icon: Mic, label: 'Voice Recording' },
        { path: '/reports', icon: FileText, label: 'Clinical Reports' },
      ]
    }

    if (user?.role === 'psychologist') {
      return [
        { path: '/psychologist/dashboard', icon: Home, label: 'Dashboard' },
        { path: '/psychologist/patients', icon: Users, label: 'My Patients' },
      ]
    }

    if (user?.role === 'super_admin' || user?.role === 'hr_admin') {
      return [
        { path: '/admin/dashboard', icon: Home, label: 'Dashboard' },
        { path: '/admin/users', icon: Users, label: 'User Management' },
        { path: '/admin/approvals', icon: UserCheck, label: 'Pending Approvals' },
      ]
    }

    return baseItems
  }

  const navItems = getNavItems()

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-background to-primary-100">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-primary-900 bg-opacity-30 z-40 lg:hidden backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-white/95 backdrop-blur-sm shadow-xl transform transition-transform duration-300 ease-in-out border-r border-primary-100
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-primary-100 bg-gradient-to-r from-primary-50 to-white">
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-800 rounded-lg flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow duration-300">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold text-primary-800">Vocalysis</span>
              <span className="block text-xs text-primary-500 italic">by Cittaa</span>
            </div>
          </Link>
          <button 
            className="lg:hidden p-2 rounded-lg hover:bg-primary-100 transition-colors duration-200"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-5 h-5 text-primary-600" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-300
                ${isActive(item.path) 
                  ? 'bg-primary-200 text-primary-800 font-medium shadow-sm' 
                  : 'text-primary-700 hover:bg-primary-100 hover:text-primary-800'
                }
              `}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon className={`w-5 h-5 ${isActive(item.path) ? 'text-primary-700' : 'text-primary-500'}`} />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* User info at bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-primary-100 bg-gradient-to-r from-primary-50 to-white">
          <div className="flex items-center space-x-3 px-2 py-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center shadow-md">
              <span className="text-white font-medium">
                {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-primary-800 truncate">
                {user?.full_name || 'User'}
              </p>
              <p className="text-xs text-primary-500 truncate capitalize">
                {user?.role?.replace('_', ' ')}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Top header */}
        <header className="h-16 bg-white/80 backdrop-blur-sm shadow-sm flex items-center justify-between px-4 lg:px-6 border-b border-primary-100">
          <button 
            className="lg:hidden p-2 rounded-lg hover:bg-primary-100 transition-colors duration-200"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-6 h-6 text-primary-700" />
          </button>

          <div className="flex-1 lg:flex-none" />

          {/* User menu */}
          <div className="relative">
            <button 
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-primary-100 transition-colors duration-200"
              onClick={() => setUserMenuOpen(!userMenuOpen)}
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center shadow-sm">
                <span className="text-white text-sm font-medium">
                  {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </span>
              </div>
              <ChevronDown className="w-4 h-4 text-primary-600" />
            </button>

            {userMenuOpen && (
              <>
                <div 
                  className="fixed inset-0 z-10"
                  onClick={() => setUserMenuOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-primary-100 py-1 z-20 animate-scale-in">
                  <div className="px-4 py-2 border-b border-primary-100 bg-primary-50">
                    <p className="text-sm font-medium text-primary-800 truncate">
                      {user?.full_name || 'User'}
                    </p>
                    <p className="text-xs text-primary-500 truncate">
                      {user?.email}
                    </p>
                  </div>
                  <button
                    className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-primary-700 hover:bg-primary-50 transition-colors duration-200"
                    onClick={() => {
                      setUserMenuOpen(false)
                      // Navigate to settings
                    }}
                  >
                    <Settings className="w-4 h-4" />
                    <span>Settings</span>
                  </button>
                  <button
                    className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-error hover:bg-red-50 transition-colors duration-200"
                    onClick={handleLogout}
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
