import React, { createContext, useContext, useState, useEffect } from 'react'

interface AuthContextType {
  isAuthenticated: boolean
  token: string | null
  parentId: number | null
  familyId: number | null
  login: (token: string, parentId: number, familyId: number) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [token, setToken] = useState<string | null>(null)
  const [parentId, setParentId] = useState<number | null>(null)
  const [familyId, setFamilyId] = useState<number | null>(null)

  useEffect(() => {
    const storedToken = localStorage.getItem('cittaa_token')
    const storedParentId = localStorage.getItem('cittaa_parent_id')
    const storedFamilyId = localStorage.getItem('cittaa_family_id')

    if (storedToken && storedParentId && storedFamilyId) {
      setToken(storedToken)
      setParentId(parseInt(storedParentId))
      setFamilyId(parseInt(storedFamilyId))
      setIsAuthenticated(true)
    }
  }, [])

  const login = (token: string, parentId: number, familyId: number) => {
    localStorage.setItem('cittaa_token', token)
    localStorage.setItem('cittaa_parent_id', parentId.toString())
    localStorage.setItem('cittaa_family_id', familyId.toString())
    
    setToken(token)
    setParentId(parentId)
    setFamilyId(familyId)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('cittaa_token')
    localStorage.removeItem('cittaa_parent_id')
    localStorage.removeItem('cittaa_family_id')
    
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
