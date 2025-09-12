import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, Fingerprint } from 'lucide-react'
import { childLogin } from '../services/api'

import type { User } from '../types'

interface ChildPasswordEntryProps {
  onLogin: (user: User) => void
}

export default function ChildPasswordEntry({ onLogin }: ChildPasswordEntryProps) {
  const [password, setPassword] = useState('')
  const [language, setLanguage] = useState('english')
  const [isLoading, setIsLoading] = useState(false)
  const [showBiometric, setShowBiometric] = useState(false)
  const navigate = useNavigate()

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const { data } = await childLogin({
        password,
        biometric_data: showBiometric ? 'fingerprint_verified' : null,
      })
      onLogin(data)
      navigate('/child-dashboard')
    } catch {
      alert('Invalid password or connection issue.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleBiometricScan = () => {
    setShowBiometric(true)
    setTimeout(() => {
      alert('Biometric verification successful!')
    }, 1500)
  }

  const translations = {
    english: {
      title: 'CITTAA Safe Zone Activation',
      subtitle: 'Enter Your Secure Password:',
      biometric: 'Biometric Scan',
      activate: 'Activate Safe Zone',
      language: 'Language:'
    },
    hindi: {
      title: 'सिट्टा सुरक्षित क्षेत्र सक्रियण',
      subtitle: 'अपना सुरक्षित पासवर्ड दर्ज करें:',
      biometric: 'बायोमेट्रिक स्कैन',
      activate: 'सुरक्षित क्षेत्र सक्रिय करें',
      language: 'भाषा:'
    }
  }

  const t = translations[language as keyof typeof translations]

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl p-8 animate-slide-in">
          <div className="text-center mb-8">
            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4 festival-glow">
              <Shield className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">{t.title}</h1>
          </div>

          <form onSubmit={handlePasswordSubmit} className="space-y-6">
            <div className="text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-orange-400 to-pink-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
                  <span className="text-2xl">👦</span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t.subtitle}
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-[#8B5A96] focus:outline-none text-lg tracking-widest"
                placeholder="●●●●●●●●●●●●●●●●●●●●●●●"
                required
              />
            </div>

            <button
              type="button"
              onClick={handleBiometricScan}
              className={`w-full py-3 px-4 rounded-xl border-2 border-dashed transition-all duration-300 ${
                showBiometric 
                  ? 'border-green-500 bg-green-50 text-green-700' 
                  : 'border-gray-300 hover:border-[#7BB3A8] text-gray-600'
              }`}
            >
              <Fingerprint className="w-6 h-6 mx-auto mb-1" />
              <span className="text-sm font-medium">{t.biometric}</span>
            </button>

            <button
              type="submit"
              disabled={isLoading || !password}
              className="w-full cittaa-primary py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-300 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed animate-bounce-gentle"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-2"></div>
                  Activating...
                </div>
              ) : (
                t.activate
              )}
            </button>

            <div className="flex items-center justify-center space-x-4 pt-4">
              <span className="text-sm text-gray-600">{t.language}</span>
              <button
                type="button"
                onClick={() => setLanguage('hindi')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  language === 'hindi' ? 'bg-[#7BB3A8] text-white' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                हिंदी
              </button>
              <button
                type="button"
                onClick={() => setLanguage('english')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  language === 'english' ? 'bg-[#7BB3A8] text-white' : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                English
              </button>
            </div>
          </form>

          <div className="mt-8 text-center">
            <button className="flex items-center justify-center mx-auto text-red-600 hover:text-red-700 font-medium">
              <span className="text-2xl mr-2">🆘</span>
              Emergency Parent Call
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
