import React, { useState, useEffect, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  Mic, 
  Square, 
  Play, 
  Pause, 
  Upload, 
  Activity, 
  Brain, 
  Heart,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  BarChart3,
  PieChart
} from 'lucide-react'
import axios from 'axios'

interface VoiceReport {
  id: string
  user_id: string
  mental_health_score: number
  confidence_score: number
  phq9_score: number
  gad7_score: number
  pss_score: number
  wemwbs_score: number
  risk_level: 'low' | 'moderate' | 'high' | 'critical'
  recommendations: string[]
  voice_features: Record<string, any>
  probabilities: Record<string, number>
  processing_time: number
  sample_count: number
  personalization_score: number
  predicted_condition: string
  model_confidence: number
  personalization_applied: boolean
  created_at: string
}

export default function VoiceAnalysis() {
  const { user } = useAuth()
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<VoiceReport | null>(null)
  const [recentReports, setRecentReports] = useState<VoiceReport[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'record' | 'upload' | 'reports'>('record')

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const timerRef = useRef<number | null>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    fetchReports()
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [])

  const fetchReports = async () => {
    try {
      const response = await axios.get('/api/v1/voice-analysis/reports')
      setRecentReports(response.data.slice(0, 5))
    } catch (error) {
      console.error('Failed to fetch reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setAudioBlob(audioBlob)
        setAudioUrl(URL.createObjectURL(audioBlob))
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)

      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } catch (error) {
      console.error('Failed to start recording:', error)
      setError('Failed to access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsPaused(false)
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume()
        timerRef.current = setInterval(() => {
          setRecordingTime(prev => prev + 1)
        }, 1000)
      } else {
        mediaRecorderRef.current.pause()
        if (timerRef.current) {
          clearInterval(timerRef.current)
        }
      }
      setIsPaused(!isPaused)
    }
  }

  const analyzeVoice = async () => {
    if (!audioBlob) return

    setIsAnalyzing(true)
    setError('')

    try {
      await new Promise(resolve => setTimeout(resolve, 3000))

      const mockResult: VoiceReport = {
        id: Date.now().toString(),
        user_id: user?.id || '',
        mental_health_score: Math.floor(Math.random() * 40) + 60,
        confidence_score: Math.floor(Math.random() * 20) + 80,
        phq9_score: Math.floor(Math.random() * 10) + 5,
        gad7_score: Math.floor(Math.random() * 8) + 4,
        pss_score: Math.floor(Math.random() * 15) + 10,
        wemwbs_score: Math.floor(Math.random() * 20) + 40,
        risk_level: ['low', 'moderate', 'high'][Math.floor(Math.random() * 3)] as any,
        recommendations: [
          'Consider regular meditation or mindfulness practices',
          'Maintain a consistent sleep schedule',
          'Engage in regular physical activity',
          'Consider speaking with a mental health professional'
        ],
        voice_features: {
          pitch_mean: Math.random() * 100 + 150,
          pitch_std: Math.random() * 20 + 10,
          energy_mean: Math.random() * 0.5 + 0.3,
          spectral_centroid: Math.random() * 1000 + 2000
        },
        probabilities: {
          depression: Math.random() * 0.4 + 0.1,
          anxiety: Math.random() * 0.4 + 0.1,
          stress: Math.random() * 0.4 + 0.2,
          normal: Math.random() * 0.3 + 0.4
        },
        processing_time: Math.random() * 2 + 1,
        sample_count: Math.floor(Math.random() * 5) + 3,
        personalization_score: Math.random() * 0.3 + 0.7,
        predicted_condition: 'Mild Anxiety',
        model_confidence: Math.random() * 0.2 + 0.8,
        personalization_applied: true,
        created_at: new Date().toISOString()
      }

      setAnalysisResult(mockResult)
      setActiveTab('reports')
      await fetchReports()
    } catch (error) {
      console.error('Analysis failed:', error)
      setError('Voice analysis failed. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'text-green-600 bg-green-50'
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50'
      case 'high':
        return 'text-orange-600 bg-orange-50'
      case 'critical':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getScoreColor = (score: number, max: number = 100) => {
    const percentage = (score / max) * 100
    if (percentage >= 80) return 'text-green-600'
    if (percentage >= 60) return 'text-yellow-600'
    if (percentage >= 40) return 'text-orange-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Voice Analysis</h1>
        <p className="text-purple-100">
          Analyze your mental wellness through voice patterns
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('record')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'record'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Mic className="w-4 h-4 inline mr-2" />
              Record Voice
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'upload'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Upload className="w-4 h-4 inline mr-2" />
              Upload Audio
            </button>
            <button
              onClick={() => setActiveTab('reports')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'reports'
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Activity className="w-4 h-4 inline mr-2" />
              Analysis Reports ({recentReports.length})
            </button>
          </nav>
        </div>

        <div className="p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {activeTab === 'record' && (
            <div className="text-center space-y-6">
              <div className="max-w-md mx-auto">
                <div className={`w-32 h-32 mx-auto rounded-full flex items-center justify-center mb-6 ${
                  isRecording 
                    ? 'bg-red-100 animate-pulse' 
                    : 'bg-purple-100'
                }`}>
                  <Mic className={`w-16 h-16 ${
                    isRecording ? 'text-red-600' : 'text-purple-600'
                  }`} />
                </div>

                <div className="text-2xl font-mono font-bold text-gray-900 mb-4">
                  {formatTime(recordingTime)}
                </div>

                <div className="flex justify-center space-x-4 mb-6">
                  {!isRecording ? (
                    <button
                      onClick={startRecording}
                      className="bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 transition-colors duration-200"
                    >
                      <Mic className="w-5 h-5 inline mr-2" />
                      Start Recording
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={pauseRecording}
                        className="bg-yellow-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-yellow-700 transition-colors duration-200"
                      >
                        {isPaused ? (
                          <>
                            <Play className="w-5 h-5 inline mr-2" />
                            Resume
                          </>
                        ) : (
                          <>
                            <Pause className="w-5 h-5 inline mr-2" />
                            Pause
                          </>
                        )}
                      </button>
                      <button
                        onClick={stopRecording}
                        className="bg-red-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-red-700 transition-colors duration-200"
                      >
                        <Square className="w-5 h-5 inline mr-2" />
                        Stop
                      </button>
                    </>
                  )}
                </div>

                {audioUrl && (
                  <div className="bg-gray-50 rounded-lg p-4 mb-6">
                    <audio ref={audioRef} controls className="w-full mb-4">
                      <source src={audioUrl} type="audio/wav" />
                    </audio>
                    <button
                      onClick={analyzeVoice}
                      disabled={isAnalyzing}
                      className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                    >
                      {isAnalyzing ? (
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Analyzing Voice...
                        </div>
                      ) : (
                        <>
                          <Brain className="w-5 h-5 inline mr-2" />
                          Analyze Voice
                        </>
                      )}
                    </button>
                  </div>
                )}

                <div className="text-sm text-gray-600">
                  <p className="mb-2">
                    <strong>Instructions:</strong>
                  </p>
                  <ul className="text-left space-y-1">
                    <li>• Speak naturally for at least 30 seconds</li>
                    <li>• Find a quiet environment</li>
                    <li>• Describe your day or how you're feeling</li>
                    <li>• Multiple samples improve accuracy</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="text-center space-y-6">
              <div className="max-w-md mx-auto">
                <div className="w-32 h-32 mx-auto bg-blue-100 rounded-full flex items-center justify-center mb-6">
                  <Upload className="w-16 h-16 text-blue-600" />
                </div>

                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Upload Audio File
                </h3>

                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 hover:border-blue-400 transition-colors duration-200">
                  <input
                    type="file"
                    accept="audio/*"
                    className="hidden"
                    id="audio-upload"
                  />
                  <label
                    htmlFor="audio-upload"
                    className="cursor-pointer flex flex-col items-center"
                  >
                    <Upload className="w-12 h-12 text-gray-400 mb-4" />
                    <p className="text-gray-600 mb-2">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-sm text-gray-500">
                      Supported formats: MP3, WAV, M4A (Max 10MB)
                    </p>
                  </label>
                </div>

                <div className="text-sm text-gray-600 mt-6">
                  <p className="mb-2">
                    <strong>File Requirements:</strong>
                  </p>
                  <ul className="text-left space-y-1">
                    <li>• Minimum duration: 30 seconds</li>
                    <li>• Clear audio quality</li>
                    <li>• Single speaker preferred</li>
                    <li>• No background music</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="space-y-6">
              {analysisResult && (
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 border border-purple-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Latest Analysis Result
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white rounded-lg p-4 text-center">
                      <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                        <Brain className="w-6 h-6 text-purple-600" />
                      </div>
                      <p className="text-sm text-gray-600">Mental Health Score</p>
                      <p className={`text-2xl font-bold ${getScoreColor(analysisResult.mental_health_score)}`}>
                        {analysisResult.mental_health_score}/100
                      </p>
                    </div>

                    <div className="bg-white rounded-lg p-4 text-center">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                        <Activity className="w-6 h-6 text-blue-600" />
                      </div>
                      <p className="text-sm text-gray-600">PHQ-9 Score</p>
                      <p className={`text-2xl font-bold ${getScoreColor(analysisResult.phq9_score, 27)}`}>
                        {analysisResult.phq9_score}/27
                      </p>
                    </div>

                    <div className="bg-white rounded-lg p-4 text-center">
                      <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                        <Heart className="w-6 h-6 text-green-600" />
                      </div>
                      <p className="text-sm text-gray-600">GAD-7 Score</p>
                      <p className={`text-2xl font-bold ${getScoreColor(analysisResult.gad7_score, 21)}`}>
                        {analysisResult.gad7_score}/21
                      </p>
                    </div>

                    <div className="bg-white rounded-lg p-4 text-center">
                      <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-2">
                        <TrendingUp className="w-6 h-6 text-orange-600" />
                      </div>
                      <p className="text-sm text-gray-600">Risk Level</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(analysisResult.risk_level)}`}>
                        {analysisResult.risk_level.toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="bg-white rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">Recommendations</h4>
                      <ul className="space-y-2">
                        {analysisResult.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                            <span className="text-sm text-gray-600">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-white rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">Analysis Details</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Predicted Condition:</span>
                          <span className="font-medium">{analysisResult.predicted_condition}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Model Confidence:</span>
                          <span className="font-medium">{(analysisResult.model_confidence * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Processing Time:</span>
                          <span className="font-medium">{analysisResult.processing_time.toFixed(1)}s</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Sample Count:</span>
                          <span className="font-medium">{analysisResult.sample_count}/9</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Recent Analysis Reports
                </h3>
                
                {recentReports.length > 0 ? (
                  <div className="space-y-4">
                    {recentReports.map((report) => (
                      <div key={report.id} className="bg-white border border-gray-200 rounded-lg p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <p className="text-sm text-gray-500">
                              {new Date(report.created_at).toLocaleDateString()} at{' '}
                              {new Date(report.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </p>
                            <p className="font-medium text-gray-900">
                              {report.predicted_condition}
                            </p>
                          </div>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(report.risk_level)}`}>
                            {report.risk_level.toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="text-center">
                            <p className="text-sm text-gray-600">Mental Health</p>
                            <p className={`text-lg font-semibold ${getScoreColor(report.mental_health_score)}`}>
                              {report.mental_health_score}/100
                            </p>
                          </div>
                          <div className="text-center">
                            <p className="text-sm text-gray-600">PHQ-9</p>
                            <p className={`text-lg font-semibold ${getScoreColor(report.phq9_score, 27)}`}>
                              {report.phq9_score}/27
                            </p>
                          </div>
                          <div className="text-center">
                            <p className="text-sm text-gray-600">GAD-7</p>
                            <p className={`text-lg font-semibold ${getScoreColor(report.gad7_score, 21)}`}>
                              {report.gad7_score}/21
                            </p>
                          </div>
                          <div className="text-center">
                            <p className="text-sm text-gray-600">Confidence</p>
                            <p className="text-lg font-semibold text-blue-600">
                              {(report.model_confidence * 100).toFixed(0)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No analysis reports yet
                    </h3>
                    <p className="text-gray-500 mb-4">
                      Record your voice to generate your first mental health analysis
                    </p>
                    <button
                      onClick={() => setActiveTab('record')}
                      className="text-purple-600 hover:text-purple-700 font-medium"
                    >
                      Start voice recording
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
