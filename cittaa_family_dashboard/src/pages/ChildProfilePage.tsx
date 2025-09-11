import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  ArrowLeft, 
  Shield, 
  Activity, 
  BookOpen, 
  CheckCircle,
  AlertCircle,
  Globe,
  Smartphone
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useFamily } from '@/contexts/FamilyContext'
import { familyApi } from '@/lib/api'

export default function ChildProfilePage() {
  const { childId } = useParams()
  const { token } = useAuth()
  const { children, consentOverview } = useFamily()
  const [childActivity, setChildActivity] = useState<any[]>([])
  const [educationalProgress, setEducationalProgress] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const child = children.find(c => c.id === parseInt(childId!))
  const childConsent = consentOverview.find(c => c.child_id === parseInt(childId!))

  useEffect(() => {
    if (childId && token) {
      loadChildData()
    }
  }, [childId, token])

  const loadChildData = async () => {
    if (!token || !childId) return

    setLoading(true)
    try {
      const [activityResponse, progressResponse] = await Promise.all([
        familyApi.getChildActivity(token, parseInt(childId)),
        familyApi.getEducationalProgress(token, parseInt(childId))
      ])
      
      setChildActivity(activityResponse as any[])
      setEducationalProgress(progressResponse as any[])
    } catch (error) {
      console.error('Failed to load child data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!child) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Child Not Found</h2>
          <p className="text-gray-600 mb-4">The requested child profile could not be found.</p>
          <Button asChild>
            <Link to="/dashboard">Return to Dashboard</Link>
          </Button>
        </div>
      </div>
    )
  }

  const getConsentStatus = () => {
    if (!childConsent) return { total: 0, given: 0 }
    const consents = Object.values(childConsent.consents)
    return {
      total: consents.length,
      given: consents.filter((c: any) => c.given).length
    }
  }

  const consentStatus = getConsentStatus()

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
              <h1 className="text-xl font-bold text-gray-900">{child.name}'s Profile</h1>
              <p className="text-sm text-gray-600">Age {child.age} • Transparent Safety Profile</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Safety Status</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {child.profile_active ? 'Protected' : 'Inactive'}
              </div>
              <Badge variant={child.profile_active ? "default" : "secondary"} className="mt-1">
                {child.profile_active ? 'Active' : 'Inactive'}
              </Badge>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Consent Status</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{consentStatus.given}/{consentStatus.total}</div>
              <Progress value={(consentStatus.given / consentStatus.total) * 100} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-1">
                Consents provided
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Today's Activity</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{childActivity.length}</div>
              <p className="text-xs text-muted-foreground">
                Logged activities
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Learning Progress</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {educationalProgress.filter((p: any) => p.completed).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Lessons completed
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
            <TabsTrigger value="education">Education</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Consent Overview</CardTitle>
                  <CardDescription>
                    Transparent consent status with age-appropriate explanations
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {childConsent && Object.entries(childConsent.consents).map(([type, consent]: [string, any]) => (
                    <div key={type} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium capitalize">{type.replace('_', ' ')}</p>
                        <p className="text-sm text-gray-600">
                          {consent.date ? `Consented on ${new Date(consent.date).toLocaleDateString()}` : 'Not consented'}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {consent.given ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : (
                          <AlertCircle className="h-5 w-5 text-red-600" />
                        )}
                        {consent.parent_consent && (
                          <Badge variant="secondary" className="text-xs">Parent</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  <Button asChild className="w-full">
                    <Link to={`/consent?child=${child.id}`}>Manage Consent</Link>
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Safety Features</CardTitle>
                  <CardDescription>
                    Active protection measures with transparent operation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Shield className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="font-medium">Content Filtering</p>
                        <p className="text-sm text-gray-600">Blocks inappropriate content</p>
                      </div>
                    </div>
                    <Badge variant={child.profile_active ? "default" : "secondary"}>
                      {child.profile_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Activity className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="font-medium">Activity Monitoring</p>
                        <p className="text-sm text-gray-600">Transparent activity tracking</p>
                      </div>
                    </div>
                    <Badge variant={child.profile_active ? "default" : "secondary"}>
                      {child.profile_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Smartphone className="h-5 w-5 text-purple-600" />
                      <div>
                        <p className="font-medium">Biometric Auth</p>
                        <p className="text-sm text-gray-600">Secure device access</p>
                      </div>
                    </div>
                    <Badge variant={child.biometric_enabled ? "default" : "secondary"}>
                      {child.biometric_enabled ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="activity" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                  Transparent monitoring with full disclosure to {child.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-8">
                    <Activity className="h-8 w-8 text-gray-400 mx-auto animate-pulse" />
                    <p className="mt-2 text-gray-600">Loading activity...</p>
                  </div>
                ) : childActivity.length > 0 ? (
                  <div className="space-y-3">
                    {childActivity.map((activity: any) => (
                      <div key={activity.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          {activity.blocked ? (
                            <Shield className="h-5 w-5 text-red-500" />
                          ) : (
                            <Globe className="h-5 w-5 text-green-500" />
                          )}
                          <div>
                            <p className="font-medium">{activity.description}</p>
                            <p className="text-sm text-gray-600">
                              {activity.url || activity.app_name}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={activity.blocked ? "destructive" : "default"}>
                            {activity.blocked ? "Blocked" : "Allowed"}
                          </Badge>
                          <p className="text-xs text-gray-600 mt-1">
                            {new Date(activity.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Activity className="h-8 w-8 text-gray-400 mx-auto" />
                    <p className="mt-2 text-gray-600">No recent activity</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="education" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Digital Citizenship Progress</CardTitle>
                <CardDescription>
                  Educational curriculum integrated with safety features
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-8">
                    <BookOpen className="h-8 w-8 text-gray-400 mx-auto animate-pulse" />
                    <p className="mt-2 text-gray-600">Loading progress...</p>
                  </div>
                ) : educationalProgress.length > 0 ? (
                  <div className="space-y-4">
                    {educationalProgress.map((lesson: any, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <BookOpen className="h-5 w-5 text-blue-600" />
                          <div>
                            <p className="font-medium">{lesson.lesson_title}</p>
                            <p className="text-sm text-gray-600">{lesson.lesson_type}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={lesson.completed ? "default" : "secondary"}>
                            {lesson.completed ? "Completed" : "In Progress"}
                          </Badge>
                          {lesson.score && (
                            <p className="text-sm text-gray-600 mt-1">
                              Score: {lesson.score}%
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BookOpen className="h-8 w-8 text-gray-400 mx-auto" />
                    <p className="mt-2 text-gray-600">No educational progress yet</p>
                    <Button className="mt-4">Start Learning Journey</Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Profile Settings</CardTitle>
                <CardDescription>
                  Manage {child.name}'s safety profile and preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Safety Profile</p>
                    <p className="text-sm text-gray-600">Enable/disable protection features</p>
                  </div>
                  <Button variant="outline">Configure</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Biometric Authentication</p>
                    <p className="text-sm text-gray-600">Face/fingerprint recognition settings</p>
                  </div>
                  <Button variant="outline">Manage</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Privacy Settings</p>
                    <p className="text-sm text-gray-600">Data access and privacy controls</p>
                  </div>
                  <Button variant="outline">Review</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Educational Preferences</p>
                    <p className="text-sm text-gray-600">Learning goals and curriculum</p>
                  </div>
                  <Button variant="outline">Customize</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
