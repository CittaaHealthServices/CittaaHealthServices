import { 
  LayoutDashboard, 
  Users, 
  UserCheck, 
  Ticket, 
  BarChart3, 
  Settings, 
  LogOut,
  Mic
} from 'lucide-react'
import type { Page } from '../App'

interface SidebarProps {
  currentPage: Page
  onPageChange: (page: Page) => void
  onLogout: () => void
}

const menuItems = [
  { id: 'dashboard' as Page, label: 'Dashboard', icon: LayoutDashboard },
  { id: 'patients' as Page, label: 'Patient Approval', icon: UserCheck },
  { id: 'psychologists' as Page, label: 'Psychologist Mapping', icon: Users },
  { id: 'coupons' as Page, label: 'Coupon Management', icon: Ticket },
  { id: 'users' as Page, label: 'User Management', icon: Users },
  { id: 'analytics' as Page, label: 'Analytics', icon: BarChart3 },
  { id: 'settings' as Page, label: 'Settings', icon: Settings },
]

export function Sidebar({ currentPage, onPageChange, onLogout }: SidebarProps) {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-blue-600 rounded-xl flex items-center justify-center">
            <Mic className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-green-700" style={{ fontFamily: 'cursive' }}>
              Cittaa
            </h1>
            <p className="text-xs text-gray-500">Vocalysis Admin</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = currentPage === item.id
          
          return (
            <button
              key={item.id}
              onClick={() => onPageChange(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-green-50 text-green-700 border-l-4 border-green-600'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-green-600' : 'text-gray-400'}`} />
              {item.label}
            </button>
          )
        })}
      </nav>

      {/* User & Logout */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3 px-4 py-2 mb-2">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-green-700">A</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">Admin User</p>
            <p className="text-xs text-gray-500 truncate">admin@cittaa.in</p>
          </div>
        </div>
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  )
}
