import { useState } from 'react'
import { startPasswordRecovery, verifySecurityQuestion, verifyEmergencyOtp, resetChildPassword } from '../services/api'

type Step = 'email' | 'security' | 'otp' | 'reset' | 'done'

export default function ForgotPassword() {
  const [step, setStep] = useState<Step>('email')
  const [email, setEmail] = useState('')
  const [answer, setAnswer] = useState('')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const next = (s: Step) => setStep(s)

  const onEmail = async () => {
    setLoading(true)
    try {
      await startPasswordRecovery(email)
      next('security')
    } finally {
      setLoading(false)
    }
  }

  const onSecurity = async () => {
    setLoading(true)
    try {
      await verifySecurityQuestion(answer)
      next('otp')
    } finally {
      setLoading(false)
    }
  }

  const onOtp = async () => {
    setLoading(true)
    try {
      await verifyEmergencyOtp(phone, otp)
      next('reset')
    } finally {
      setLoading(false)
    }
  }

  const onReset = async () => {
    setLoading(true)
    try {
      await resetChildPassword(newPassword, true)
      next('done')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--cittaa-bg)] p-4">
      <div className="bg-white rounded-2xl p-6 shadow-xl max-w-md w-full">
        <div className="text-2xl font-bold text-[var(--cittaa-text)] mb-4">Forgot Password</div>

        {step === 'email' && (
          <div className="space-y-3">
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Parent email"
              className="w-full border rounded-lg p-3"
            />
            <button onClick={onEmail} disabled={loading || !email} className="w-full py-3 rounded-md cittaa-primary">
              {loading ? 'Verifying…' : 'Verify Email'}
            </button>
          </div>
        )}

        {step === 'security' && (
          <div className="space-y-3">
            <input
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Security answer"
              className="w-full border rounded-lg p-3"
            />
            <button onClick={onSecurity} disabled={loading || !answer} className="w-full py-3 rounded-md cittaa-primary">
              {loading ? 'Checking…' : 'Submit Answer'}
            </button>
          </div>
        )}

        {step === 'otp' && (
          <div className="space-y-3">
            <input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Emergency contact phone"
              className="w-full border rounded-lg p-3"
            />
            <input
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              placeholder="OTP"
              className="w-full border rounded-lg p-3"
            />
            <button onClick={onOtp} disabled={loading || !phone || !otp} className="w-full py-3 rounded-md cittaa-primary">
              {loading ? 'Verifying…' : 'Verify OTP'}
            </button>
          </div>
        )}

        {step === 'reset' && (
          <div className="space-y-3">
            <input
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="New password"
              type="password"
              className="w-full border rounded-lg p-3"
            />
            <button onClick={onReset} disabled={loading || !newPassword} className="w-full py-3 rounded-md cittaa-primary">
              {loading ? 'Resetting…' : 'Reset Password'}
            </button>
          </div>
        )}

        {step === 'done' && (
          <div className="text-center">
            <div className="text-green-600 font-medium mb-2">Password reset successful</div>
            <div className="text-sm text-[var(--cittaa-gray)]">You can now log in with your new password.</div>
          </div>
        )}
      </div>
    </div>
  )
}
