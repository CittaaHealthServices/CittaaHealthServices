import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { dashboardService, DashboardData } from '../services/api'
import { 
  Mic, TrendingUp, TrendingDown, Minus, Activity, Calendar, 
  AlertTriangle, CheckCircle, Clock, ArrowRight, Heart
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function PatientDashboard() {
  const { user } = useAuth()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [, setError] = useState('')

  useEffect(() => {
    if (user?.id) {
      loadDashboard()
    }
  }, [user?.id])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const data = await dashboardService.getUserDashboard(user!.id)
      setDashboardData(data)
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'low':
        return <CheckCircle className="w-6 h-6 text-success" />
      case 'moderate':
        return <AlertTriangle className="w-6 h-6 text-warning" />
      case 'high':
        return <AlertTriangle className="w-6 h-6 text-error" />
      default:
        return <Activity className="w-6 h-6 text-gray-400" />
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingDown className="w-5 h-5 text-success" />
      case 'worsening':
        return <TrendingUp className="w-5 h-5 text-error" />
      default:
        return <Minus className="w-5 h-5 text-gray-400" />
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'bg-success/10 text-success border-success/20'
      case 'moderate':
        return 'bg-warning/10 text-warning border-warning/20'
      case 'high':
        return 'bg-error/10 text-error border-error/20'
      default:
        return 'bg-gray-100 text-gray-500 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl p-6 text-white shadow-lg animate-fade-in">
        <h1 className="text-2xl font-bold">
          Welcome back, {user?.full_name?.split(' ')[0] || 'there'}!
        </h1>
        <p className="mt-1 text-white/80">
          Track your mental wellness journey with voice analysis
        </p>
        <p className="text-sm text-white/60 italic mt-2">Healing is a journey. We will walk beside you.</p>
        <Link
          to="/record"
          className="inline-flex items-center mt-4 px-6 py-3 bg-white text-primary-800 rounded-lg font-medium hover:bg-white/90 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
        >
          <Mic className="w-5 h-5 mr-2" />
          Start Voice Recording
          <ArrowRight className="w-4 h-4 ml-2" />
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Current Risk Level */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Current Risk Level</span>
            {getRiskIcon(dashboardData?.current_risk_level || 'unknown')}
          </div>
          <div className={`mt-3 inline-flex px-3 py-1 rounded-full text-sm font-medium capitalize border ${getRiskColor(dashboardData?.current_risk_level || 'unknown')}`}>
            {dashboardData?.current_risk_level || 'Unknown'}
          </div>
        </div>

        {/* Risk Trend */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Weekly Trend</span>
            {getTrendIcon(dashboardData?.risk_trend || 'stable')}
          </div>
          <p className="mt-3 text-lg font-semibold text-gray-800 capitalize">
            {dashboardData?.risk_trend === 'improving' ? 'Improving' :
             dashboardData?.risk_trend === 'worsening' ? 'Needs Attention' :
             dashboardData?.risk_trend === 'stable' ? 'Stable' : 'Insufficient Data'}
          </p>
        </div>

        {/* Compliance Rate */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Compliance Rate</span>
            <Calendar className="w-5 h-5 text-primary-400" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-800">
            {dashboardData?.compliance_rate?.toFixed(0) || 0}%
          </p>
          <div className="mt-2 w-full bg-gray-100 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-primary-500 to-secondary-400 h-2 rounded-full transition-all duration-500"
              style={{ width: `${dashboardData?.compliance_rate || 0}%` }}
            />
          </div>
        </div>

        {/* Total Recordings */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Total Recordings</span>
            <Mic className="w-5 h-5 text-secondary-400" />
          </div>
          <p className="mt-3 text-2xl font-bold text-gray-800">
            {dashboardData?.total_recordings || 0}
          </p>
          <p className="text-xs text-gray-400 mt-1">Voice samples analyzed</p>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Trend Chart */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Weekly Mental Health Trends</h3>
          {dashboardData?.weekly_trend_data && dashboardData.weekly_trend_data.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={dashboardData.weekly_trend_data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { weekday: 'short' })}
                />
                <YAxis tick={{ fontSize: 12 }} domain={[0, 1]} />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="depression" 
                  stroke="#8B5A96" 
                  strokeWidth={2}
                  dot={{ fill: '#8B5A96', strokeWidth: 2 }}
                  name="Depression"
                />
                <Line 
                  type="monotone" 
                  dataKey="anxiety" 
                  stroke="#FF8C42" 
                  strokeWidth={2}
                  dot={{ fill: '#FF8C42', strokeWidth: 2 }}
                  name="Anxiety"
                />
                <Line 
                  type="monotone" 
                  dataKey="stress" 
                  stroke="#7BB3A8" 
                  strokeWidth={2}
                  dot={{ fill: '#7BB3A8', strokeWidth: 2 }}
                  name="Stress"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-gray-400">
              <div className="text-center">
                <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No trend data available yet</p>
                <p className="text-sm">Start recording to see your trends</p>
              </div>
            </div>
          )}
        </div>

        {/* Recent Predictions */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Analyses</h3>
          {dashboardData?.recent_predictions && dashboardData.recent_predictions.length > 0 ? (
            <div className="space-y-3">
              {dashboardData.recent_predictions.slice(0, 4).map((prediction) => (
                <Link
                  key={prediction.id}
                  to={`/results/${prediction.id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors border border-gray-100"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getRiskColor(prediction.overall_risk_level || 'unknown')}`}>
                      <Heart className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">
                        Score: {prediction.mental_health_score?.toFixed(0) || 'N/A'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(prediction.predicted_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-medium capitalize ${getRiskColor(prediction.overall_risk_level || 'unknown')}`}>
                    {prediction.overall_risk_level || 'Unknown'}
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-gray-400">
              <div className="text-center">
                <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No analyses yet</p>
                <Link to="/record" className="text-primary-500 hover:underline text-sm">
                  Record your first sample
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/record"
            className="flex items-center p-4 rounded-lg border-2 border-dashed border-primary-200 hover:border-primary-400 hover:bg-primary-50 transition-all duration-200"
          >
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mr-4">
              <Mic className="w-6 h-6 text-primary-500" />
            </div>
            <div>
              <p className="font-medium text-gray-800">New Recording</p>
              <p className="text-sm text-gray-500">Record voice sample</p>
            </div>
          </Link>

          <Link
            to="/reports"
            className="flex items-center p-4 rounded-lg border-2 border-dashed border-secondary-200 hover:border-secondary-400 hover:bg-secondary-50 transition-all duration-200"
          >
            <div className="w-12 h-12 bg-secondary-100 rounded-lg flex items-center justify-center mr-4">
              <Activity className="w-6 h-6 text-secondary-500" />
            </div>
            <div>
              <p className="font-medium text-gray-800">View Reports</p>
              <p className="text-sm text-gray-500">Clinical assessments</p>
            </div>
          </Link>

          <div className="flex items-center p-4 rounded-lg border-2 border-dashed border-accent-200 hover:border-accent-400 hover:bg-accent-50 transition-all duration-200 cursor-pointer">
            <div className="w-12 h-12 bg-accent-100 rounded-lg flex items-center justify-center mr-4">
              <Calendar className="w-6 h-6 text-accent-500" />
            </div>
            <div>
              <p className="font-medium text-gray-800">Schedule Session</p>
              <p className="text-sm text-gray-500">Book with psychologist</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
