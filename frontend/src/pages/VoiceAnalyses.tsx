import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { adminService } from '../services/api'
import { 
  ArrowLeft, BarChart3, Search, Filter, Activity, AlertTriangle,
  RefreshCw, Calendar, User, TrendingUp, TrendingDown
} from 'lucide-react'

interface VoiceAnalysis {
  id: string
  user_id: string
  user_email: string
  mental_health_score: number
  confidence_score: number
  overall_risk_level: string
  phq9_score: number | null
  gad7_score: number | null
  pss_score: number | null
  wemwbs_score: number | null
  predicted_at: string
  processing_time: number | null
}

export default function VoiceAnalyses() {
  const [analyses, setAnalyses] = useState<VoiceAnalysis[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [totalAnalyses, setTotalAnalyses] = useState(0)
  const [riskFilter, setRiskFilter] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadAnalyses()
  }, [riskFilter])

  const loadAnalyses = async () => {
    try {
      setLoading(true)
      const data = await adminService.getVoiceAnalyses({
        risk_level: riskFilter || undefined,
        limit: 100
      })
      setAnalyses(data.analyses || [])
      setTotalAnalyses(data.total || 0)
    } catch (err) {
      setError('Failed to load voice analyses')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'low': return 'bg-green-100 text-green-700'
      case 'moderate': return 'bg-yellow-100 text-yellow-700'
      case 'high': return 'bg-orange-100 text-orange-700'
      case 'severe': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  const getScoreColor = (score: number | null, max: number) => {
    if (score === null) return 'text-gray-400'
    const percentage = score / max
    if (percentage < 0.3) return 'text-green-600'
    if (percentage < 0.6) return 'text-yellow-600'
    if (percentage < 0.8) return 'text-orange-600'
    return 'text-red-600'
  }

  const filteredAnalyses = analyses.filter(analysis => {
    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      return analysis.user_email?.toLowerCase().includes(search)
    }
    return true
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading voice analyses...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link 
            to="/admin/dashboard" 
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Voice Analyses</h1>
            <p className="text-sm text-gray-500">Monitor all voice analysis results</p>
          </div>
        </div>
        <button
          onClick={loadAnalyses}
          className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-primary-500" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">{totalAnalyses}</p>
              <p className="text-sm text-gray-500">Total Analyses</p>
            </div>
          </div>
        </div>
        <div className="bg-green-50 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingDown className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">
                {analyses.filter(a => a.overall_risk_level?.toLowerCase() === 'low').length}
              </p>
              <p className="text-sm text-gray-500">Low Risk</p>
            </div>
          </div>
        </div>
        <div className="bg-yellow-50 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-yellow-500" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">
                {analyses.filter(a => a.overall_risk_level?.toLowerCase() === 'moderate').length}
              </p>
              <p className="text-sm text-gray-500">Moderate Risk</p>
            </div>
          </div>
        </div>
        <div className="bg-red-50 rounded-xl p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">
                {analyses.filter(a => ['high', 'severe'].includes(a.overall_risk_level?.toLowerCase())).length}
              </p>
              <p className="text-sm text-gray-500">High/Severe Risk</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Risk Levels</option>
              <option value="low">Low</option>
              <option value="moderate">Moderate</option>
              <option value="high">High</option>
              <option value="severe">Severe</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 rounded-xl p-4 border border-red-200 flex items-center space-x-2 text-red-600">
          <AlertTriangle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Analyses Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PHQ-9
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  GAD-7
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PSS
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  WEMWBS
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredAnalyses.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500">
                    <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>No voice analyses found</p>
                    <p className="text-sm mt-1">Analyses will appear here after patients record voice samples</p>
                  </td>
                </tr>
              ) : (
                filteredAnalyses.map((analysis) => (
                  <tr key={analysis.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(analysis.predicted_at).toLocaleDateString()}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <User className="w-4 h-4 text-gray-400" />
                        <span className="text-sm font-medium text-gray-900">{analysis.user_email}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded capitalize ${getRiskColor(analysis.overall_risk_level)}`}>
                        {analysis.overall_risk_level || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getScoreColor(analysis.phq9_score, 27)}`}>
                        {analysis.phq9_score !== null ? analysis.phq9_score : '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getScoreColor(analysis.gad7_score, 21)}`}>
                        {analysis.gad7_score !== null ? analysis.gad7_score : '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getScoreColor(analysis.pss_score, 40)}`}>
                        {analysis.pss_score !== null ? analysis.pss_score : '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${analysis.wemwbs_score ? 'text-green-600' : 'text-gray-400'}`}>
                        {analysis.wemwbs_score !== null ? analysis.wemwbs_score : '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-500 h-2 rounded-full" 
                            style={{ width: `${(analysis.confidence_score || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-500">
                          {((analysis.confidence_score || 0) * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
