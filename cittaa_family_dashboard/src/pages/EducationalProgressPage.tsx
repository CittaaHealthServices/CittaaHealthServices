import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  ArrowLeft, 
  BookOpen, 
  Award, 
  Clock,
  CheckCircle,
  PlayCircle,
  Star,
  Target,
  TrendingUp
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useFamily } from '@/contexts/FamilyContext'
import { familyApi } from '@/lib/api'

export default function EducationalProgressPage() {
  const { token } = useAuth()
  const { children } = useFamily()
  const [progressData, setProgressData] = useState<any>({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadEducationalProgress()
  }, [])

  const loadEducationalProgress = async () => {
    if (!token) return

    setLoading(true)
    try {
      const allProgress: any = {}
      for (const child of children) {
        const progress = await familyApi.getEducationalProgress(token, child.id)
        allProgress[child.id] = progress
      }
      setProgressData(allProgress)
    } catch (error) {
      console.error('Failed to load educational progress:', error)
    } finally {
      setLoading(false)
    }
  }

  const getOverallProgress = (childId: number) => {
    const progress = progressData[childId] || []
    if (progress.length === 0) return 0
    
    const completed = progress.filter((p: any) => p.completed).length
    return Math.round((completed / progress.length) * 100)
  }

  const getAverageScore = (childId: number) => {
    const progress = progressData[childId] || []
    const completedWithScores = progress.filter((p: any) => p.completed && p.score !== null)
    
    if (completedWithScores.length === 0) return 0
    
    const totalScore = completedWithScores.reduce((sum: number, p: any) => sum + p.score, 0)
    return Math.round(totalScore / completedWithScores.length)
  }

  const getTotalTimeSpent = (childId: number) => {
    const progress = progressData[childId] || []
    return progress.reduce((total: number, p: any) => total + p.time_spent, 0)
  }

  const lessonCategories = [
    {
      id: 'internet_safety',
      name: 'Internet Safety',
      icon: BookOpen,
      color: 'blue',
      lessons: [
        'Understanding Online Privacy',
        'Safe Browsing Habits',
        'Recognizing Phishing Attempts',
        'Password Security Basics'
      ]
    },
    {
      id: 'digital_citizenship',
      name: 'Digital Citizenship',
      icon: Award,
      color: 'green',
      lessons: [
        'Respectful Online Communication',
        'Digital Footprint Awareness',
        'Copyright and Fair Use',
        'Online Ethics and Responsibility'
      ]
    },
    {
      id: 'privacy_awareness',
      name: 'Privacy Awareness',
      icon: Target,
      color: 'purple',
      lessons: [
        'Personal Information Protection',
        'Social Media Privacy Settings',
        'Data Sharing Consequences',
        'Identity Protection Online'
      ]
    }
  ]

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
              <h1 className="text-xl font-bold text-gray-900">Educational Progress</h1>
              <p className="text-sm text-gray-600">Digital citizenship learning journey</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Learners</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{children.length}</div>
              <p className="text-xs text-muted-foreground">
                Children in program
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Lessons Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Object.values(progressData).flat().filter((p: any) => p.completed).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Total completions
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Score</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {children.length > 0 
                  ? Math.round(children.reduce((sum, child) => sum + getAverageScore(child.id), 0) / children.length)
                  : 0
                }%
              </div>
              <p className="text-xs text-muted-foreground">
                Family average
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Learning Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Math.round(children.reduce((sum, child) => sum + getTotalTimeSpent(child.id), 0) / 60)}h
              </div>
              <p className="text-xs text-muted-foreground">
                Total time spent
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Family Overview</TabsTrigger>
            <TabsTrigger value="curriculum">Curriculum</TabsTrigger>
            <TabsTrigger value="achievements">Achievements</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {children.map((child) => {
                const progress = progressData[child.id] || []
                const overallProgress = getOverallProgress(child.id)
                const averageScore = getAverageScore(child.id)
                const timeSpent = getTotalTimeSpent(child.id)

                return (
                  <Card key={child.id}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>{child.name}'s Progress</span>
                        <Badge variant="outline">Age {child.age}</Badge>
                      </CardTitle>
                      <CardDescription>
                        Digital citizenship learning journey
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Overall Progress</span>
                          <span>{overallProgress}%</span>
                        </div>
                        <Progress value={overallProgress} />
                      </div>

                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <div className="text-lg font-bold text-blue-600">
                            {progress.filter((p: any) => p.completed).length}
                          </div>
                          <p className="text-xs text-gray-600">Completed</p>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-green-600">{averageScore}%</div>
                          <p className="text-xs text-gray-600">Avg Score</p>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-purple-600">
                            {Math.round(timeSpent / 60)}h
                          </div>
                          <p className="text-xs text-gray-600">Time Spent</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <h4 className="font-medium">Recent Lessons</h4>
                        {progress.slice(0, 3).map((lesson: any, index: number) => (
                          <div key={index} className="flex items-center justify-between text-sm">
                            <span>{lesson.lesson_title}</span>
                            <Badge variant={lesson.completed ? "default" : "secondary"}>
                              {lesson.completed ? "Completed" : "In Progress"}
                            </Badge>
                          </div>
                        ))}
                      </div>

                      <Button asChild className="w-full">
                        <Link to={`/child/${child.id}`}>View Detailed Progress</Link>
                      </Button>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          <TabsContent value="curriculum" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Digital Citizenship Curriculum</CardTitle>
                <CardDescription>
                  Age-appropriate lessons integrated with safety features
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {lessonCategories.map((category) => {
                    const Icon = category.icon
                    return (
                      <Card key={category.id}>
                        <CardHeader>
                          <CardTitle className="flex items-center space-x-2">
                            <Icon className={`h-5 w-5 text-${category.color}-600`} />
                            <span>{category.name}</span>
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-3">
                            {category.lessons.map((lesson, index) => (
                              <div key={index} className="flex items-center justify-between">
                                <span className="text-sm">{lesson}</span>
                                <Button variant="ghost" size="sm">
                                  <PlayCircle className="h-4 w-4" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="achievements" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Family Achievements</CardTitle>
                <CardDescription>
                  Celebrating digital citizenship milestones
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="text-center p-6 border rounded-lg">
                    <Award className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
                    <h3 className="font-semibold mb-2">Safety Champion</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Completed all internet safety lessons
                    </p>
                    <Badge variant="secondary">In Progress</Badge>
                  </div>

                  <div className="text-center p-6 border rounded-lg">
                    <Star className="h-12 w-12 text-blue-500 mx-auto mb-4" />
                    <h3 className="font-semibold mb-2">Digital Citizen</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Mastered online ethics and responsibility
                    </p>
                    <Badge variant="secondary">Locked</Badge>
                  </div>

                  <div className="text-center p-6 border rounded-lg">
                    <TrendingUp className="h-12 w-12 text-green-500 mx-auto mb-4" />
                    <h3 className="font-semibold mb-2">Privacy Pro</h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Expert in personal data protection
                    </p>
                    <Badge variant="secondary">Locked</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Learning Streaks</CardTitle>
                <CardDescription>
                  Consistent learning builds strong digital habits
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {children.map((child) => (
                    <div key={child.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="font-semibold text-blue-600">
                            {child.name.charAt(0)}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium">{child.name}</p>
                          <p className="text-sm text-gray-600">Current streak: 5 days</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-orange-600">🔥 5</div>
                        <p className="text-xs text-gray-600">days</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
