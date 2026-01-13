import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Activity, Mail, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await login(email, password)
      // Redirect based on user role
      const userRole = response?.role || localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user') || '{}').role : 'patient'
      switch (userRole) {
        case 'psychologist':
          navigate('/psychologist/dashboard')
          break
        case 'super_admin':
        case 'hr_admin':
          navigate('/admin/dashboard')
          break
        case 'researcher':
          navigate('/dashboard')
          break
        default:
          navigate('/dashboard')
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 
        'Login failed. Please check your credentials.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-lavender flex items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative floral elements */}
      <div className="absolute top-0 right-0 w-64 h-64 opacity-30">
        <svg viewBox="0 0 200 200" className="w-full h-full">
          <circle cx="150" cy="50" r="8" fill="#6B9B6B" className="animate-pulse-soft" />
          <circle cx="170" cy="80" r="6" fill="#9B7B9B" className="animate-pulse-soft" style={{ animationDelay: '0.5s' }} />
          <circle cx="130" cy="70" r="10" fill="#DCC8DC" className="animate-pulse-soft" style={{ animationDelay: '1s' }} />
          <path d="M140 30 Q160 50 140 70 Q120 50 140 30" fill="#6B9B6B" opacity="0.6" />
          <path d="M160 60 Q180 80 160 100 Q140 80 160 60" fill="#9B7B9B" opacity="0.5" />
        </svg>
      </div>
      <div className="absolute bottom-0 left-0 w-48 h-48 opacity-30">
        <svg viewBox="0 0 200 200" className="w-full h-full">
          <circle cx="50" cy="150" r="8" fill="#6B9B6B" className="animate-pulse-soft" />
          <circle cx="30" cy="120" r="6" fill="#9B7B9B" className="animate-pulse-soft" style={{ animationDelay: '0.3s' }} />
          <path d="M60 170 Q40 150 60 130 Q80 150 60 170" fill="#6B9B6B" opacity="0.6" />
        </svg>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo and Title */}
        <div className="text-center mb-8 animate-slide-up">
          <h1 className="text-4xl font-display italic text-primary-800 mb-2">Cittaa</h1>
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-purple rounded-2xl shadow-lg mb-4 animate-float">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-primary-700">Vocalysis</h2>
          <p className="text-primary-600 mt-1">Voice-based Mental Health Screening</p>
          <p className="text-sm text-primary-500 mt-2 italic">Healing is a journey. We will walk beside you.</p>
        </div>

        {/* Login Form */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-8 animate-scale-in border border-primary-200" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-2xl font-semibold text-primary-800 mb-6">Welcome Back</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-red-600 animate-fadeIn">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-12 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`
                w-full py-3 px-4 rounded-lg font-medium text-white
                bg-primary-800 hover:bg-primary-700
                focus:ring-4 focus:ring-primary-300
                transition-all duration-300 transform hover:scale-[1.02] hover:shadow-lg
                ${loading ? 'opacity-70 cursor-not-allowed' : ''}
              `}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-4 text-center">
            <Link to="/forgot-password" className="text-primary-700 hover:text-primary-800 text-sm font-medium">
              Forgot your password?
            </Link>
          </div>

          <div className="mt-4 text-center">
            <p className="text-primary-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary-800 hover:text-primary-900 font-medium underline underline-offset-2">
                Register here
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-primary-600 text-sm mt-6">
          &copy; 2026 CITTAA Health Services Private Limited
        </p>
      </div>
    </div>
  )
}
