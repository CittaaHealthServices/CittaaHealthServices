import React, { createContext, useContext, useState, useEffect } from 'react'
import { useAuth } from './AuthContext'
import { familyApi } from '@/lib/api'

interface Child {
  id: number
  name: string
  age: number
  profile_active: boolean
  biometric_enabled: boolean
}

interface ConsentStatus {
  content_filtering: {
    given: boolean
    date: string | null
    parent_consent: boolean
  }
  activity_monitoring: {
    given: boolean
    date: string | null
    parent_consent: boolean
  }
  biometric_data: {
    given: boolean
    date: string | null
    parent_consent: boolean
  }
}

interface FamilyContextType {
  family: {
    id: number
    name: string
    created_at: string
  } | null
  children: Child[]
  consentOverview: any[]
  loading: boolean
  refreshFamily: () => Promise<void>
}

const FamilyContext = createContext<FamilyContextType | undefined>(undefined)

export function FamilyProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, token } = useAuth()
  const [family, setFamily] = useState(null)
  const [childrenData, setChildrenData] = useState<Child[]>([])
  const [consentOverview, setConsentOverview] = useState([])
  const [loading, setLoading] = useState(false)

  const refreshFamily = async () => {
    if (!isAuthenticated || !token) return

    setLoading(true)
    try {
      const response = await familyApi.getOverview(token)
      setFamily(response.family)
      setChildrenData(response.children)
      setConsentOverview(response.consent_overview)
    } catch (error) {
      console.error('Failed to fetch family data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      refreshFamily()
    }
  }, [isAuthenticated])

  return (
    <FamilyContext.Provider value={{
      family,
      children: childrenData,
      consentOverview,
      loading,
      refreshFamily
    }}>
      {children}
    </FamilyContext.Provider>
  )
}

export function useFamily() {
  const context = useContext(FamilyContext)
  if (context === undefined) {
    throw new Error('useFamily must be used within a FamilyProvider')
  }
  return context
}
