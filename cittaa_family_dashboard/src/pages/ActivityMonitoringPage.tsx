import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  ArrowLeft, 
  Activity, 
  Shield, 
  CheckCircle, 
  Eye,
  Search,
  Download,
  Clock,
  Globe,
  Smartphone
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useFamily } from '@/contexts/FamilyContext'
import { familyApi } from '@/lib/api'

export default function ActivityMonitoringPage() {
  const { token } = useAuth()
  const { children } = useFamily()
  const [activities, setActivities] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedChild, setSelectedChild] = useState('all')
  const [activityFilter, setActivityFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadActivities()
  }, [])

  const loadActivities = async () => {
    if (!token) return

    setLoading(true)
    try {
      const allActivities = []
      for (const child of children) {
        const childActivities = await familyApi.getChildActivity(token, child.id) as any[]
        const activitiesWithChild = childActivities.map((activity: any) => ({
          ...activity,
          child_name: child.name,
          child_id: child.id
        }))
        allActivities.push(...activitiesWithChild)
      }
      
      allActivities.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      setActivities(allActivities)
    } catch (error) {
      console.error('Failed to load activities:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredActivities = activities.filter((activity: any) => {
    const matchesChild = selectedChild === 'all' || activity.child_id.toString() === selectedChild
    const matchesFilter = activityFilter === 'all' || 
      (activityFilter === 'blocked' && activity.blocked) ||
      (activityFilter === 'allowed' && !activity.blocked) ||
      (activityFilter === 'educational' && activity.educational_alternative_shown)
    const matchesSearch = searchTerm === '' || 
      activity.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (activity.url && activity.url.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (activity.app_name && activity.app_name.toLowerCase().includes(searchTerm.toLowerCase()))
    
    return matchesChild && matchesFilter && matchesSearch
  })

  const stats = {
    total: activities.length,
    blocked: activities.filter((a: any) => a.blocked).length,
    allowed: activities.filter((a: any) => !a.blocked).length,
    educational: activities.filter((a: any) => a.educational_alternative_shown).length
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
              <h1 className="text-xl font-bold text-gray-900">Activity Monitoring</h1>
              <p className="text-sm text-gray-600">Transparent monitoring with full disclosure</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Activities</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
              <p className="text-xs text-muted-foreground">
                All logged activities
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Content Blocked</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.blocked}</div>
              <p className="text-xs text-muted-foreground">
                With educational explanations
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Content Allowed</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.allowed}</div>
              <p className="text-xs text-muted-foreground">
                Age-appropriate content
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Educational Shown</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.educational}</div>
              <p className="text-xs text-muted-foreground">
                Alternative content provided
              </p>
            </CardContent>
          </Card>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Activity Filters</CardTitle>
            <CardDescription>
              Filter and search through transparent activity logs
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Child</label>
                <Select value={selectedChild} onValueChange={setSelectedChild}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select child" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Children</SelectItem>
                    {children.map(child => (
                      <SelectItem key={child.id} value={child.id.toString()}>
                        {child.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Activity Type</label>
                <Select value={activityFilter} onValueChange={setActivityFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Filter activities" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Activities</SelectItem>
                    <SelectItem value="blocked">Blocked Content</SelectItem>
                    <SelectItem value="allowed">Allowed Content</SelectItem>
                    <SelectItem value="educational">Educational Alternatives</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search activities..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Actions</label>
                <Button variant="outline" className="w-full">
                  <Download className="h-4 w-4 mr-2" />
                  Export Report
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="timeline" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="timeline">Activity Timeline</TabsTrigger>
            <TabsTrigger value="summary">Daily Summary</TabsTrigger>
            <TabsTrigger value="transparency">Transparency Report</TabsTrigger>
          </TabsList>

          <TabsContent value="timeline" className="space-y-4">
            {loading ? (
              <Card>
                <CardContent className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <Activity className="h-12 w-12 text-gray-400 mx-auto animate-pulse" />
                    <p className="mt-4 text-gray-600">Loading activities...</p>
                  </div>
                </CardContent>
              </Card>
            ) : filteredActivities.length > 0 ? (
              <div className="space-y-3">
                {filteredActivities.map((activity, index) => (
                  <Card key={`${activity.id}-${index}`}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="flex-shrink-0">
                            {activity.blocked ? (
                              <div className="p-2 bg-red-100 rounded-full">
                                <Shield className="h-5 w-5 text-red-600" />
                              </div>
                            ) : (
                              <div className="p-2 bg-green-100 rounded-full">
                                <CheckCircle className="h-5 w-5 text-green-600" />
                              </div>
                            )}
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <h3 className="font-medium">{activity.description}</h3>
                              <Badge variant="outline">{activity.child_name}</Badge>
                            </div>
                            
                            <div className="text-sm text-gray-600 space-y-1">
                              {activity.url && (
                                <div className="flex items-center space-x-2">
                                  <Globe className="h-3 w-3" />
                                  <span>{activity.url}</span>
                                </div>
                              )}
                              {activity.app_name && (
                                <div className="flex items-center space-x-2">
                                  <Smartphone className="h-3 w-3" />
                                  <span>{activity.app_name}</span>
                                </div>
                              )}
                              <div className="flex items-center space-x-2">
                                <Clock className="h-3 w-3" />
                                <span>{new Date(activity.timestamp).toLocaleString()}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex flex-col items-end space-y-2">
                          <Badge variant={activity.blocked ? "destructive" : "default"}>
                            {activity.blocked ? "Blocked" : "Allowed"}
                          </Badge>
                          
                          {activity.educational_alternative_shown && (
                            <Badge variant="secondary" className="text-xs">
                              Educational Alternative Shown
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="flex items-center justify-center h-64">
                  <div className="text-center">
                    <Activity className="h-12 w-12 text-gray-400 mx-auto" />
                    <h3 className="text-lg font-medium text-gray-900 mt-4">No Activities Found</h3>
                    <p className="text-gray-600 mt-2">
                      {searchTerm || activityFilter !== 'all' 
                        ? 'Try adjusting your filters or search terms'
                        : 'No activities have been logged yet'
                      }
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="summary" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Daily Activity Summary</CardTitle>
                <CardDescription>
                  Transparent overview of today's protection activities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center p-6 border rounded-lg">
                    <Shield className="h-8 w-8 text-red-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-red-600">{stats.blocked}</div>
                    <p className="text-sm text-gray-600">Content Blocks</p>
                    <p className="text-xs text-gray-500 mt-1">
                      All blocks included educational explanations
                    </p>
                  </div>
                  
                  <div className="text-center p-6 border rounded-lg">
                    <Eye className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-blue-600">{stats.educational}</div>
                    <p className="text-sm text-gray-600">Educational Alternatives</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Safe learning content provided
                    </p>
                  </div>
                  
                  <div className="text-center p-6 border rounded-lg">
                    <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-green-600">{stats.allowed}</div>
                    <p className="text-sm text-gray-600">Content Allowed</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Age-appropriate and safe
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="transparency" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Transparency Report</CardTitle>
                <CardDescription>
                  How we ensure transparent monitoring and child awareness
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="font-semibold text-lg">Child Awareness</h3>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm">All children understand monitoring is active</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm">Age-appropriate explanations provided</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm">Clear consent obtained for all features</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm">Educational alternatives always shown</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="font-semibold text-lg">Compliance Status</h3>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm">DPDP Act 2023 compliant</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm">Children's privacy rights respected</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm">Data minimization principles followed</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm">Audit trail maintained</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
