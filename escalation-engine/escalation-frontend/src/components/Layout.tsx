import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { 
  LayoutDashboard, FileText, AlertTriangle, GraduationCap,
  LogOut, Menu, X, Shield, ChevronDown, User
} from 'lucide-react';
import { CITTAA_COLORS } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/reports', label: 'Reports', icon: FileText },
    { path: '/escalations', label: 'Escalations', icon: AlertTriangle },
    { path: '/students', label: 'Students', icon: GraduationCap },
  ];

  if (user?.role === 'admin') {
    navItems.push({ path: '/admin', label: 'Admin', icon: Shield });
  }

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen" style={{ backgroundColor: CITTAA_COLORS.lightBg }}>
      <aside
        className={`fixed top-0 left-0 z-40 h-screen transition-transform duration-300 ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width: '260px', backgroundColor: 'white' }}
      >
        <div className="h-full flex flex-col border-r">
          <div className="p-4 border-b">
            <div className="flex items-center gap-3">
              <div 
                className="w-10 h-10 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: CITTAA_COLORS.purple }}
              >
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 
                  className="text-xl font-bold"
                  style={{ color: CITTAA_COLORS.purple }}
                >
                  CITTAA
                </h1>
                <p className="text-xs text-gray-500">Escalation Engine</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    active ? 'text-white' : 'text-gray-600 hover:bg-gray-100'
                  }`}
                  style={active ? { backgroundColor: CITTAA_COLORS.purple } : {}}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t">
            <div className="relative">
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div 
                  className="w-10 h-10 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: `${CITTAA_COLORS.teal}20` }}
                >
                  <User className="w-5 h-5" style={{ color: CITTAA_COLORS.teal }} />
                </div>
                <div className="flex-1 text-left">
                  <p className="text-sm font-medium truncate">{user?.full_name}</p>
                  <p className="text-xs text-gray-500 truncate">{user?.role?.replace('_', ' ')}</p>
                </div>
                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isProfileOpen ? 'rotate-180' : ''}`} />
              </button>

              {isProfileOpen && (
                <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border rounded-lg shadow-lg overflow-hidden">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut className="w-5 h-5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>

      <div 
        className={`transition-all duration-300 ${isSidebarOpen ? 'ml-[260px]' : 'ml-0'}`}
      >
        <header className="sticky top-0 z-30 bg-white border-b">
          <div className="flex items-center justify-between px-6 py-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="flex items-center gap-4">
              <span 
                className="text-sm px-3 py-1 rounded-full"
                style={{ 
                  backgroundColor: `${CITTAA_COLORS.teal}20`,
                  color: CITTAA_COLORS.teal
                }}
              >
                {user?.institution_id ? 'Institution User' : 'System User'}
              </span>
            </div>
          </div>
        </header>

        <main className="p-6">
          {children}
        </main>

        <footer className="border-t bg-white p-4 text-center">
          <p className="text-xs text-gray-500">
            CITTAA Health Services Private Limited - Bridging Mental Health Gaps Through Intelligent Wellness Solutions
          </p>
        </footer>
      </div>
    </div>
  );
}
