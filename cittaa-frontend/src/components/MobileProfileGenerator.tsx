import { useState } from 'react'
import { generateMobileProfile } from '../services/api'

export default function MobileProfileGenerator() {
  const [childId, setChildId] = useState('')
  const [platform, setPlatform] = useState<'ios' | 'android'>('ios')
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const onGenerate = async () => {
    setLoading(true)
    try {
      const { data } = await generateMobileProfile(childId, platform)
      setToken(data.profile_token)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--cittaa-bg)] p-6">
      <div className="max-w-xl mx-auto bg-white rounded-2xl p-6 shadow">
        <h1 className="text-2xl font-bold text-[var(--cittaa-text)] mb-4">Generate Mobile Profile</h1>
        <input value={childId} onChange={(e) => setChildId(e.target.value)} placeholder="Child ID" className="border rounded-lg p-3 w-full mb-3" />
        <div className="flex gap-2 mb-4">
          <button onClick={() => setPlatform('ios')} className={`px-4 py-2 rounded ${platform === 'ios' ? 'bg-[#8B5A96] text-white' : 'bg-gray-100'}`}>iOS</button>
          <button onClick={() => setPlatform('android')} className={`px-4 py-2 rounded ${platform === 'android' ? 'bg-[#7BB3A8] text-white' : 'bg-gray-100'}`}>Android</button>
        </div>
        <button onClick={onGenerate} disabled={!childId || loading} className="w-full cittaa-primary py-3 rounded-lg">{loading ? 'Generating…' : 'Generate Profile Token'}</button>
        {token && (
          <div className="mt-4 p-3 bg-gray-50 rounded">
            <div className="text-sm text-gray-600 mb-1">Profile token (valid ~15 min):</div>
            <div className="font-mono break-all">{token}</div>
          </div>
        )}
      </div>
    </div>
  )
}
