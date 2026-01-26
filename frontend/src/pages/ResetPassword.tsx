import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Activity, Lock, Eye, EyeOff, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [token, setToken] = useState('')

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (!tokenParam) {
      setError('Invalid or missing reset token. Please request a new password reset.')
    } else {
      setToken(tokenParam)
    }
  }, [searchParams])

  const validatePassword = (pwd: string): string | null => {
    if (pwd.length < 8) {
      return 'Password must be at least 8 characters long'
    }
    if (!/[A-Z]/.test(pwd)) {
      return 'Password must contain at least one uppercase letter'
    }
    if (!/[a-z]/.test(pwd)) {
      return 'Password must contain at least one lowercase letter'
    }
    if (!/[0-9]/.test(pwd)) {
      return 'Password must contain at least one number'
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) {
      return 'Password must contain at least one special character'
    }
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    // Validate password strength
    const passwordError = validatePassword(password)
    if (passwordError) {
      setError(passwordError)
      return
    }

    setLoading(true)

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'https://vocalysis-backend-1081764900204.us-central1.run.app'
      const response = await fetch(`${API_URL}/api/v1/auth/reset-password?token=${encodeURIComponent(token)}&new_password=${encodeURIComponent(password)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to reset password')
      }

      setSuccess(true)
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login')
      }, 3000)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 
        'Failed to reset password. The link may have expired.'
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

        {/* Reset Password Form */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl p-8 animate-scale-in border border-primary-200" style={{ animationDelay: '0.1s' }}>
          {success ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-success" />
              </div>
              <h2 className="text-xl font-semibold text-primary-800 mb-2">Password Reset Successful!</h2>
              <p className="text-primary-600 mb-6">
                Your password has been reset successfully. You will be redirected to the login page shortly.
              </p>
              <Link
                to="/login"
                className="inline-flex items-center justify-center w-full py-3 px-4 rounded-xl font-medium text-white bg-primary-800 hover:bg-primary-900 transition-all duration-200"
              >
                Go to Sign In
              </Link>
            </div>
          ) : (
            <>
              <h2 className="text-2xl font-semibold text-primary-800 mb-2">Reset Your Password</h2>
              <p className="text-primary-600 mb-6">
                Enter your new password below. Make sure it's strong and secure.
              </p>

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-red-600 animate-fade-in">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              {!token ? (
                <div className="text-center">
                  <Link
                    to="/forgot-password"
                    className="inline-flex items-center justify-center w-full py-3 px-4 rounded-xl font-medium text-white bg-primary-800 hover:bg-primary-900 transition-all duration-200"
                  >
                    Request New Reset Link
                  </Link>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-primary-700 mb-2">
                      New Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-primary-400" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full pl-10 pr-12 py-3 border border-primary-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 bg-white/50"
                        placeholder="Enter new password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-primary-400 hover:text-primary-600"
                      >
                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-primary-700 mb-2">
                      Confirm New Password
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-primary-400" />
                      <input
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full pl-10 pr-12 py-3 border border-primary-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 bg-white/50"
                        placeholder="Confirm new password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-primary-400 hover:text-primary-600"
                      >
                        {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>

                  <div className="text-xs text-primary-500 bg-primary-50 p-3 rounded-lg">
                    <p className="font-medium mb-1">Password requirements:</p>
                    <ul className="list-disc list-inside space-y-0.5">
                      <li>At least 8 characters long</li>
                      <li>One uppercase letter</li>
                      <li>One lowercase letter</li>
                      <li>One number</li>
                      <li>One special character (!@#$%^&*)</li>
                    </ul>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className={`
                      w-full py-3 px-4 rounded-xl font-medium text-white
                      bg-primary-800 hover:bg-primary-900
                      focus:ring-4 focus:ring-primary-200
                      transition-all duration-200
                      ${loading ? 'opacity-70 cursor-not-allowed' : ''}
                    `}
                  >
                    {loading ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Resetting Password...
                      </span>
                    ) : (
                      'Reset Password'
                    )}
                  </button>
                </form>
              )}

              <div className="mt-6 text-center">
                <Link
                  to="/login"
                  className="inline-flex items-center text-primary-600 hover:text-primary-700 font-medium"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Sign In
                </Link>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-primary-500 text-xs mt-6">
          &copy; 2026 CITTAA Health Services Private Limited
        </p>
      </div>
    </div>
  )
}
