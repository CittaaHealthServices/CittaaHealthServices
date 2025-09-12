import { useState } from 'react'
import { downloadProfileByToken } from '../services/api'

export default function ProfileDownloadManager() {
  const [token, setToken] = useState('')
  const [loading, setLoading] = useState(false)

  const onDownload = async () => {
    setLoading(true)
    try {
      const res = await downloadProfileByToken(token)
      const cd = (res.headers && (res.headers['content-disposition'] as string | undefined)) || ''
      const filename = /filename="([^"]+)"/.exec(cd)?.[1] || 'CITTAA_profile'
      const blob = new Blob([res.data])
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
      alert('Profile downloaded. Continue to activation.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--cittaa-bg)] p-6">
      <div className="max-w-xl mx-auto bg-white rounded-2xl p-6 shadow">
        <h1 className="text-2xl font-bold text-[var(--cittaa-text)] mb-4">Download Mobile Profile</h1>
        <input value={token} onChange={(e) => setToken(e.target.value)} placeholder="Profile token" className="border rounded-lg p-3 w-full mb-3" />
        <button onClick={onDownload} disabled={!token || loading} className="w-full cittaa-primary py-3 rounded-lg">{loading ? 'Downloading…' : 'Download'}</button>
      </div>
    </div>
  )
}
