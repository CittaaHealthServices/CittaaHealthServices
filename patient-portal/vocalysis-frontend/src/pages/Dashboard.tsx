import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  Calendar, 
  MessageCircle, 
  Activity, 
  Users, 
  Clock, 
  TrendingUp,
  Heart,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import { Link } from 'react-router-dom'
import axios from 'axios'

interface DashboardStats {
  upcomingAppointments: number
  unreadMessages: number
  recentAnalyses: number
  totalReports: number
}

interface RecentActivity {
  id: string
  type: 'appointment' | 'message' | 'analysis'
  title: string
  description: string
  timestamp: string
  status?: string
}

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats>({
    upcomingAppointments: 0,
    unreadMessages: 0,
    recentAnalyses: 0,
    totalReports: 0
  })
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [appointmentsRes, messagesRes, reportsRes] = await Promise.all([
        axios.get('/api/v1/appointments'),
        axios.get('/api/v1/messages'),
        axios.get('/api/v1/voice-analysis/reports')
      ])

      const appointments = appointmentsRes.data
      const messages = messagesRes.data
      const reports = reportsRes.data

      const now = new Date()
      const upcomingAppointments = appointments.filter((apt: any) => 
        new Date(apt.appointment_date) > now && apt.status === 'scheduled'
      ).length

      const unreadMessages = messages.filter((msg: any) => 
        !msg.is_read && msg.receiver_id === user?.id
      ).length

      const recentAnalyses = reports.filter((report: any) => {
        const reportDate = new Date(report.created_at)
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        return reportDate > weekAgo
      }).length

      setStats({
        upcomingAppointments,
        unreadMessages,
        recentAnalyses,
        totalReports: reports.length
      })

      const activities: RecentActivity[] = [
        ...appointments.slice(0, 3).map((apt: any) => ({
          id: apt.id,
          type: 'appointment' as const,
          title: 'Upcoming Appointment',
          description: `Scheduled for ${new Date(apt.appointment_date).toLocaleDateString()}`,
          timestamp: apt.created_at,
          status: apt.status
        })),
        ...messages.slice(0, 2).map((msg: any) => ({
          id: msg.id,
          type: 'message' as const,
          title: 'New Message',
          description: msg.content.substring(0, 50) + '...',
          timestamp: msg.created_at
        })),
        ...reports.slice(0, 2).map((report: any) => ({
          id: report.id,
          type: 'analysis' as const,
          title: 'Voice Analysis Complete',
          description: `Mental Health Score: ${report.mental_health_score}/100`,
          timestamp: report.created_at
        }))
      ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

      setRecentActivity(activities.slice(0, 5))
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'appointment':
        return <Calendar className="w-5 h-5 text-blue-600" />
      case 'message':
        return <MessageCircle className="w-5 h-5 text-green-600" />
      case 'analysis':
        return <Activity className="w-5 h-5 text-purple-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'scheduled':
        return 'text-blue-600 bg-blue-50'
      case 'confirmed':
        return 'text-green-600 bg-green-50'
      case 'cancelled':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold mb-2">
              {getGreeting()}, {user?.full_name}!
            </h1>
            <p className="text-blue-100">
              Welcome to your mental wellness dashboard
            </p>
          </div>
          <div className="hidden md:block">
            <Heart className="w-16 h-16 text-white opacity-20" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Upcoming Appointments</p>
              <p className="text-3xl font-bold text-gray-900">{stats.upcomingAppointments}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4">
            <Link 
              to="/appointments" 
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View all appointments →
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Unread Messages</p>
              <p className="text-3xl font-bold text-gray-900">{stats.unreadMessages}</p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <MessageCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4">
            <Link 
              to="/messages" 
              className="text-sm text-green-600 hover:text-green-700 font-medium"
            >
              Check messages →
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recent Analyses</p>
              <p className="text-3xl font-bold text-gray-900">{stats.recentAnalyses}</p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <Activity className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4">
            <Link 
              to="/voice-analysis" 
              className="text-sm text-purple-600 hover:text-purple-700 font-medium"
            >
              Start analysis →
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Reports</p>
              <p className="text-3xl font-bold text-gray-900">{stats.totalReports}</p>
            </div>
            <div className="p-3 bg-orange-50 rounded-lg">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-sm text-gray-500">
              All time reports
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {activity.title}
                    </p>
                    <p className="text-sm text-gray-500">
                      {activity.description}
                    </p>
                    <div className="flex items-center mt-1 space-x-2">
                      <p className="text-xs text-gray-400">
                        {new Date(activity.timestamp).toLocaleDateString()}
                      </p>
                      {activity.status && (
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                          {activity.status}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No recent activity</p>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <Link
              to="/appointments"
              className="flex flex-col items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors duration-200"
            >
              <Calendar className="w-8 h-8 text-blue-600 mb-2" />
              <span className="text-sm font-medium text-blue-900">Book Appointment</span>
            </Link>
            
            <Link
              to="/voice-analysis"
              className="flex flex-col items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors duration-200"
            >
              <Activity className="w-8 h-8 text-purple-600 mb-2" />
              <span className="text-sm font-medium text-purple-900">Voice Analysis</span>
            </Link>
            
            <Link
              to="/messages"
              className="flex flex-col items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors duration-200"
            >
              <MessageCircle className="w-8 h-8 text-green-600 mb-2" />
              <span className="text-sm font-medium text-green-900">Messages</span>
            </Link>
            
            <Link
              to="/doctors"
              className="flex flex-col items-center p-4 bg-orange-50 rounded-lg hover:bg-orange-100 transition-colors duration-200"
            >
              <Users className="w-8 h-8 text-orange-600 mb-2" />
              <span className="text-sm font-medium text-orange-900">Find Doctors</span>
            </Link>
          </div>
        </div>
      </div>

      {user?.role === 'patient' && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 border border-green-200">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Your Mental Wellness Journey
              </h3>
              <p className="text-gray-600 mb-4">
                Regular voice analysis helps track your mental health progress. Consider scheduling your next session.
              </p>
              <Link
                to="/voice-analysis"
                className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors duration-200"
              >
                Start Voice Analysis
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
