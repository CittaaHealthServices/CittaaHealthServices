import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { voiceService, SampleProgress } from '../services/api'
import { 
  Mic, Square, Play, Pause, Upload, AlertCircle, 
  CheckCircle, Loader, Volume2, Activity, Target, Flame, Award
} from 'lucide-react'

export default function VoiceRecording() {
  const navigate = useNavigate()
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [duration, setDuration] = useState(0)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [waveformData, setWaveformData] = useState<number[]>([])
  const [sampleProgress, setSampleProgress] = useState<SampleProgress | null>(null)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationRef = useRef<number | null>(null)

  useEffect(() => {
    loadSampleProgress()
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
      if (audioUrl) URL.revokeObjectURL(audioUrl)
    }
  }, [audioUrl])

  const loadSampleProgress = async () => {
    try {
      const progress = await voiceService.getSampleProgress()
      setSampleProgress(progress)
    } catch (err) {
      console.error('Failed to load sample progress:', err)
    }
  }

  const startRecording = async () => {
    try {
      setError('')
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      })

      // Set up audio analysis for waveform
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      source.connect(analyser)
      analyserRef.current = analyser

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        setAudioBlob(audioBlob)
        setAudioUrl(URL.createObjectURL(audioBlob))
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start(100)
      setIsRecording(true)
      setDuration(0)

      // Start timer
      timerRef.current = setInterval(() => {
        setDuration(prev => prev + 1)
      }, 1000)

      // Start waveform animation
      const updateWaveform = () => {
        if (analyserRef.current) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
          analyserRef.current.getByteFrequencyData(dataArray)
          const normalizedData = Array.from(dataArray.slice(0, 32)).map(v => v / 255)
          setWaveformData(normalizedData)
        }
        animationRef.current = requestAnimationFrame(updateWaveform)
      }
      updateWaveform()

    } catch (err) {
      setError('Microphone access denied. Please allow microphone access to record.')
      console.error(err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsPaused(false)
      if (timerRef.current) clearInterval(timerRef.current)
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
      setWaveformData([])
    }
  }

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume()
        timerRef.current = setInterval(() => {
          setDuration(prev => prev + 1)
        }, 1000)
      } else {
        mediaRecorderRef.current.pause()
        if (timerRef.current) clearInterval(timerRef.current)
      }
      setIsPaused(!isPaused)
    }
  }

  const resetRecording = () => {
    setAudioBlob(null)
    if (audioUrl) URL.revokeObjectURL(audioUrl)
    setAudioUrl(null)
    setDuration(0)
    setError('')
    setUploadProgress(0)
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('audio/')) {
        setError('Please upload an audio file')
        return
      }
      if (file.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB')
        return
      }
      setAudioBlob(file)
      setAudioUrl(URL.createObjectURL(file))
      setError('')
    }
  }

  const analyzeRecording = async () => {
    if (!audioBlob) return

    try {
      setAnalyzing(true)
      setError('')
      setUploadProgress(10)

      // Convert blob to file
      const file = new File([audioBlob], 'recording.webm', { type: audioBlob.type })
      
      setUploadProgress(30)
      
      // Upload voice sample
      const uploadResponse = await voiceService.uploadVoice(file)
      setUploadProgress(60)

      // Analyze the sample
      const analysisResult = await voiceService.analyzeVoice(uploadResponse.sample_id)
      setUploadProgress(100)

      // Navigate to results
      navigate(`/results/${analysisResult.id}`)

    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 
        'Analysis failed. Please try again.'
      setError(errorMessage)
      setUploadProgress(0)
    } finally {
      setAnalyzing(false)
    }
  }

  const runDemoAnalysis = async (demoType: string) => {
    try {
      setAnalyzing(true)
      setError('')
      
      const result = await voiceService.demoAnalyze(demoType)
      navigate(`/results/${result.id}`)
      
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 
        'Demo analysis failed. Please try again.'
      setError(errorMessage)
    } finally {
      setAnalyzing(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-2 mb-2">
          <span className="text-xl font-display italic text-primary-700">Cittaa</span>
          <span className="text-primary-400">|</span>
          <span className="text-primary-600">Vocalysis</span>
        </div>
        <h1 className="text-2xl font-bold text-primary-800">Voice Recording</h1>
        <p className="text-primary-600 mt-1">Record or upload a voice sample for mental health analysis</p>
      </div>

      {/* Sample Collection Progress Card */}
      {sampleProgress && (
        <div className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-primary-500">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                sampleProgress.baseline_established 
                  ? 'bg-success/20 text-success' 
                  : 'bg-primary-100 text-primary-600'
              }`}>
                {sampleProgress.baseline_established ? (
                  <Award className="w-6 h-6" />
                ) : (
                  <Target className="w-6 h-6" />
                )}
              </div>
              <div>
                <h3 className="font-semibold text-gray-800">
                  {sampleProgress.baseline_established ? 'Personalized Analysis Active' : 'Building Your Baseline'}
                </h3>
                <p className="text-sm text-gray-500">{sampleProgress.message}</p>
              </div>
            </div>
            {sampleProgress.streak_days > 0 && (
              <div className="flex items-center space-x-1 px-3 py-1 bg-accent-50 rounded-full">
                <Flame className="w-4 h-4 text-accent-500" />
                <span className="text-sm font-medium text-accent-600">{sampleProgress.streak_days} day streak</span>
              </div>
            )}
          </div>
          
          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">
                Sample {sampleProgress.samples_collected} of {sampleProgress.target_samples}
              </span>
              <span className="font-medium text-primary-600">
                {sampleProgress.progress_percentage.toFixed(0)}%
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-3">
              <div 
                className={`h-3 rounded-full transition-all duration-500 ${
                  sampleProgress.baseline_established 
                    ? 'bg-success' 
                    : 'bg-gradient-to-r from-primary-500 to-secondary-400'
                }`}
                style={{ width: `${sampleProgress.progress_percentage}%` }}
              />
            </div>
          </div>
          
          {/* Stats Row */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-primary-600">{sampleProgress.samples_collected}</p>
              <p className="text-xs text-gray-500">Total Samples</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-secondary-500">{sampleProgress.today_samples}</p>
              <p className="text-xs text-gray-500">Today</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-accent-500">{sampleProgress.samples_remaining}</p>
              <p className="text-xs text-gray-500">Remaining</p>
            </div>
          </div>
          
          {/* Personalization Score (if baseline established) */}
          {sampleProgress.baseline_established && sampleProgress.personalization_score && (
            <div className="mt-4 p-3 bg-success/10 rounded-lg flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-success" />
                <span className="text-sm text-gray-700">Personalization Quality</span>
              </div>
              <span className="font-semibold text-success">
                {(sampleProgress.personalization_score * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>
      )}

      {/* Recording Card */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        {/* Waveform Visualization */}
        <div className="h-24 bg-gray-50 rounded-xl mb-6 flex items-center justify-center overflow-hidden">
          {isRecording ? (
            <div className="flex items-end justify-center space-x-1 h-full py-4">
              {waveformData.map((value, index) => (
                <div
                  key={index}
                  className="w-2 bg-gradient-to-t from-primary-500 to-secondary-400 rounded-full transition-all duration-75"
                  style={{ height: `${Math.max(10, value * 100)}%` }}
                />
              ))}
              {waveformData.length === 0 && (
                Array.from({ length: 32 }).map((_, index) => (
                  <div
                    key={index}
                    className="w-2 bg-gradient-to-t from-primary-500 to-secondary-400 rounded-full waveform-bar"
                    style={{ 
                      height: '20%',
                      animationDelay: `${index * 0.05}s`
                    }}
                  />
                ))
              )}
            </div>
          ) : audioUrl ? (
            <audio controls src={audioUrl} className="w-full max-w-md" />
          ) : (
            <div className="text-gray-400 flex flex-col items-center">
              <Volume2 className="w-8 h-8 mb-2" />
              <span className="text-sm">Ready to record</span>
            </div>
          )}
        </div>

        {/* Timer */}
        <div className="text-center mb-6">
          <div className="text-4xl font-mono font-bold text-gray-800">
            {formatTime(duration)}
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {isRecording ? (isPaused ? 'Paused' : 'Recording...') : 
             audioBlob ? 'Recording complete' : 'Minimum 10 seconds required'}
          </p>
        </div>

        {/* Recording Controls */}
        <div className="flex items-center justify-center space-x-4">
          {!isRecording && !audioBlob && (
            <>
              <button
                onClick={startRecording}
                className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
              >
                <Mic className="w-8 h-8" />
              </button>
              
              <div className="text-gray-300">or</div>
              
              <label className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center text-gray-500 cursor-pointer hover:bg-gray-200 transition-all duration-200">
                <Upload className="w-8 h-8" />
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </>
          )}

          {isRecording && (
            <>
              <button
                onClick={pauseRecording}
                className="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 hover:bg-gray-200 transition-all duration-200"
              >
                {isPaused ? <Play className="w-6 h-6" /> : <Pause className="w-6 h-6" />}
              </button>
              
              <button
                onClick={stopRecording}
                className="w-20 h-20 bg-gradient-to-br from-error to-red-600 rounded-full flex items-center justify-center text-white shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 recording-pulse"
              >
                <Square className="w-8 h-8" />
              </button>
            </>
          )}

          {audioBlob && !isRecording && (
            <>
              <button
                onClick={resetRecording}
                className="px-6 py-3 bg-gray-100 rounded-lg text-gray-600 font-medium hover:bg-gray-200 transition-all duration-200"
              >
                Record Again
              </button>
              
              <button
                onClick={analyzeRecording}
                disabled={analyzing || duration < 10}
                className={`
                  px-8 py-3 rounded-lg font-medium text-white
                  bg-gradient-to-r from-primary-500 to-secondary-400
                  hover:from-primary-600 hover:to-secondary-500
                  transition-all duration-200 shadow-lg
                  ${(analyzing || duration < 10) ? 'opacity-70 cursor-not-allowed' : ''}
                `}
              >
                {analyzing ? (
                  <span className="flex items-center">
                    <Loader className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Activity className="w-5 h-5 mr-2" />
                    Analyze Voice
                  </span>
                )}
              </button>
            </>
          )}
        </div>

        {/* Progress Bar */}
        {analyzing && uploadProgress > 0 && (
          <div className="mt-6">
            <div className="flex justify-between text-sm text-gray-500 mb-1">
              <span>Processing...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-primary-500 to-secondary-400 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-red-600 animate-fadeIn">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}
      </div>

      {/* Demo Mode */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Demo Mode</h3>
        <p className="text-sm text-gray-500 mb-4">
          Try the analysis with pre-generated demo results to see how the system works.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {['normal', 'anxiety', 'depression', 'stress'].map((type) => (
            <button
              key={type}
              onClick={() => runDemoAnalysis(type)}
              disabled={analyzing}
              className={`
                px-4 py-3 rounded-lg font-medium capitalize
                border-2 transition-all duration-200
                ${type === 'normal' ? 'border-success/30 text-success hover:bg-success/10' :
                  type === 'anxiety' ? 'border-accent-400/30 text-accent-500 hover:bg-accent-50' :
                  type === 'depression' ? 'border-primary-400/30 text-primary-500 hover:bg-primary-50' :
                  'border-secondary-400/30 text-secondary-500 hover:bg-secondary-50'}
                ${analyzing ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-6">
        <h3 className="font-semibold text-gray-800 mb-3">Recording Tips</h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li className="flex items-start">
            <CheckCircle className="w-4 h-4 text-success mr-2 mt-0.5 flex-shrink-0" />
            Speak naturally for at least 30 seconds to 2 minutes
          </li>
          <li className="flex items-start">
            <CheckCircle className="w-4 h-4 text-success mr-2 mt-0.5 flex-shrink-0" />
            Find a quiet environment with minimal background noise
          </li>
          <li className="flex items-start">
            <CheckCircle className="w-4 h-4 text-success mr-2 mt-0.5 flex-shrink-0" />
            Talk about your day, feelings, or read a passage aloud
          </li>
          <li className="flex items-start">
            <CheckCircle className="w-4 h-4 text-success mr-2 mt-0.5 flex-shrink-0" />
            Keep the microphone at a consistent distance
          </li>
        </ul>
      </div>
    </div>
  )
}
