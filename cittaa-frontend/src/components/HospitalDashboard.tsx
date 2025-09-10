import { useState } from 'react'
import { Heart, User, Clock, Shield, Activity, FileText, Users } from 'lucide-react'

interface HospitalDashboardProps {
  user: any
}

export default function HospitalDashboard({}: HospitalDashboardProps) {
  const [currentSession] = useState({
    type: 'Anxiety Therapy',
    patient: 'Rohan',
    age: 14,
    duration: 45,
    remaining: 45
  })

  const [sessionAnalytics] = useState({
    attentionSpan: 8.5,
    stressIndicators: 'Low',
    engagement: 'High'
  })

  const [therapyModeSettings] = useState({
    socialMedia: 'Blocked',
    gaming: 'Restricted',
    messaging: 'Family only',
    therapeuticApps: 'Enabled'
  })

  const handleEndSession = () => {
    console.log('Ending therapy session')
  }

  const handleNotes = () => {
    console.log('Opening session notes')
  }

  const handleFamily = () => {
    console.log('Contacting family')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 to-blue-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-3xl shadow-xl p-6 animate-slide-in">
          {/* Header */}
          <div className="border-b border-gray-200 pb-4 mb-6">
            <div className="flex items-center">
              <Heart className="w-8 h-8 mr-3 text-teal-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">AIIMS Child Psychology - CITTAA</h1>
                <p className="text-gray-600">👨‍⚕️ Dr. Sharma's Patient Portal</p>
              </div>
            </div>
          </div>

          {/* Current Session Info */}
          <div className="bg-gradient-to-r from-teal-50 to-blue-50 rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <User className="w-6 h-6 mr-3 text-teal-600" />
                <div>
                  <h2 className="text-xl font-semibold text-gray-800">Current Session: {currentSession.type}</h2>
                  <p className="text-gray-600">Patient: {currentSession.patient} (Age {currentSession.age})</p>
                </div>
              </div>
              <div className="text-right">
                <div className="flex items-center text-teal-600 font-medium">
                  <Clock className="w-5 h-5 mr-1" />
                  {currentSession.remaining} minutes remaining
                </div>
                <div className="text-sm text-gray-600">Duration: {currentSession.duration} minutes</div>
              </div>
            </div>
          </div>

          {/* Therapy Mode Status */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <Shield className="w-6 h-6 mr-2 text-green-600" />
              🔒 Therapy Mode Active
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
                <div className="text-red-600 font-medium">Social Media</div>
                <div className="text-sm text-gray-600">{therapyModeSettings.socialMedia}</div>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 text-center">
                <div className="text-orange-600 font-medium">Gaming</div>
                <div className="text-sm text-gray-600">{therapyModeSettings.gaming}</div>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
                <div className="text-blue-600 font-medium">Messaging</div>
                <div className="text-sm text-gray-600">{therapyModeSettings.messaging}</div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
                <div className="text-green-600 font-medium">Therapeutic Apps</div>
                <div className="text-sm text-gray-600">{therapyModeSettings.therapeuticApps}</div>
              </div>
            </div>
          </div>

          {/* Session Analytics */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
              <Activity className="w-6 h-6 mr-2 text-purple-600" />
              📊 Session Analytics
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-purple-50 rounded-xl p-6 text-center">
                <div className="text-3xl font-bold text-purple-600">{sessionAnalytics.attentionSpan}/10</div>
                <div className="text-sm text-gray-600">Attention Span</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${sessionAnalytics.attentionSpan * 10}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-green-50 rounded-xl p-6 text-center">
                <div className="text-2xl font-bold text-green-600">{sessionAnalytics.stressIndicators}</div>
                <div className="text-sm text-gray-600">Stress Indicators</div>
                <div className="mt-2">
                  <span className="inline-block w-3 h-3 bg-green-500 rounded-full"></span>
                </div>
              </div>

              <div className="bg-blue-50 rounded-xl p-6 text-center">
                <div className="text-2xl font-bold text-blue-600">{sessionAnalytics.engagement}</div>
                <div className="text-sm text-gray-600">Engagement</div>
                <div className="mt-2">
                  <span className="inline-block w-3 h-3 bg-blue-500 rounded-full"></span>
                </div>
              </div>
            </div>
          </div>

          {/* Mental Health Indicators */}
          <div className="mb-6">
            <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-xl p-4">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-yellow-500 rounded-full mr-3"></div>
                <div>
                  <div className="font-medium text-gray-800">Patient Progress Monitoring</div>
                  <div className="text-sm text-gray-600">Real-time behavioral analysis active • Compliance with Mental Healthcare Act 2017</div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4">
            <button
              onClick={handleEndSession}
              className="flex items-center px-6 py-3 bg-red-600 text-white rounded-xl font-medium hover:bg-red-700 transition-colors"
            >
              <Clock className="w-5 h-5 mr-2" />
              End Session
            </button>
            <button
              onClick={handleNotes}
              className="flex items-center px-6 py-3 cittaa-primary rounded-xl font-medium hover:bg-blue-700 transition-colors"
            >
              <FileText className="w-5 h-5 mr-2" />
              Notes
            </button>
            <button
              onClick={handleFamily}
              className="flex items-center px-6 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors"
            >
              <Users className="w-5 h-5 mr-2" />
              Family
            </button>
          </div>

          {/* Compliance Notice */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex items-center">
              <Shield className="w-5 h-5 mr-2 text-blue-600" />
              <div className="text-sm text-blue-800">
                <strong>Compliance:</strong> All patient data is encrypted and stored in compliance with Mental Healthcare Act 2017 and DPDP Act 2023. 
                Session recordings are automatically deleted after 30 days unless marked for clinical review.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
