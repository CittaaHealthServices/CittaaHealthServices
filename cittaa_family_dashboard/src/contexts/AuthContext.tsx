import React, { createContext, useContext, useState, useEffect } from 'react'

interface AuthContextType {
  isAuthenticated: boolean
  token: string | null
  parentId: number | null
  familyId: number | null
  loading: boolean
  login: (token: string, parentId: number, familyId: number) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [token, setToken] = useState<string | null>(null)
  const [parentId, setParentId] = useState<number | null>(null)
  const [familyId, setFamilyId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('auth_token')
    const storedParentId = localStorage.getItem('parent_id')
    const storedFamilyId = localStorage.getItem('family_id')

    if (storedToken && storedParentId && storedFamilyId) {
      setToken(storedToken)
      setParentId(parseInt(storedParentId))
      setFamilyId(parseInt(storedFamilyId))
      setIsAuthenticated(true)
    } else {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('parent_id')
      localStorage.removeItem('family_id')
    }
    setLoading(false)
  }, [])

  const login = (token: string, parentId: number, familyId: number) => {
    localStorage.setItem('auth_token', token)
    localStorage.setItem('parent_id', parentId.toString())
    localStorage.setItem('family_id', familyId.toString())
    
    setToken(token)
    setParentId(parentId)
    setFamilyId(familyId)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('parent_id')
    localStorage.removeItem('family_id')
    
    setToken(null)
    setParentId(null)
    setFamilyId(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{
      isAuthenticated,
      token,
      parentId,
      familyId,
      loading,
      login,
      logout
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
