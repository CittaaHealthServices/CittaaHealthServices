import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { predictionsService, Prediction } from '../services/api'
import { 
  Activity, AlertTriangle, CheckCircle, ArrowLeft, Download,
  Brain, Heart, Zap, Info
} from 'lucide-react'
import { 
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell
} from 'recharts'

export default function AnalysisResults() {
  const { predictionId } = useParams<{ predictionId: string }>()
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (predictionId) {
      loadPrediction()
    }
  }, [predictionId])

  const loadPrediction = async () => {
    try {
      setLoading(true)
      const data = await predictionsService.getPredictionDetails(predictionId!)
      setPrediction(data)
    } catch (err) {
      setError('Failed to load analysis results')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading results...</p>
        </div>
      </div>
    )
  }

  if (error || !prediction) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-error mx-auto mb-4" />
          <p className="text-gray-600">{error || 'Results not found'}</p>
          <Link to="/dashboard" className="text-primary-500 hover:underline mt-2 inline-block">
            Return to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  // Prepare chart data
  const classificationData = [
    { name: 'Normal', value: (prediction.normal_score || 0) * 100, color: '#27AE60' },
    { name: 'Anxiety', value: (prediction.anxiety_score || 0) * 100, color: '#FF8C42' },
    { name: 'Depression', value: (prediction.depression_score || 0) * 100, color: '#8B5A96' },
    { name: 'Stress', value: (prediction.stress_score || 0) * 100, color: '#7BB3A8' },
  ]

  const radarData = prediction.voice_features ? [
    { feature: 'Pitch', value: Math.min(100, (prediction.voice_features.pitch_mean || 0) / 3) },
    { feature: 'Energy', value: Math.min(100, (prediction.voice_features.rms_mean || 0) * 500) },
    { feature: 'Speech Rate', value: Math.min(100, (prediction.voice_features.speech_rate || 0) * 20) },
    { feature: 'Jitter', value: Math.min(100, (prediction.voice_features.jitter_mean || 0) * 2000) },
    { feature: 'HNR', value: Math.min(100, (prediction.voice_features.hnr || 0) * 5) },
    { feature: 'Spectral', value: Math.min(100, (prediction.voice_features.spectral_centroid_mean || 0) / 50) },
  ] : []

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link 
            to="/dashboard" 
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Analysis Results</h1>
            <p className="text-sm text-gray-500">
              {new Date(prediction.predicted_at).toLocaleString()}
            </p>
          </div>
        </div>
        <button className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
          <Download className="w-4 h-4 mr-2" />
          Download Report
        </button>
      </div>

      {/* Overall Score Card */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-400 rounded-2xl p-6 text-white">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center md:text-left">
            <p className="text-white/80 text-sm">Mental Health Score</p>
            <div className="text-5xl font-bold mt-2">
              {prediction.mental_health_score?.toFixed(0) || 'N/A'}
              <span className="text-2xl text-white/60">/100</span>
            </div>
          </div>
          
          <div className="text-center">
            <p className="text-white/80 text-sm">Risk Level</p>
            <div className={`inline-flex items-center mt-2 px-4 py-2 rounded-full text-lg font-semibold capitalize ${
              prediction.overall_risk_level === 'low' ? 'bg-white/20' :
              prediction.overall_risk_level === 'moderate' ? 'bg-warning/30' :
              'bg-error/30'
            }`}>
              {prediction.overall_risk_level === 'low' && <CheckCircle className="w-5 h-5 mr-2" />}
              {prediction.overall_risk_level === 'moderate' && <AlertTriangle className="w-5 h-5 mr-2" />}
              {prediction.overall_risk_level === 'high' && <AlertTriangle className="w-5 h-5 mr-2" />}
              {prediction.overall_risk_level || 'Unknown'}
            </div>
          </div>
          
          <div className="text-center md:text-right">
            <p className="text-white/80 text-sm">Confidence</p>
            <div className="text-3xl font-bold mt-2">
              {((prediction.confidence || 0) * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Classification Probabilities */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-primary-500" />
            Mental State Classification
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={classificationData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={80} />
              <Tooltip 
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Probability']}
                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {classificationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Voice Features Radar */}
        {radarData.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-secondary-500" />
              Voice Feature Analysis
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="feature" tick={{ fontSize: 11 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Radar
                  name="Voice Features"
                  dataKey="value"
                  stroke="#8B5A96"
                  fill="#8B5A96"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Clinical Scale Mappings */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <Heart className="w-5 h-5 mr-2 text-accent-500" />
          Clinical Scale Mappings
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* PHQ-9 */}
          <div className="p-4 bg-primary-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">PHQ-9</span>
              <span className="text-xs text-gray-500">Depression</span>
            </div>
            <div className="text-2xl font-bold text-primary-600">
              {prediction.phq9_score?.toFixed(0) || 0}
              <span className="text-sm text-gray-400">/27</span>
            </div>
            <div className="mt-2 w-full bg-primary-100 rounded-full h-2">
              <div 
                className="bg-primary-500 h-2 rounded-full"
                style={{ width: `${((prediction.phq9_score || 0) / 27) * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-600 mt-2">{prediction.phq9_severity || 'N/A'}</p>
          </div>

          {/* GAD-7 */}
          <div className="p-4 bg-accent-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">GAD-7</span>
              <span className="text-xs text-gray-500">Anxiety</span>
            </div>
            <div className="text-2xl font-bold text-accent-600">
              {prediction.gad7_score?.toFixed(0) || 0}
              <span className="text-sm text-gray-400">/21</span>
            </div>
            <div className="mt-2 w-full bg-accent-100 rounded-full h-2">
              <div 
                className="bg-accent-500 h-2 rounded-full"
                style={{ width: `${((prediction.gad7_score || 0) / 21) * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-600 mt-2">{prediction.gad7_severity || 'N/A'}</p>
          </div>

          {/* PSS */}
          <div className="p-4 bg-secondary-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">PSS</span>
              <span className="text-xs text-gray-500">Stress</span>
            </div>
            <div className="text-2xl font-bold text-secondary-600">
              {prediction.pss_score?.toFixed(0) || 0}
              <span className="text-sm text-gray-400">/40</span>
            </div>
            <div className="mt-2 w-full bg-secondary-100 rounded-full h-2">
              <div 
                className="bg-secondary-500 h-2 rounded-full"
                style={{ width: `${((prediction.pss_score || 0) / 40) * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-600 mt-2">{prediction.pss_severity || 'N/A'}</p>
          </div>

          {/* WEMWBS */}
          <div className="p-4 bg-success/10 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-gray-700">WEMWBS</span>
              <span className="text-xs text-gray-500">Wellbeing</span>
            </div>
            <div className="text-2xl font-bold text-success">
              {prediction.wemwbs_score?.toFixed(0) || 0}
              <span className="text-sm text-gray-400">/70</span>
            </div>
            <div className="mt-2 w-full bg-success/20 rounded-full h-2">
              <div 
                className="bg-success h-2 rounded-full"
                style={{ width: `${((prediction.wemwbs_score || 0) / 70) * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-600 mt-2">{prediction.wemwbs_severity || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Interpretations & Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Interpretations */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Info className="w-5 h-5 mr-2 text-primary-500" />
            Clinical Interpretations
          </h3>
          <div className="space-y-3">
            {prediction.interpretations && prediction.interpretations.length > 0 ? (
              prediction.interpretations.map((interpretation, index) => (
                <div key={index} className="flex items-start p-3 bg-gray-50 rounded-lg">
                  <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                    <span className="text-xs font-medium text-primary-600">{index + 1}</span>
                  </div>
                  <p className="text-sm text-gray-700">{interpretation}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No interpretations available</p>
            )}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-accent-500" />
            Recommendations
          </h3>
          <div className="space-y-3">
            {prediction.recommendations && prediction.recommendations.length > 0 ? (
              prediction.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start p-3 bg-accent-50 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-accent-500 mr-3 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-gray-700">{recommendation}</p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-sm">No recommendations available</p>
            )}
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          <strong>Disclaimer:</strong> This analysis is for screening purposes only and does not constitute a medical diagnosis. 
          Please consult a qualified mental health professional for clinical assessment and treatment.
        </p>
      </div>
    </div>
  )
}
