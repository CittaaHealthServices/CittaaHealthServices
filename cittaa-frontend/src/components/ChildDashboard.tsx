import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpen, GamepadIcon, Music, Phone, Target, Clock, Shield } from 'lucide-react'

import type { User } from '../types'

interface ChildDashboardProps {
  user: User | null
}

export default function ChildDashboard({ user }: ChildDashboardProps) {
  const [timeRemaining] = useState({ games: 120, total: 480 })
  const [learningGoals] = useState([
    { subject: 'Math Practice', target: 30, completed: 30, status: 'completed' },
    { subject: 'Science Reading', target: 45, completed: 20, status: 'in-progress' },
    { subject: 'English Writing', target: 20, completed: 0, status: 'pending' }
  ])
  const [language, setLanguage] = useState('english')
  const navigate = useNavigate()

  const translations = {
    english: {
      welcome: 'Welcome',
      safeZoneOn: 'Safe Zone ON',
      todaysGoals: "Today's Learning Goals",
      recommended: 'Recommended Content',
      approvedGames: 'Approved Games',
      musicStories: 'Music & Stories',
      emergency: 'Emergency Parent Call',
      timeLeft: 'left'
    },
    hindi: {
      welcome: 'स्वागत',
      safeZoneOn: 'सुरक्षित क्षेत्र चालू',
      todaysGoals: 'आज के शिक्षा लक्ष्य',
      recommended: 'अनुशंसित सामग्री',
      approvedGames: 'अनुमोदित खेल',
      musicStories: 'संगीत और कहानियां',
      emergency: 'आपातकालीन माता-पिता कॉल',
      timeLeft: 'बचा है'
    }
  }

  const t = translations[language as keyof typeof translations]

  const educationalContent = [
    { name: 'NCERT Math', icon: '📚', color: 'bg-blue-500', url: '/educational/ncert-math' },
    { name: 'Khan Academy', icon: '🎓', color: 'bg-green-500', url: '/educational/khan-academy' },
    { name: "Byju's", icon: '📖', color: 'bg-purple-500', url: '/educational/byjus' }
  ]

  const handleEmergencyCall = () => {
    navigate('/emergency-override')
  }

  const handleContentClick = (url: string) => {
    window.open(url, '_blank')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-4">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-3xl shadow-xl p-6 animate-slide-in">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="flex items-center justify-center mb-4">
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center mr-3">
                <span className="text-2xl">👦</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">
                  {t.welcome} {user?.name || 'Aarav'}! 📚
                </h1>
                <div className="flex items-center text-green-600 font-medium">
                  <Shield className="w-4 h-4 mr-1 animate-pulse-safe" />
                  {t.safeZoneOn}
                </div>
              </div>
            </div>
          </div>

          {/* Learning Goals */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <Target className="w-5 h-5 mr-2 text-blue-600" />
              {t.todaysGoals}
            </h2>
            <div className="space-y-3">
              {learningGoals.map((goal, index) => (
                <div key={index} className="bg-gray-50 rounded-xl p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-700">{goal.subject}</span>
                    {goal.status === 'completed' && <span className="text-green-600">✓</span>}
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-500 ${
                        goal.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${(goal.completed / goal.target) * 100}%` }}
                    ></div>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {goal.completed}/{goal.target} mins
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Content */}
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <BookOpen className="w-5 h-5 mr-2 text-purple-600" />
              {t.recommended}
            </h2>
            <div className="grid grid-cols-3 gap-3">
              {educationalContent.map((content, index) => (
                <button
                  key={index}
                  onClick={() => handleContentClick(content.url)}
                  className={`${content.color} text-white rounded-xl p-4 text-center transition-transform hover:scale-105 animate-bounce-gentle`}
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="text-2xl mb-1">{content.icon}</div>
                  <div className="text-xs font-medium">{content.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Games and Entertainment */}
          <div className="mb-6">
            <div className="bg-gradient-to-r from-orange-100 to-pink-100 rounded-xl p-4 mb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <GamepadIcon className="w-5 h-5 mr-2 text-orange-600" />
                  <span className="font-medium text-gray-800">{t.approvedGames}</span>
                </div>
                <div className="flex items-center text-orange-600 font-medium">
                  <Clock className="w-4 h-4 mr-1" />
                  {timeRemaining.games}m {t.timeLeft}
                </div>
              </div>
            </div>

            <button className="w-full bg-gradient-to-r from-purple-100 to-blue-100 rounded-xl p-4 text-left transition-transform hover:scale-105">
              <div className="flex items-center">
                <Music className="w-5 h-5 mr-3 text-purple-600" />
                <span className="font-medium text-gray-800">{t.musicStories}</span>
              </div>
            </button>
          </div>

          {/* Emergency Call */}
          <button
            onClick={handleEmergencyCall}
            className="w-full bg-red-500 hover:bg-red-600 text-white rounded-xl p-4 font-medium transition-colors flex items-center justify-center"
          >
            <Phone className="w-5 h-5 mr-2" />
            {t.emergency} 🆘
          </button>

          {/* Language Toggle */}
          <div className="flex justify-center mt-4 space-x-2">
            <button
              onClick={() => setLanguage('hindi')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                language === 'hindi' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => setLanguage('english')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                language === 'english' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              English
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
