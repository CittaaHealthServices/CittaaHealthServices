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

      {/* Clinical Scale Mappings with Theory */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <Heart className="w-5 h-5 mr-2 text-accent-500" />
          Clinical Scale Mappings (Golden Standards)
        </h3>
        <p className="text-sm text-gray-500 mb-6">
          Voice biomarkers are mapped to validated clinical assessment scales used worldwide in mental health screening.
        </p>
        
        <div className="space-y-6">
          {/* PHQ-9 Section */}
          <div className="p-5 bg-primary-50 rounded-xl border border-primary-100">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-semibold text-gray-800 flex items-center">
                  PHQ-9 
                  <span className="ml-2 text-xs bg-primary-200 text-primary-700 px-2 py-0.5 rounded-full">Depression</span>
                </h4>
                <p className="text-xs text-gray-500 mt-1">Patient Health Questionnaire-9</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-primary-600">
                  {prediction.phq9_score?.toFixed(0) || 0}
                  <span className="text-lg text-gray-400">/27</span>
                </div>
                <p className="text-sm font-medium text-primary-700">{prediction.phq9_severity || 'N/A'}</p>
              </div>
            </div>
            <div className="w-full bg-primary-100 rounded-full h-3 mb-3">
              <div 
                className="bg-gradient-to-r from-primary-400 to-primary-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${((prediction.phq9_score || 0) / 27) * 100}%` }}
              />
            </div>
            <div className="bg-white/60 rounded-lg p-3 text-xs text-gray-600">
              <p className="font-medium text-gray-700 mb-1">Clinical Theory:</p>
              <p>The PHQ-9 is a validated 9-item self-report questionnaire measuring depression severity based on DSM-IV criteria. Voice analysis correlates with PHQ-9 through reduced pitch variability, slower speech rate, and decreased energy—biomarkers associated with depressive states. Scores: 0-4 (minimal), 5-9 (mild), 10-14 (moderate), 15-19 (moderately severe), 20-27 (severe).</p>
            </div>
          </div>

          {/* GAD-7 Section */}
          <div className="p-5 bg-accent-50 rounded-xl border border-accent-100">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-semibold text-gray-800 flex items-center">
                  GAD-7
                  <span className="ml-2 text-xs bg-accent-200 text-accent-700 px-2 py-0.5 rounded-full">Anxiety</span>
                </h4>
                <p className="text-xs text-gray-500 mt-1">Generalized Anxiety Disorder-7</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-accent-600">
                  {prediction.gad7_score?.toFixed(0) || 0}
                  <span className="text-lg text-gray-400">/21</span>
                </div>
                <p className="text-sm font-medium text-accent-700">{prediction.gad7_severity || 'N/A'}</p>
              </div>
            </div>
            <div className="w-full bg-accent-100 rounded-full h-3 mb-3">
              <div 
                className="bg-gradient-to-r from-accent-400 to-accent-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${((prediction.gad7_score || 0) / 21) * 100}%` }}
              />
            </div>
            <div className="bg-white/60 rounded-lg p-3 text-xs text-gray-600">
              <p className="font-medium text-gray-700 mb-1">Clinical Theory:</p>
              <p>The GAD-7 is a validated screening tool for generalized anxiety disorder. Voice biomarkers correlating with anxiety include increased pitch mean, elevated jitter (voice tremor), faster speech rate, and irregular breathing patterns. These acoustic features reflect the physiological arousal state characteristic of anxiety. Scores: 0-4 (minimal), 5-9 (mild), 10-14 (moderate), 15-21 (severe).</p>
            </div>
          </div>

          {/* PSS Section */}
          <div className="p-5 bg-secondary-50 rounded-xl border border-secondary-100">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-semibold text-gray-800 flex items-center">
                  PSS
                  <span className="ml-2 text-xs bg-secondary-200 text-secondary-700 px-2 py-0.5 rounded-full">Stress</span>
                </h4>
                <p className="text-xs text-gray-500 mt-1">Perceived Stress Scale</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-secondary-600">
                  {prediction.pss_score?.toFixed(0) || 0}
                  <span className="text-lg text-gray-400">/40</span>
                </div>
                <p className="text-sm font-medium text-secondary-700">{prediction.pss_severity || 'N/A'}</p>
              </div>
            </div>
            <div className="w-full bg-secondary-100 rounded-full h-3 mb-3">
              <div 
                className="bg-gradient-to-r from-secondary-400 to-secondary-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${((prediction.pss_score || 0) / 40) * 100}%` }}
              />
            </div>
            <div className="bg-white/60 rounded-lg p-3 text-xs text-gray-600">
              <p className="font-medium text-gray-700 mb-1">Clinical Theory:</p>
              <p>The PSS measures the degree to which situations in life are perceived as stressful. Voice markers of stress include elevated shimmer (amplitude variation), increased pitch, shortened pause durations, and higher spectral energy. These reflect the autonomic nervous system activation during stress responses. Scores: 0-13 (low stress), 14-26 (moderate stress), 27-40 (high perceived stress).</p>
            </div>
          </div>

          {/* WEMWBS Section */}
          <div className="p-5 bg-success/10 rounded-xl border border-success/20">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h4 className="font-semibold text-gray-800 flex items-center">
                  WEMWBS
                  <span className="ml-2 text-xs bg-success/30 text-success px-2 py-0.5 rounded-full">Wellbeing</span>
                </h4>
                <p className="text-xs text-gray-500 mt-1">Warwick-Edinburgh Mental Wellbeing Scale</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-success">
                  {prediction.wemwbs_score?.toFixed(0) || 0}
                  <span className="text-lg text-gray-400">/70</span>
                </div>
                <p className="text-sm font-medium text-success">{prediction.wemwbs_severity || 'N/A'}</p>
              </div>
            </div>
            <div className="w-full bg-success/20 rounded-full h-3 mb-3">
              <div 
                className="bg-gradient-to-r from-success/70 to-success h-3 rounded-full transition-all duration-500"
                style={{ width: `${((prediction.wemwbs_score || 0) / 70) * 100}%` }}
              />
            </div>
            <div className="bg-white/60 rounded-lg p-3 text-xs text-gray-600">
              <p className="font-medium text-gray-700 mb-1">Clinical Theory:</p>
              <p>The WEMWBS measures positive mental wellbeing, focusing on positive affect, satisfying relationships, and positive functioning. Higher scores indicate better wellbeing. Voice markers of positive wellbeing include natural pitch variation, consistent speech rhythm, good harmonic-to-noise ratio, and expressive prosody. Scores: 14-31 (low wellbeing), 32-44 (below average), 45-58 (average), 59-70 (high wellbeing).</p>
            </div>
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
