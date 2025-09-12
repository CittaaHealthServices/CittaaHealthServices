import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Shield, 
  Users, 
  Activity, 
  BookOpen, 
  CheckCircle, 
  AlertCircle,
  Clock,
  Heart,
  LogOut
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useFamily } from '@/contexts/FamilyContext'

export default function DashboardPage() {
  const { logout } = useAuth()
  const { family, children, consentOverview, loading, refreshFamily } = useFamily()

  useEffect(() => {
    refreshFamily()
  }, [])

  const getConsentStatus = (childConsents: any) => {
    const totalConsents = Object.keys(childConsents).length
    const givenConsents = Object.values(childConsents).filter((consent: any) => consent.given).length
    return { total: totalConsents, given: givenConsents }
  }

  const getOverallComplianceScore = () => {
    if (consentOverview.length === 0) return 0
    
    let totalPossibleConsents = 0
    let totalGivenConsents = 0
    
    consentOverview.forEach(child => {
      const status = getConsentStatus(child.consents)
      totalPossibleConsents += status.total
      totalGivenConsents += status.given
    })
    
    return totalPossibleConsents > 0 ? Math.round((totalGivenConsents / totalPossibleConsents) * 100) : 0
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Shield className="h-12 w-12 text-blue-600 mx-auto animate-pulse" />
          <p className="mt-4 text-gray-600">Loading family dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">CITTAA Family Safety</h1>
                <p className="text-sm text-gray-600">{family?.name} Family Dashboard</p>
              </div>
            </div>
            <Button variant="outline" onClick={logout} className="flex items-center space-x-2">
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Family Members</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{children.length}</div>
              <p className="text-xs text-muted-foreground">
                Children protected
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{getOverallComplianceScore()}%</div>
              <Progress value={getOverallComplianceScore()} className="mt-2" />
              <p className="text-xs text-muted-foreground mt-1">
                DPDP Act 2023 compliance
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Profiles</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {children.filter(child => child.profile_active).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Currently protected
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Family Trust</CardTitle>
              <Heart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">95%</div>
              <p className="text-xs text-muted-foreground">
                Transparency satisfaction
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="children" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="children">Children</TabsTrigger>
            <TabsTrigger value="consent">Consent Status</TabsTrigger>
            <TabsTrigger value="activity">Recent Activity</TabsTrigger>
            <TabsTrigger value="education">Education</TabsTrigger>
            <TabsTrigger value="mobile">Mobile Profiles</TabsTrigger>
          </TabsList>

          <TabsContent value="children" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Family Members</h2>
              <Button asChild>
                <Link to="/child/new">Add Child</Link>
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {children.map((child) => {
                const childConsent = consentOverview.find(c => c.child_id === child.id)
                const consentStatus = childConsent ? getConsentStatus(childConsent.consents) : { total: 0, given: 0 }
                
                return (
                  <Card key={child.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{child.name}</CardTitle>
                        <Badge variant={child.profile_active ? "default" : "secondary"}>
                          {child.profile_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      <CardDescription>Age {child.age}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between text-sm">
                        <span>Consent Status:</span>
                        <span className="font-medium">
                          {consentStatus.given}/{consentStatus.total} given
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-2 text-sm">
                        {child.biometric_enabled ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-yellow-600" />
                        )}
                        <span>
                          Biometric: {child.biometric_enabled ? "Enabled" : "Disabled"}
                        </span>
                      </div>
                      
                      <div className="flex space-x-2">
                        <Button asChild size="sm" className="flex-1">
                          <Link to={`/child/${child.id}`}>View Profile</Link>
                        </Button>
                        <Button asChild variant="outline" size="sm" className="flex-1">
                          <Link to={`/consent?child=${child.id}`}>Manage Consent</Link>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          <TabsContent value="consent" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Consent Management</h2>
              <Button asChild>
                <Link to="/consent">Manage All Consent</Link>
              </Button>
            </div>
            
            <div className="space-y-4">
              {consentOverview.map((child) => (
                <Card key={child.child_id}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>{child.child_name} (Age {child.age})</span>
                      <Badge variant="outline">
                        {getConsentStatus(child.consents).given}/{getConsentStatus(child.consents).total} Consents
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {Object.entries(child.consents).map(([type, consent]: [string, any]) => (
                        <div key={type} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <p className="font-medium capitalize">{type.replace('_', ' ')}</p>
                            <p className="text-sm text-gray-600">
                              {consent.date ? new Date(consent.date).toLocaleDateString() : 'Not given'}
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
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="activity" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Recent Activity</h2>
              <Button asChild>
                <Link to="/activity">View All Activity</Link>
              </Button>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Today's Protection Summary</CardTitle>
                <CardDescription>Transparent monitoring with full disclosure</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">23</div>
                    <p className="text-sm text-gray-600">Content blocks with explanations</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600">45</div>
                    <p className="text-sm text-gray-600">Educational alternatives shown</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">12</div>
                    <p className="text-sm text-gray-600">Family discussions initiated</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="education" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Digital Citizenship Education</h2>
              <Button asChild>
                <Link to="/education">View Progress</Link>
              </Button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BookOpen className="h-5 w-5" />
                    <span>Learning Progress</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Internet Safety</span>
                        <span>80%</span>
                      </div>
                      <Progress value={80} />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Digital Citizenship</span>
                        <span>65%</span>
                      </div>
                      <Progress value={65} />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Privacy Awareness</span>
                        <span>90%</span>
                      </div>
                      <Progress value={90} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Clock className="h-5 w-5" />
                    <span>Recent Lessons</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Understanding Online Privacy</span>
                      <Badge variant="default">Completed</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Safe Social Media Use</span>
                      <Badge variant="secondary">In Progress</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Recognizing Online Scams</span>
                      <Badge variant="outline">Upcoming</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="mobile" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Mobile Profile Management</h2>
              <Button asChild>
                <Link to="/mobile-profiles">Manage Mobile Profiles</Link>
              </Button>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Mobile Safety Profiles</CardTitle>
                <CardDescription>Generate and manage mobile safety profiles for your children's devices</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{children.length}</div>
                    <p className="text-sm text-gray-600">Children ready for mobile profiles</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-green-600">iOS &amp; Android</div>
                    <p className="text-sm text-gray-600">Supported platforms</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">100%</div>
                    <p className="text-sm text-gray-600">DPDP Act 2023 compliant</p>
                  </div>
                </div>
                <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-blue-800 mb-2">Mobile Profile Features:</h4>
                  <ul className="text-sm space-y-1 text-blue-700">
                    <li>✅ Transparent content filtering with educational explanations</li>
                    <li>✅ Age-appropriate consent mechanisms</li>
                    <li>✅ VPN detection and blocking</li>
                    <li>✅ Educational content promotion</li>
                    <li>✅ Complete transparency and compliance</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
