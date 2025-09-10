import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, BookOpen, Palette, Gamepad2, HelpCircle, ArrowLeft } from 'lucide-react'

export default function ContentBlocked() {
  const [language, setLanguage] = useState('english')
  const navigate = useNavigate()

  const translations = {
    english: {
      title: 'Content Blocked',
      subtitle: 'This content is not suitable for your age group.',
      instead: 'Instead, try these:',
      educational: 'Educational Videos',
      study: 'Study Materials',
      creative: 'Creative Activities',
      games: 'Approved Games',
      request: 'Request Parent Review',
      back: 'Back to Safe Zone',
      help: 'Need help?',
      support: 'Contact Support'
    },
    hindi: {
      title: 'सामग्री अवरुद्ध',
      subtitle: 'यह सामग्री आपके आयु समूह के लिए उपयुक्त नहीं है।',
      instead: 'इसके बजाय, इन्हें आज़माएं:',
      educational: 'शैक्षिक वीडियो',
      study: 'अध्ययन सामग्री',
      creative: 'रचनात्मक गतिविधियां',
      games: 'अनुमोदित खेल',
      request: 'माता-पिता की समीक्षा का अनुरोध करें',
      back: 'सुरक्षित क्षेत्र में वापस जाएं',
      help: 'सहायता चाहिए?',
      support: 'सहायता से संपर्क करें'
    }
  }

  const t = translations[language as keyof typeof translations]

  const alternatives = [
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: t.educational,
      color: 'bg-blue-500',
      url: 'https://ncert.nic.in/textbook/textbook.htm'
    },
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: t.study,
      color: 'bg-green-500',
      url: 'https://www.khanacademy.org/'
    },
    {
      icon: <Palette className="w-8 h-8" />,
      title: t.creative,
      color: 'bg-purple-500',
      url: '/creative-activities'
    },
    {
      icon: <Gamepad2 className="w-8 h-8" />,
      title: t.games,
      color: 'bg-orange-500',
      url: '/approved-games'
    }
  ]

  const handleRequestReview = () => {
    console.log('Requesting parent review')
    alert('Parent review request sent! Your parents will be notified.')
  }

  const handleBackToSafeZone = () => {
    navigate('/child-dashboard')
  }

  const handleContactSupport = () => {
    console.log('Contacting support')
    alert('Support team will contact you shortly.')
  }

  const handleAlternativeClick = (url: string) => {
    if (url.startsWith('http')) {
      window.open(url, '_blank')
    } else {
      navigate(url)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-100 via-orange-50 to-yellow-50 p-4 flex items-center justify-center">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-3xl shadow-2xl p-8 animate-slide-in">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mx-auto w-24 h-24 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center mb-4 festival-glow">
              <Shield className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">🛡️ {t.title}</h1>
          </div>

          {/* Blocked Content Icon */}
          <div className="text-center mb-6">
            <div className="w-20 h-20 bg-red-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-4xl">🚫</span>
            </div>
          </div>

          {/* Message */}
          <div className="text-center mb-8">
            <p className="text-gray-700 mb-4">{t.subtitle}</p>
            <p className="font-medium text-gray-800">{t.instead}</p>
          </div>

          {/* Alternative Content */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            {alternatives.map((alt, index) => (
              <button
                key={index}
                onClick={() => handleAlternativeClick(alt.url)}
                className={`${alt.color} text-white rounded-xl p-4 text-center transition-transform hover:scale-105 animate-bounce-gentle`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex justify-center mb-2">{alt.icon}</div>
                <div className="text-sm font-medium">{alt.title}</div>
              </button>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="space-y-3 mb-6">
            <button
              onClick={handleRequestReview}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-3 px-4 font-medium transition-colors"
            >
              {t.request}
            </button>
            <button
              onClick={handleBackToSafeZone}
              className="w-full cittaa-primary rounded-xl py-3 px-4 font-medium hover:bg-blue-700 transition-colors flex items-center justify-center"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              {t.back}
            </button>
          </div>

          {/* Support */}
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">{t.help}</p>
            <button
              onClick={handleContactSupport}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center justify-center mx-auto"
            >
              <HelpCircle className="w-4 h-4 mr-1" />
              {t.support}
            </button>
          </div>

          {/* Language Toggle */}
          <div className="flex justify-center mt-6 space-x-2">
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
