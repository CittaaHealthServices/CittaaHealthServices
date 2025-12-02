import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { predictionsService, Prediction } from '../services/api'
import { 
  FileText, Calendar,
  Download, Eye, Filter, Search, Activity, AlertTriangle
} from 'lucide-react'

export default function ClinicalReports() {
  const { user } = useAuth()
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (user?.id) {
      loadPredictions()
    }
  }, [user?.id])

  const loadPredictions = async () => {
    try {
      setLoading(true)
      const data = await predictionsService.getUserPredictions(user!.id, 50)
      setPredictions(data)
    } catch (err) {
      setError('Failed to load clinical reports')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-success/10 text-success border-success/20'
      case 'moderate': return 'bg-warning/10 text-warning border-warning/20'
      case 'high': return 'bg-error/10 text-error border-error/20'
      default: return 'bg-gray-100 text-gray-500 border-gray-200'
    }
  }

  const filteredPredictions = predictions.filter(p => {
    if (filter !== 'all' && p.overall_risk_level !== filter) return false
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading reports...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Clinical Reports</h1>
          <p className="text-gray-500">View your voice analysis history and clinical assessments</p>
        </div>
        <Link
          to="/record"
          className="inline-flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <Activity className="w-4 h-4 mr-2" />
          New Analysis
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search reports..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Risk Levels</option>
              <option value="low">Low Risk</option>
              <option value="moderate">Moderate Risk</option>
              <option value="high">High Risk</option>
            </select>
          </div>
        </div>
      </div>

      {/* Reports List */}
      {error ? (
        <div className="bg-red-50 rounded-xl p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-error mx-auto mb-4" />
          <p className="text-gray-600">{error}</p>
        </div>
      ) : filteredPredictions.length === 0 ? (
        <div className="bg-white rounded-xl p-12 text-center shadow-sm border border-gray-100">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-800 mb-2">No Reports Found</h3>
          <p className="text-gray-500 mb-4">
            {filter !== 'all' 
              ? 'No reports match the selected filter'
              : 'Start recording voice samples to generate clinical reports'}
          </p>
          <Link
            to="/record"
            className="inline-flex items-center px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            <Activity className="w-5 h-5 mr-2" />
            Record Voice Sample
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredPredictions.map((prediction) => (
            <div
              key={prediction.id}
              className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start space-x-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${getRiskColor(prediction.overall_risk_level || 'unknown')}`}>
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="font-semibold text-gray-800">
                        Mental Health Score: {prediction.mental_health_score?.toFixed(0) || 'N/A'}
                      </h3>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${getRiskColor(prediction.overall_risk_level || 'unknown')}`}>
                        {prediction.overall_risk_level || 'Unknown'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      <Calendar className="w-4 h-4 inline mr-1" />
                      {new Date(prediction.predicted_at).toLocaleString()}
                    </p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      <span className="text-xs bg-primary-50 text-primary-600 px-2 py-1 rounded">
                        PHQ-9: {prediction.phq9_score?.toFixed(0) || 'N/A'}
                      </span>
                      <span className="text-xs bg-accent-50 text-accent-600 px-2 py-1 rounded">
                        GAD-7: {prediction.gad7_score?.toFixed(0) || 'N/A'}
                      </span>
                      <span className="text-xs bg-secondary-50 text-secondary-600 px-2 py-1 rounded">
                        PSS: {prediction.pss_score?.toFixed(0) || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Link
                    to={`/results/${prediction.id}`}
                    className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    View Details
                  </Link>
                  <button className="p-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {predictions.length > 0 && (
        <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-6">
          <h3 className="font-semibold text-gray-800 mb-4">Summary Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">{predictions.length}</p>
              <p className="text-sm text-gray-600">Total Reports</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-success">
                {predictions.filter(p => p.overall_risk_level === 'low').length}
              </p>
              <p className="text-sm text-gray-600">Low Risk</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-warning">
                {predictions.filter(p => p.overall_risk_level === 'moderate').length}
              </p>
              <p className="text-sm text-gray-600">Moderate Risk</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-error">
                {predictions.filter(p => p.overall_risk_level === 'high').length}
              </p>
              <p className="text-sm text-gray-600">High Risk</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
