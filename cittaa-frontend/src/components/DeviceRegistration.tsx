import { useMemo, useState } from 'react'
import { activateMobileProfile } from '../services/api'

function fingerprint() {
  const data = navigator.userAgent + '|' + screen.width + 'x' + screen.height + '|' + Intl.DateTimeFormat().resolvedOptions().timeZone
  let hash = 0
  for (let i = 0; i < data.length; i++) hash = (hash << 5) - hash + data.charCodeAt(i) | 0
  return String(hash)
}

export default function DeviceRegistration() {
  const [childId, setChildId] = useState('')
  const [platform, setPlatform] = useState<'ios' | 'android'>('ios')
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const fp = useMemo(() => fingerprint(), [])

  const onActivate = async () => {
    setLoading(true)
    try {
      await activateMobileProfile({ child_id: childId, platform, device_fingerprint: fp, biometric_setup: true })
      setDone(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--cittaa-bg)] p-6">
      <div className="max-w-xl mx-auto bg-white rounded-2xl p-6 shadow">
        <h1 className="text-2xl font-bold text-[var(--cittaa-text)] mb-4">Activate Profile on Device</h1>
        <input value={childId} onChange={(e) => setChildId(e.target.value)} placeholder="Child ID" className="border rounded-lg p-3 w-full mb-3" />
        <div className="flex gap-2 mb-3">
          <button onClick={() => setPlatform('ios')} className={`px-4 py-2 rounded ${platform === 'ios' ? 'bg-[#8B5A96] text-white' : 'bg-gray-100'}`}>iOS</button>
          <button onClick={() => setPlatform('android')} className={`px-4 py-2 rounded ${platform === 'android' ? 'bg-[#7BB3A8] text-white' : 'bg-gray-100'}`}>Android</button>
        </div>
        <div className="text-xs text-gray-500 mb-4">Device fingerprint: {fp}</div>
        <button onClick={onActivate} disabled={!childId || loading} className="w-full cittaa-primary py-3 rounded-lg">{loading ? 'Activating…' : 'Activate'}</button>
        {done && <div className="mt-3 text-green-600">Device registered and profile activated.</div>}
      </div>
    </div>
  )
}
