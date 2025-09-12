import { useState } from 'react'

export default function CrossDeviceSync() {
  const [status] = useState([
    { name: 'Riya iPad', state: 'Synced' },
    { name: 'Riya Android', state: 'Pending' },
  ])

  return (
    <div className="min-h-screen bg-[var(--cittaa-bg)] p-6">
      <div className="max-w-3xl mx-auto bg-white rounded-2xl p-6 shadow">
        <h1 className="text-2xl font-bold text-[var(--cittaa-text)] mb-4">Cross-Device Sync</h1>
        <div className="grid gap-3">
          {status.map((d) => (
            <div key={d.name} className="flex items-center justify-between border rounded-lg p-3">
              <div className="font-medium">{d.name}</div>
              <div className={`px-3 py-1 rounded-full text-sm ${d.state === 'Synced' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>{d.state}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
