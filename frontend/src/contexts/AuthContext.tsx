import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService, User } from '../services/api'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  registerClinicalTrial: (data: ClinicalTrialRegisterData) => Promise<User>
  logout: () => void
  updateUser: (data: Partial<User>) => void
}

interface RegisterData {
  email: string
  password: string
  full_name?: string
  phone?: string
  role?: string
}

interface ClinicalTrialRegisterData {
  email: string
  password: string
  full_name?: string
  phone?: string
  age_range?: string
  gender?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password)
    localStorage.setItem('token', response.access_token)
    localStorage.setItem('user', JSON.stringify(response.user))
    setUser(response.user)
  }

  const register = async (data: RegisterData) => {
    const response = await authService.register(data)
    localStorage.setItem('token', response.access_token)
    localStorage.setItem('user', JSON.stringify(response.user))
    setUser(response.user)
  }

  const registerClinicalTrial = async (data: ClinicalTrialRegisterData): Promise<User> => {
    const response = await authService.registerClinicalTrial(data)
    // Don't set user as logged in - they need admin approval first
    // Just return the user data so the UI can show pending status
    return response.user
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const updateUser = (data: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...data }
      localStorage.setItem('user', JSON.stringify(updatedUser))
      setUser(updatedUser)
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      loading,
      login,
      register,
      registerClinicalTrial,
      logout,
      updateUser
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
