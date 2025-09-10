import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, AlertTriangle, ArrowLeft, Info } from 'lucide-react'

export default function VPNAlert() {
  const [language, setLanguage] = useState('english')
  const navigate = useNavigate()

  const translations = {
    english: {
      title: 'Security Alert',
      detected: 'VPN Connection Detected and Blocked',
      device: 'Device:',
      time: 'Time:',
      app: 'App:',
      status: 'Status:',
      protected: 'Your safety is protected',
      notified: 'Parents have been notified via WhatsApp and email.',
      understand: 'Understand Why',
      return: 'Return to Safe Zone'
    },
    hindi: {
      title: 'सुरक्षा चेतावनी',
      detected: 'VPN कनेक्शन का पता लगाया गया और अवरुद्ध किया गया',
      device: 'डिवाइस:',
      time: 'समय:',
      app: 'ऐप:',
      status: 'स्थिति:',
      protected: 'आपकी सुरक्षा सुरक्षित है',
      notified: 'माता-पिता को व्हाट्सऐप और ईमेल के माध्यम से सूचित किया गया है।',
      understand: 'समझें कि क्यों',
      return: 'सुरक्षित क्षेत्र में वापस जाएं'
    }
  }

  const t = translations[language as keyof typeof translations]

  const alertData = {
    device: "Aarav's Phone",
    time: 'Just now',
    app: 'TurboVPN',
    status: 'Installation Prevented'
  }

  const handleUnderstandWhy = () => {
    alert(`VPNs can be used to bypass parental controls and access inappropriate content. CITTAA blocks VPNs to keep you safe and ensure your parents can monitor your online activities for your protection.`)
  }

  const handleReturnToSafeZone = () => {
    navigate('/child-dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-100 via-orange-50 to-yellow-50 p-4 flex items-center justify-center">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-3xl shadow-2xl p-8 animate-slide-in">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mx-auto w-24 h-24 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center mb-4 festival-glow animate-pulse-safe">
              <AlertTriangle className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">🚨 {t.title}</h1>
          </div>

          {/* Security Shield Icon */}
          <div className="text-center mb-6">
            <div className="w-20 h-20 bg-red-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-4xl">⚠️</span>
            </div>
          </div>

          {/* Alert Message */}
          <div className="text-center mb-8">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">{t.detected}</h2>
          </div>

          {/* Alert Details */}
          <div className="bg-gray-50 rounded-xl p-6 mb-6 space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">{t.device}</span>
              <span className="font-medium text-gray-800">{alertData.device}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">{t.time}</span>
              <span className="font-medium text-gray-800">{alertData.time}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">{t.app}</span>
              <span className="font-medium text-gray-800">{alertData.app}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">{t.status}</span>
              <span className="font-medium text-red-600">{alertData.status}</span>
            </div>
          </div>

          {/* Safety Message */}
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6">
            <div className="flex items-center">
              <Shield className="w-6 h-6 text-green-600 mr-3" />
              <div>
                <div className="font-medium text-green-800">🔒 {t.protected}</div>
                <div className="text-sm text-green-700 mt-1">{t.notified}</div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3 mb-6">
            <button
              onClick={handleUnderstandWhy}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-3 px-4 font-medium transition-colors flex items-center justify-center"
            >
              <Info className="w-5 h-5 mr-2" />
              {t.understand}
            </button>
            <button
              onClick={handleReturnToSafeZone}
              className="w-full cittaa-primary rounded-xl py-3 px-4 font-medium hover:bg-blue-700 transition-colors flex items-center justify-center"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              {t.return}
            </button>
          </div>

          {/* Language Toggle */}
          <div className="flex justify-center space-x-2">
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
