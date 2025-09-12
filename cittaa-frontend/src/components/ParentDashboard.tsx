import { useState } from 'react'
import { Users, Shield, AlertTriangle, BarChart3, Settings, Eye, Ban, CheckCircle } from 'lucide-react'

export default function ParentDashboard() {
  const [children] = useState([
    {
      id: 1,
      name: 'Aarav',
      age: 12,
      status: 'online',
      device: "Mom's Phone",
      activity: 'NCERT Math',
      screenTime: '2h 15m',
      safetyStatus: 'safe',
      blockedAttempts: 0
    },
    {
      id: 2,
      name: 'Priya',
      age: 8,
      status: 'blocked_attempt',
      device: 'Family Tablet',
      activity: 'VPN Installation',
      screenTime: '1h 30m',
      safetyStatus: 'alert',
      blockedAttempts: 3,
      lastBlocked: '2 minutes ago'
    }
  ])

  const familyStats = {
    totalScreenTime: '18h',
    educationalTime: '75%',
    blockedAttempts: 12,
    vpnBlocks: 3
  }

  const handleViewDetails = (childId: number) => {
    console.log('Viewing details for child:', childId)
  }

  const handleOverride = (childId: number) => {
    console.log('Override for child:', childId)
  }

  const handleReview = (childId: number) => {
    console.log('Review blocked content for child:', childId)
  }

  const handleAllow = (childId: number) => {
    console.log('Allow content for child:', childId)
  }

  const handleRestrict = (childId: number) => {
    console.log('Restrict content for child:', childId)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-3xl shadow-xl p-6 animate-slide-in">
          {/* Header */}
          <div className="border-b border-gray-200 pb-4 mb-6">
            <h1 className="text-2xl font-bold text-gray-800">CITTAA Family Dashboard</h1>
            <p className="text-gray-600">Family: The Sharmas</p>
          </div>

          {/* Family Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{familyStats.totalScreenTime}</div>
              <div className="text-sm text-gray-600">Total Screen Time</div>
            </div>
            <div className="bg-green-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{familyStats.educationalTime}</div>
              <div className="text-sm text-gray-600">Educational Time</div>
            </div>
            <div className="bg-orange-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">{familyStats.blockedAttempts}</div>
              <div className="text-sm text-gray-600">Blocked Attempts</div>
            </div>
            <div className="bg-red-50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-red-600">{familyStats.vpnBlocks}</div>
              <div className="text-sm text-gray-600">VPN Blocks</div>
            </div>
          </div>

          {/* Active Children */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Users className="w-6 h-6 mr-2 text-blue-600" />
              👨‍👩‍👧‍👦 Active Children Today
            </h2>

            <div className="space-y-4">
              {children.map((child) => (
                <div key={child.id} className="bg-gray-50 rounded-xl p-4 border-l-4 border-l-blue-500">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        child.status === 'online' ? 'bg-green-500' : 
                        child.status === 'blocked_attempt' ? 'bg-red-500' : 'bg-gray-400'
                      }`}></div>
                      <h3 className="font-semibold text-gray-800">
                        {child.name} ({child.age}) 
                        {child.status === 'online' && <span className="text-green-600 ml-2">🟢 Online {child.screenTime}</span>}
                        {child.status === 'blocked_attempt' && <span className="text-red-600 ml-2">🔴 Blocked Attempt</span>}
                      </h3>
                    </div>
                    <div className="flex items-center space-x-2">
                      {child.safetyStatus === 'safe' && <CheckCircle className="w-5 h-5 text-green-500" />}
                      {child.safetyStatus === 'alert' && <AlertTriangle className="w-5 h-5 text-red-500" />}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div>
                      <span className="text-sm text-gray-600">Device: </span>
                      <span className="font-medium">{child.device}</span>
                    </div>
                    <div>
                      <span className="text-sm text-gray-600">Activity: </span>
                      <span className="font-medium">{child.activity}</span>
                    </div>
                  </div>

                  {child.status === 'online' && (
                    <div className="mb-3">
                      <span className="text-sm text-gray-600">Status: </span>
                      <span className="text-green-600 font-medium">All Safe ✅</span>
                    </div>
                  )}

                  {child.status === 'blocked_attempt' && (
                    <div className="mb-3 space-y-1">
                      <div>
                        <span className="text-sm text-gray-600">Blocked: </span>
                        <span className="text-red-600 font-medium">{child.activity}</span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-600">Time: </span>
                        <span className="font-medium">{child.lastBlocked}</span>
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleViewDetails(child.id)}
                      className="flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View Details
                    </button>
                    <button
                      onClick={() => handleOverride(child.id)}
                      className="flex items-center px-3 py-1 bg-orange-100 text-orange-700 rounded-lg text-sm font-medium hover:bg-orange-200 transition-colors"
                    >
                      <Shield className="w-4 h-4 mr-1" />
                      Override
                    </button>
                    {child.status === 'blocked_attempt' && (
                      <>
                        <button
                          onClick={() => handleReview(child.id)}
                          className="flex items-center px-3 py-1 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors"
                        >
                          Review
                        </button>
                        <button
                          onClick={() => handleAllow(child.id)}
                          className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors"
                        >
                          Allow
                        </button>
                        <button
                          onClick={() => handleRestrict(child.id)}
                          className="flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition-colors"
                        >
                          <Ban className="w-4 h-4 mr-1" />
                          Restrict
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button className="flex items-center px-6 py-3 cittaa-primary rounded-xl font-medium hover:bg-blue-700 transition-colors">
              <BarChart3 className="w-5 h-5 mr-2" />
              📊 Analytics
            </button>
            <button className="flex items-center px-6 py-3 bg-gray-600 text-white rounded-xl font-medium hover:bg-gray-700 transition-colors">
              <Settings className="w-5 h-5 mr-2" />
              🔧 Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
