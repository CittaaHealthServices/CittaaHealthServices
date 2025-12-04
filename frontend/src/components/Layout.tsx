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

    if (user?.role === 'super_admin' || user?.role === 'hr_admin' || user?.role === 'admin') {
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
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-100">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-400 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold text-primary-500">Vocalysis</span>
              <span className="block text-xs text-gray-500">by CITTAA</span>
            </div>
          </Link>
          <button 
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                ${isActive(item.path) 
                  ? 'bg-primary-50 text-primary-600 font-medium' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-primary-500'
                }
              `}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon className={`w-5 h-5 ${isActive(item.path) ? 'text-primary-500' : ''}`} />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* User info at bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-100">
          <div className="flex items-center space-x-3 px-2 py-2">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
              <span className="text-white font-medium">
                {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.full_name || 'User'}
              </p>
              <p className="text-xs text-gray-500 truncate capitalize">
                {user?.role?.replace('_', ' ')}
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Top header */}
        <header className="h-16 bg-white shadow-sm flex items-center justify-between px-4 lg:px-6">
          <button 
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-6 h-6 text-gray-600" />
          </button>

          <div className="flex-1 lg:flex-none" />

          {/* User menu */}
          <div className="relative">
            <button 
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100"
              onClick={() => setUserMenuOpen(!userMenuOpen)}
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                </span>
              </div>
              <ChevronDown className="w-4 h-4 text-gray-500" />
            </button>

            {userMenuOpen && (
              <>
                <div 
                  className="fixed inset-0 z-10"
                  onClick={() => setUserMenuOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-20 animate-fadeIn">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {user?.full_name || 'User'}
                    </p>
                    <p className="text-xs text-gray-500 truncate">
                      {user?.email}
                    </p>
                  </div>
                  <button
                    className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => {
                      setUserMenuOpen(false)
                      // Navigate to settings
                    }}
                  >
                    <Settings className="w-4 h-4" />
                    <span>Settings</span>
                  </button>
                  <button
                    className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-error hover:bg-red-50"
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
