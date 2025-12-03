import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { psychologistService } from '../services/api'
import { 
  ArrowLeft, Phone, Mail, Calendar, Activity,
  FileText, Plus, AlertTriangle, Mic, Loader2
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

interface PatientData {
  patient: {
    id: string
    email: string
    full_name: string
    phone: string
    age_range: string
    gender: string
    language_preference: string
    consent_given: boolean
    assignment_date: string
    created_at: string
  }
  predictions: Array<{
    id: string
    predicted_at: string
    overall_risk_level: string
    mental_health_score: number
    depression_score: number
    anxiety_score: number
    stress_score: number
    phq9_score: number
    gad7_score: number
    pss_score: number
    confidence: number
  }>
  clinical_assessments: Array<{
    id: string
    assessment_date: string
    phq9_score: number
    gad7_score: number
    pss_score: number
    clinician_notes: string
    diagnosis: string
    treatment_plan: string
    session_number: number
  }>
  voice_samples_count: number
}

export default function PatientDetails() {
  const { patientId } = useParams<{ patientId: string }>()
  const [patientData, setPatientData] = useState<PatientData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAssessmentForm, setShowAssessmentForm] = useState(false)
  const [analyzingVoice, setAnalyzingVoice] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<{
    prediction_id: string
    risk_level: string
    mental_health_score: number
    phq9_score: number
    gad7_score: number
    pss_score: number
    wemwbs_score: number
    confidence: number
    interpretations: string[]
    recommendations: string[]
  } | null>(null)
  const [assessmentForm, setAssessmentForm] = useState({
    phq9_score: '',
    gad7_score: '',
    pss_score: '',
    clinician_notes: '',
    diagnosis: '',
    treatment_plan: ''
  })

  useEffect(() => {
    if (patientId) {
      loadPatientData()
    }
  }, [patientId])

  const loadPatientData = async () => {
    try {
      setLoading(true)
      const data = await psychologistService.getPatientDetails(patientId!)
      setPatientData(data)
    } catch (err) {
      setError('Failed to load patient data')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAssessment = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await psychologistService.createAssessment({
        patient_id: patientId!,
        phq9_score: assessmentForm.phq9_score ? parseInt(assessmentForm.phq9_score) : undefined,
        gad7_score: assessmentForm.gad7_score ? parseInt(assessmentForm.gad7_score) : undefined,
        pss_score: assessmentForm.pss_score ? parseInt(assessmentForm.pss_score) : undefined,
        clinician_notes: assessmentForm.clinician_notes || undefined,
        diagnosis: assessmentForm.diagnosis || undefined,
        treatment_plan: assessmentForm.treatment_plan || undefined
      })
      setShowAssessmentForm(false)
      setAssessmentForm({
        phq9_score: '',
        gad7_score: '',
        pss_score: '',
        clinician_notes: '',
        diagnosis: '',
        treatment_plan: ''
      })
      loadPatientData()
    } catch (err) {
      console.error('Failed to create assessment:', err)
    }
  }

  const handleVoiceAnalysis = async () => {
    try {
      setAnalyzingVoice(true)
      setAnalysisResult(null)
      const result = await psychologistService.analyzePatientVoice(patientId!)
      setAnalysisResult(result)
      loadPatientData()
    } catch (err) {
      console.error('Voice analysis failed:', err)
      setError('Failed to perform voice analysis')
    } finally {
      setAnalyzingVoice(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-success/10 text-success'
      case 'moderate': return 'bg-warning/10 text-warning'
      case 'high': return 'bg-error/10 text-error'
      default: return 'bg-gray-100 text-gray-500'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-12 h-12 text-primary-500 animate-spin" />
          <p className="mt-4 text-gray-500">Loading patient data...</p>
        </div>
      </div>
    )
  }

  if (error || !patientData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-error mx-auto mb-4" />
          <p className="text-gray-600">{error || 'Patient not found'}</p>
          <Link to="/psychologist/dashboard" className="text-primary-500 hover:underline mt-2 inline-block">
            Return to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  const { patient, predictions, clinical_assessments, voice_samples_count } = patientData

  // Prepare chart data
  const chartData = predictions.slice(0, 10).reverse().map(p => ({
    date: new Date(p.predicted_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    depression: (p.depression_score || 0) * 100,
    anxiety: (p.anxiety_score || 0) * 100,
    stress: (p.stress_score || 0) * 100,
    score: p.mental_health_score || 0
  }))

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Link 
          to="/psychologist/dashboard" 
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Patient Details</h1>
          <p className="text-sm text-gray-500">View and manage patient information</p>
        </div>
      </div>

      {/* Patient Info Card */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gradient-to-br from-primary-400 to-secondary-400 rounded-full flex items-center justify-center">
              <span className="text-white text-xl font-bold">
                {patient.full_name?.charAt(0) || patient.email?.charAt(0) || 'P'}
              </span>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-800">{patient.full_name || 'Unknown'}</h2>
              <div className="flex flex-wrap items-center gap-3 mt-1 text-sm text-gray-500">
                <span className="flex items-center">
                  <Mail className="w-4 h-4 mr-1" />
                  {patient.email}
                </span>
                {patient.phone && (
                  <span className="flex items-center">
                    <Phone className="w-4 h-4 mr-1" />
                    {patient.phone}
                  </span>
                )}
              </div>
              <div className="flex flex-wrap gap-2 mt-2">
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  {patient.age_range || 'Age N/A'}
                </span>
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded capitalize">
                  {patient.gender || 'Gender N/A'}
                </span>
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded capitalize">
                  {patient.language_preference || 'English'}
                </span>
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            <span className="text-sm text-gray-500">
              <Calendar className="w-4 h-4 inline mr-1" />
              Assigned: {patient.assignment_date ? new Date(patient.assignment_date).toLocaleDateString() : 'N/A'}
            </span>
            <span className="text-sm text-gray-500">
              Voice Samples: {voice_samples_count}
            </span>
          </div>
        </div>
      </div>

      {/* Stats and Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Latest Stats */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-800 mb-4">Latest Assessment</h3>
          {predictions.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Mental Health Score</span>
                <span className="text-xl font-bold text-primary-600">
                  {predictions[0].mental_health_score?.toFixed(0) || 'N/A'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Risk Level</span>
                <span className={`px-2 py-1 rounded text-sm font-medium capitalize ${getRiskColor(predictions[0].overall_risk_level)}`}>
                  {predictions[0].overall_risk_level || 'Unknown'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">PHQ-9</span>
                <span className="font-medium">{predictions[0].phq9_score?.toFixed(0) || 'N/A'}/27</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">GAD-7</span>
                <span className="font-medium">{predictions[0].gad7_score?.toFixed(0) || 'N/A'}/21</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">PSS</span>
                <span className="font-medium">{predictions[0].pss_score?.toFixed(0) || 'N/A'}/40</span>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No assessments yet</p>
          )}
        </div>

        {/* Trend Chart */}
        <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="font-semibold text-gray-800 mb-4">Mental Health Trends</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
                <Legend />
                <Line type="monotone" dataKey="depression" stroke="#8B5A96" strokeWidth={2} name="Depression" />
                <Line type="monotone" dataKey="anxiety" stroke="#FF8C42" strokeWidth={2} name="Anxiety" />
                <Line type="monotone" dataKey="stress" stroke="#7BB3A8" strokeWidth={2} name="Stress" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[200px] flex items-center justify-center text-gray-400">
              No trend data available
            </div>
          )}
        </div>
      </div>

      {/* Voice Analysis Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-5 border-b border-gray-100 flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">Voice Analysis</h3>
          <button
            onClick={handleVoiceAnalysis}
            disabled={analyzingVoice}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-primary-500 to-secondary-400 text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {analyzingVoice ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Mic className="w-4 h-4 mr-2" />
                Run Voice Analysis
              </>
            )}
          </button>
        </div>
        
        {analysisResult && (
          <div className="p-5 space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-500">Mental Health Score</p>
                <p className="text-2xl font-bold text-primary-600">{analysisResult.mental_health_score?.toFixed(0) || 'N/A'}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-500">Risk Level</p>
                <p className={`text-lg font-semibold capitalize ${
                  analysisResult.risk_level === 'low' ? 'text-success' :
                  analysisResult.risk_level === 'moderate' ? 'text-warning' : 'text-error'
                }`}>{analysisResult.risk_level}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-500">Confidence</p>
                <p className="text-lg font-semibold text-gray-700">{((analysisResult.confidence || 0) * 100).toFixed(0)}%</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <p className="text-sm text-gray-500">PHQ-9</p>
                <p className="text-lg font-semibold text-gray-700">{analysisResult.phq9_score?.toFixed(0) || 'N/A'}/27</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-primary-50 rounded-lg p-4">
                <p className="text-sm font-medium text-primary-700">GAD-7 (Anxiety)</p>
                <p className="text-xl font-bold text-primary-600">{analysisResult.gad7_score?.toFixed(0) || 'N/A'}/21</p>
              </div>
              <div className="bg-secondary-50 rounded-lg p-4">
                <p className="text-sm font-medium text-secondary-700">PSS (Stress)</p>
                <p className="text-xl font-bold text-secondary-600">{analysisResult.pss_score?.toFixed(0) || 'N/A'}/40</p>
              </div>
              <div className="bg-accent-50 rounded-lg p-4">
                <p className="text-sm font-medium text-accent-700">WEMWBS (Wellbeing)</p>
                <p className="text-xl font-bold text-accent-600">{analysisResult.wemwbs_score?.toFixed(0) || 'N/A'}/70</p>
              </div>
            </div>
            
            {analysisResult.interpretations && analysisResult.interpretations.length > 0 && (
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-800 mb-2">Clinical Interpretations</h4>
                <ul className="space-y-1">
                  {analysisResult.interpretations.map((item, idx) => (
                    <li key={idx} className="text-sm text-blue-700">{item}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-medium text-green-800 mb-2">Recommendations</h4>
                <ul className="space-y-1">
                  {analysisResult.recommendations.map((item, idx) => (
                    <li key={idx} className="text-sm text-green-700">{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {!analysisResult && !analyzingVoice && (
          <div className="p-12 text-center">
            <Mic className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Click "Run Voice Analysis" to analyze patient's voice samples</p>
            <p className="text-sm text-gray-400 mt-1">Results will be saved to patient's record and visible in their portal</p>
          </div>
        )}
      </div>

      {/* Clinical Assessments */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-5 border-b border-gray-100 flex items-center justify-between">
          <h3 className="font-semibold text-gray-800">Clinical Assessments</h3>
          <button
            onClick={() => setShowAssessmentForm(true)}
            className="flex items-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Assessment
          </button>
        </div>
        
        {showAssessmentForm && (
          <div className="p-5 border-b border-gray-100 bg-gray-50">
            <form onSubmit={handleCreateAssessment} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">PHQ-9 Score (0-27)</label>
                  <input
                    type="number"
                    min="0"
                    max="27"
                    value={assessmentForm.phq9_score}
                    onChange={(e) => setAssessmentForm(prev => ({ ...prev, phq9_score: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">GAD-7 Score (0-21)</label>
                  <input
                    type="number"
                    min="0"
                    max="21"
                    value={assessmentForm.gad7_score}
                    onChange={(e) => setAssessmentForm(prev => ({ ...prev, gad7_score: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">PSS Score (0-40)</label>
                  <input
                    type="number"
                    min="0"
                    max="40"
                    value={assessmentForm.pss_score}
                    onChange={(e) => setAssessmentForm(prev => ({ ...prev, pss_score: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Clinical Notes</label>
                <textarea
                  value={assessmentForm.clinician_notes}
                  onChange={(e) => setAssessmentForm(prev => ({ ...prev, clinician_notes: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosis</label>
                  <input
                    type="text"
                    value={assessmentForm.diagnosis}
                    onChange={(e) => setAssessmentForm(prev => ({ ...prev, diagnosis: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Treatment Plan</label>
                  <input
                    type="text"
                    value={assessmentForm.treatment_plan}
                    onChange={(e) => setAssessmentForm(prev => ({ ...prev, treatment_plan: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowAssessmentForm(false)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  Save Assessment
                </button>
              </div>
            </form>
          </div>
        )}

        {clinical_assessments.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No clinical assessments recorded</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {clinical_assessments.map((assessment) => (
              <div key={assessment.id} className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-800">Session #{assessment.session_number}</span>
                  <span className="text-sm text-gray-500">
                    {new Date(assessment.assessment_date).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 mb-2">
                  {assessment.phq9_score !== null && (
                    <span className="text-xs bg-primary-50 text-primary-600 px-2 py-1 rounded">
                      PHQ-9: {assessment.phq9_score}
                    </span>
                  )}
                  {assessment.gad7_score !== null && (
                    <span className="text-xs bg-accent-50 text-accent-600 px-2 py-1 rounded">
                      GAD-7: {assessment.gad7_score}
                    </span>
                  )}
                  {assessment.pss_score !== null && (
                    <span className="text-xs bg-secondary-50 text-secondary-600 px-2 py-1 rounded">
                      PSS: {assessment.pss_score}
                    </span>
                  )}
                </div>
                {assessment.clinician_notes && (
                  <p className="text-sm text-gray-600 mt-2">{assessment.clinician_notes}</p>
                )}
                {assessment.diagnosis && (
                  <p className="text-sm text-gray-500 mt-1">
                    <strong>Diagnosis:</strong> {assessment.diagnosis}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
