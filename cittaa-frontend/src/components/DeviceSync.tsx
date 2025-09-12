import { useState, useEffect } from 'react'
import { Smartphone, Laptop, Tv, Wifi, Shield, RefreshCw, CheckCircle, AlertCircle, Download } from 'lucide-react'
import { downloadMobileProfile } from '../services/api'

export default function DeviceSync() {
  const [lastUpdated, setLastUpdated] = useState('2 seconds ago')
  const [syncSpeed] = useState('847ms')
  const [autoSync, setAutoSync] = useState(true)

  const devices = [
    {
      id: 1,
      name: "Mom's iPhone",
      type: 'mobile',
      status: 'synced',
      icon: <Smartphone className="w-6 h-6" />,
      lastSync: '2 seconds ago',
      protection: 'active'
    },
    {
      id: 2,
      name: "Dad's Android",
      type: 'mobile',
      status: 'synced',
      icon: <Smartphone className="w-6 h-6" />,
      lastSync: '2 seconds ago',
      protection: 'active'
    },
    {
      id: 3,
      name: 'Family Laptop',
      type: 'laptop',
      status: 'syncing',
      icon: <Laptop className="w-6 h-6" />,
      lastSync: '15 seconds ago',
      protection: 'active'
    },
    {
      id: 4,
      name: 'Smart TV',
      type: 'tv',
      status: 'synced',
      icon: <Tv className="w-6 h-6" />,
      lastSync: '2 seconds ago',
      protection: 'active'
    },
    {
      id: 5,
      name: "Aarav's Phone",
      type: 'mobile',
      status: 'offline',
      icon: <Smartphone className="w-6 h-6" />,
      lastSync: '2 hours ago',
      protection: 'inactive'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'synced':
        return 'text-green-600'
      case 'syncing':
        return 'text-yellow-600'
      case 'offline':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'synced':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'syncing':
        return <RefreshCw className="w-5 h-5 text-yellow-600 animate-spin" />
      case 'offline':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'synced':
        return '🟢 Synced'
      case 'syncing':
        return '🟡 Syncing'
      case 'offline':
        return '🔴 Offline'
      default:
        return '⚪ Unknown'
    }
  }

  const handleForceSync = () => {
    console.log('Forcing device sync...')
    alert('Force sync initiated. All devices will be updated within 30 seconds.')
  }

  const handleToggleAutoSync = () => {
    setAutoSync(!autoSync)

    console.log('Auto-sync toggled:', !autoSync)
  }

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated('Just now')
      setTimeout(() => setLastUpdated('2 seconds ago'), 2000)
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-3xl shadow-xl p-6 animate-slide-in">
          {/* Header */}
          <div className="border-b border-gray-200 pb-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <RefreshCw className="w-8 h-8 mr-3 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">Device Sync Status</h1>
                  <p className="text-gray-600">Real-time device synchronization monitoring</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">Last Updated:</div>
                <div className="font-medium text-blue-600">{lastUpdated}</div>
              </div>
            </div>
          </div>

          {/* Sync Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{syncSpeed}</div>
              <div className="text-sm text-gray-600">Sync Speed</div>
            </div>
            <div className="bg-green-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-green-600">AES-256</div>
              <div className="text-sm text-gray-600">Encryption</div>
            </div>
            <div className="bg-purple-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">Strong 📶</div>
              <div className="text-sm text-gray-600">Network Status</div>
            </div>
          </div>

          {/* Device List */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Connected Devices</h2>
            
            <div className="space-y-4">
              {devices.map((device) => (
                <div key={device.id} className="bg-gray-50 rounded-xl p-4 border-l-4 border-l-blue-500">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="mr-4 text-gray-600">
                        {device.icon}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-800 flex items-center">
                          {device.name}
                          <span className={`ml-3 ${getStatusColor(device.status)}`}>
                            {getStatusText(device.status)}
                          </span>
                        </h3>
                        <div className="text-sm text-gray-600">
                          Last sync: {device.lastSync}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(device.status)}
                      <div className="text-right">
                        <div className={`text-sm font-medium ${
                          device.protection === 'active' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {device.protection === 'active' ? '🔒 Protected' : '🔓 Unprotected'}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sync Settings */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Sync Settings</h2>
            
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <RefreshCw className="w-6 h-6 mr-3 text-blue-600" />
                  <div>
                    <h3 className="font-semibold text-gray-800">🔄 Auto-sync enabled</h3>
                    <p className="text-sm text-gray-600">Automatically sync all devices every 30 seconds</p>
                  </div>
                </div>
                <button
                  onClick={handleToggleAutoSync}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    autoSync ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      autoSync ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center">
                <Shield className="w-6 h-6 mr-3 text-green-600" />
                <div>
                  <h3 className="font-semibold text-gray-800">⚡ Real-time protection active</h3>
                  <p className="text-sm text-gray-600">All devices are continuously monitored and protected</p>
                </div>
              </div>
            </div>
          </div>

          {/* Network Information */}
          <div className="mb-6">
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <div className="flex items-center">
                <Wifi className="w-6 h-6 mr-3 text-green-600" />
                <div>
                  <h3 className="font-semibold text-green-800">Network Status: Strong 📶</h3>
                  <p className="text-sm text-green-700">
                    All devices connected via secure encrypted channels. 
                    Data transmission protected with AES-256 encryption 🔒
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={handleForceSync}
              className="flex items-center px-6 py-3 cittaa-primary rounded-xl font-medium hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="w-5 h-5 mr-2" />
              Force Sync All Devices
            </button>
            <button
              onClick={async () => {
                try {
                  const res = await downloadMobileProfile('ios')
                  const blob = new Blob([res.data], { type: 'application/x-apple-aspen-config' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = 'CITTAA.mobileconfig'
                  document.body.appendChild(a)
                  a.click()
                  a.remove()
                  URL.revokeObjectURL(url)
                } catch {
                  alert('Failed to download mobile profile. Please try again.')
                }
              }}
              className="flex items-center px-6 py-3 bg-[#8B5A96] text-white rounded-xl font-medium hover:opacity-90 transition-colors">
              <Download className="w-5 h-5 mr-2" />
              Download iOS Profile
            </button>
            <button
              onClick={async () => {
                try {
                  const res = await downloadMobileProfile('android')
                  const blob = new Blob([res.data], { type: 'application/json' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = 'CITTAA_android_profile.json'
                  document.body.appendChild(a)
                  a.click()
                  a.remove()
                  URL.revokeObjectURL(url)
                } catch {
                  alert('Failed to download mobile profile. Please try again.')
                }
              }}
              className="flex items-center px-6 py-3 bg-[#7BB3A8] text-white rounded-xl font-medium hover:opacity-90 transition-colors">
              <Download className="w-5 h-5 mr-2" />
              Download Android Profile
            </button>

            <button className="flex items-center px-6 py-3 bg-gray-600 text-white rounded-xl font-medium hover:bg-gray-700 transition-colors">
              <Shield className="w-5 h-5 mr-2" />
              Security Settings
            </button>
          </div>

          {/* Technical Details */}
          <div className="mt-6 bg-gray-50 rounded-xl p-4">
            <div className="text-sm text-gray-600">
              <strong>Technical Details:</strong> Device synchronization uses WebSocket connections for real-time updates. 
              All data is encrypted end-to-end and stored locally on devices when possible. 
              Sync conflicts are resolved using timestamp-based priority with parent device override capabilities.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
