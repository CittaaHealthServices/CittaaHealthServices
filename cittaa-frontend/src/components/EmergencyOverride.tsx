import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, ArrowLeft } from 'lucide-react'

export default function EmergencyOverride() {
  const [overrideCode, setOverrideCode] = useState(['', '', '', '', '', ''])
  const [reason, setReason] = useState('')
  const [duration, setDuration] = useState('30')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()

  const handleCodeChange = (index: number, value: string) => {
    if (value.length <= 1 && /^\d*$/.test(value)) {
      const newCode = [...overrideCode]
      newCode[index] = value
      setOverrideCode(newCode)
      
      if (value && index < 5) {
        const nextInput = document.getElementById(`code-${index + 1}`)
        nextInput?.focus()
      }
    }
  }

  const handleGrantAccess = async () => {
    const code = overrideCode.join('')
    if (code.length !== 6) {
      alert('Please enter a complete 6-digit override code.')
      return
    }

    if (!reason) {
      alert('Please select a reason for the override.')
      return
    }

    setIsLoading(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      alert(`Emergency override granted for ${duration} minutes. Child device access has been temporarily unrestricted.`)
      navigate('/parent-dashboard')
    } catch {
      alert('Failed to grant override. Please check your code and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    navigate('/parent-dashboard')
  }

  const emergencyReasons = [
    { value: 'medical', label: 'Medical Emergency', icon: '🏥' },
    { value: 'educational', label: 'Educational Requirement', icon: '📚' },
    { value: 'family', label: 'Family Communication', icon: '👨‍👩‍👧‍👦' },
    { value: 'technical', label: 'Technical Support', icon: '🔧' }
  ]

  const durationOptions = [
    { value: '30', label: '30 min' },
    { value: '60', label: '1 hour' },
    { value: '120', label: '2 hours' },
    { value: 'custom', label: 'Custom' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-100 via-orange-50 to-yellow-50 p-4 flex items-center justify-center">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-3xl shadow-2xl p-8 animate-slide-in">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mx-auto w-24 h-24 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center mb-4 festival-glow animate-pulse-safe">
              <AlertTriangle className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">🆘 Emergency Parent Access</h1>
          </div>

          {/* Child Info */}
          <div className="bg-gray-50 rounded-xl p-4 mb-6">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Child:</span>
                <span className="font-medium text-gray-800">Aarav Sharma</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Device:</span>
                <span className="font-medium text-gray-800">Family Tablet</span>
              </div>
            </div>
          </div>

          {/* Override Code Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Emergency Code Required
            </label>
            <div className="flex space-x-2 justify-center">
              {overrideCode.map((digit, index) => (
                <input
                  key={index}
                  id={`code-${index}`}
                  type="text"
                  value={digit}
                  onChange={(e) => handleCodeChange(index, e.target.value)}
                  className="w-12 h-12 text-center text-xl font-bold border-2 border-gray-300 rounded-lg focus:border-red-500 focus:outline-none"
                  maxLength={1}
                />
              ))}
            </div>
          </div>

          {/* Reason Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Reason for Override:
            </label>
            <div className="space-y-2">
              {emergencyReasons.map((reasonOption) => (
                <label key={reasonOption.value} className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="reason"
                    value={reasonOption.value}
                    checked={reason === reasonOption.value}
                    onChange={(e) => setReason(e.target.value)}
                    className="mr-3 text-red-600 focus:ring-red-500"
                  />
                  <span className="mr-2">{reasonOption.icon}</span>
                  <span className="text-gray-700">{reasonOption.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Duration Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Duration:
            </label>
            <div className="grid grid-cols-2 gap-2">
              {durationOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setDuration(option.value)}
                  className={`py-2 px-4 rounded-lg border-2 transition-colors ${
                    duration === option.value
                      ? 'border-red-500 bg-red-50 text-red-700'
                      : 'border-gray-300 hover:border-gray-400 text-gray-700'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={handleGrantAccess}
              disabled={isLoading || overrideCode.join('').length !== 6 || !reason}
              className="w-full bg-red-600 hover:bg-red-700 text-white rounded-xl py-4 px-6 font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-2"></div>
                  Granting Access...
                </div>
              ) : (
                'Grant Temporary Access'
              )}
            </button>
            
            <button
              onClick={handleCancel}
              className="w-full bg-gray-600 hover:bg-gray-700 text-white rounded-xl py-3 px-6 font-medium transition-colors flex items-center justify-center"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Cancel
            </button>
          </div>

          {/* Warning Notice */}
          <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-xl p-4">
            <div className="flex items-start">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" />
              <div className="text-sm text-yellow-800">
                <strong>Warning:</strong> Emergency override will temporarily disable all parental controls. 
                Use only in genuine emergencies. All activity will be logged and reviewed.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
