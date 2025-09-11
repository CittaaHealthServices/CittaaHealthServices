import { useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Shield, 
  Eye, 
  Fingerprint, 
  CheckCircle, 
  AlertCircle, 
  ArrowLeft,
  Info,
  Users,
  Calendar
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useFamily } from '@/contexts/FamilyContext'
import { familyApi } from '@/lib/api'

export default function ConsentManagementPage() {
  const [searchParams] = useSearchParams()
  const selectedChildId = searchParams.get('child')
  const { token } = useAuth()
  const { children, consentOverview, refreshFamily } = useFamily()
  const [loading, setLoading] = useState(false)
  const [selectedChild, setSelectedChild] = useState<number | null>(
    selectedChildId ? parseInt(selectedChildId) : null
  )

  const consentTypes = [
    {
      id: 'content_filtering',
      name: 'Content Filtering',
      icon: Shield,
      description: 'Blocks inappropriate content and shows educational alternatives',
      ageExplanations: {
        under_13: 'We help block websites that might not be good for kids your age, and show you fun learning websites instead!',
        teen: 'Content filtering protects you from inappropriate material and promotes educational resources.',
        adult: 'Content filtering system with transparent criteria and appeal processes.'
      }
    },
    {
      id: 'activity_monitoring',
      name: 'Activity Monitoring',
      icon: Eye,
      description: 'Transparent monitoring of online activity with full disclosure',
      ageExplanations: {
        under_13: 'Your parents can see what websites and apps you use to make sure you\'re safe.',
        teen: 'Your online activity is monitored for safety. You can always discuss any concerns with your parents.',
        adult: 'Activity monitoring with full transparency and data access rights.'
      }
    },
    {
      id: 'biometric_data',
      name: 'Biometric Authentication',
      icon: Fingerprint,
      description: 'Face or fingerprint recognition for secure account access',
      ageExplanations: {
        under_13: 'We use your face or fingerprint to know it\'s really you when you use your device.',
        teen: 'Biometric authentication for secure access. This data is encrypted and only used for verification.',
        adult: 'Biometric data collection for authentication with full control and opt-out options.'
      }
    }
  ]

  const handleConsentChange = async (childId: number, consentType: string, given: boolean) => {
    if (!token) return

    setLoading(true)
    try {
      const child = children.find(c => c.id === childId)
      const requiresParentConsent = child && child.age < 18

      await familyApi.manageConsent(token, {
        child_id: childId,
        consent_type: consentType,
        consent_given: given,
        parent_consent: requiresParentConsent || false
      })

      await refreshFamily()
    } catch (error) {
      console.error('Failed to update consent:', error)
    } finally {
      setLoading(false)
    }
  }

  const getChildConsent = (childId: number) => {
    return consentOverview.find(c => c.child_id === childId)
  }

  const getAgeCategory = (age: number) => {
    if (age < 13) return 'under_13'
    if (age < 18) return 'teen'
    return 'adult'
  }

  const getConsentRequirements = (age: number) => {
    if (age < 13) {
      return {
        requiresParent: true,
        requiresChild: true,
        canWithdraw: false,
        explanation: 'Children under 13 require both parent consent and child assent'
      }
    } else if (age < 18) {
      return {
        requiresParent: true,
        requiresChild: true,
        canWithdraw: true,
        explanation: 'Teens require both parent and child consent, with withdrawal rights'
      }
    } else {
      return {
        requiresParent: false,
        requiresChild: true,
        canWithdraw: true,
        explanation: 'Adults provide their own consent with full withdrawal rights'
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 space-x-4">
            <Button variant="ghost" asChild>
              <Link to="/dashboard">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Link>
            </Button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Consent Management</h1>
              <p className="text-sm text-gray-600">Transparent consent with age-appropriate explanations</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="h-5 w-5" />
                  <span>Family Members</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {children.map((child) => (
                  <Button
                    key={child.id}
                    variant={selectedChild === child.id ? "default" : "outline"}
                    className="w-full justify-start"
                    onClick={() => setSelectedChild(child.id)}
                  >
                    <div className="text-left">
                      <div className="font-medium">{child.name}</div>
                      <div className="text-xs opacity-70">Age {child.age}</div>
                    </div>
                  </Button>
                ))}
              </CardContent>
            </Card>

            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Info className="h-5 w-5" />
                  <span>Compliance Info</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>DPDP Act 2023 Compliant</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Age-Appropriate Consent</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Transparent Explanations</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Withdrawal Rights</span>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-3">
            {selectedChild ? (
              <ChildConsentDetails
                child={children.find(c => c.id === selectedChild)!}
                consent={getChildConsent(selectedChild)}
                consentTypes={consentTypes}
                onConsentChange={handleConsentChange}
                loading={loading}
                getAgeCategory={getAgeCategory}
                getConsentRequirements={getConsentRequirements}
              />
            ) : (
              <Card>
                <CardContent className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Family Member</h3>
                    <p className="text-gray-600">Choose a child from the sidebar to manage their consent settings</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

function ChildConsentDetails({ 
  child, 
  consent, 
  consentTypes, 
  onConsentChange, 
  loading,
  getAgeCategory,
  getConsentRequirements 
}: any) {
  const ageCategory = getAgeCategory(child.age)
  const requirements = getConsentRequirements(child.age)

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{child.name}'s Consent Settings</span>
            <Badge variant="outline">Age {child.age}</Badge>
          </CardTitle>
          <CardDescription>
            {requirements.explanation}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              All consent explanations are age-appropriate and transparent. 
              {child.age < 18 && " Parent consent is required for all features."}
              {requirements.canWithdraw && " Consent can be withdrawn at any time."}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {consentTypes.map((type: any) => {
          const Icon = type.icon
          const childConsent = consent?.consents[type.id]
          const isGiven = childConsent?.given || false
          const consentDate = childConsent?.date

          return (
            <Card key={type.id}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Icon className="h-6 w-6 text-blue-600" />
                    <div>
                      <h3 className="text-lg font-medium">{type.name}</h3>
                      <p className="text-sm text-gray-600">{type.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {isGiven && (
                      <div className="text-right text-sm text-gray-600">
                        <div>Consented</div>
                        {consentDate && (
                          <div className="flex items-center space-x-1">
                            <Calendar className="h-3 w-3" />
                            <span>{new Date(consentDate).toLocaleDateString()}</span>
                          </div>
                        )}
                      </div>
                    )}
                    <Switch
                      checked={isGiven}
                      onCheckedChange={(checked) => onConsentChange(child.id, type.id, checked)}
                      disabled={loading}
                    />
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">
                    Age-Appropriate Explanation for {child.name}:
                  </h4>
                  <p className="text-blue-800 text-sm">
                    {type.ageExplanations[ageCategory]}
                  </p>
                </div>
                
                {isGiven && (
                  <div className="mt-4 flex items-center space-x-2 text-sm text-green-700">
                    <CheckCircle className="h-4 w-4" />
                    <span>
                      Consent given with full understanding and transparency
                      {requirements.requiresParent && " (Parent consent also provided)"}
                    </span>
                  </div>
                )}
                
                {!isGiven && (
                  <div className="mt-4 flex items-center space-x-2 text-sm text-gray-600">
                    <AlertCircle className="h-4 w-4" />
                    <span>
                      This feature is not active. Consent required to enable protection.
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {requirements.canWithdraw && (
        <Card>
          <CardHeader>
            <CardTitle className="text-red-700">Withdrawal Rights</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              {child.name} has the right to withdraw consent for any feature at any time. 
              Withdrawal will immediately disable the associated protection and monitoring.
            </p>
            <Button variant="outline" className="text-red-600 border-red-600 hover:bg-red-50">
              Withdraw All Consent
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
