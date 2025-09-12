import { useState } from 'react'
import { BarChart3, Shield, Download, Settings } from 'lucide-react'

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('week')

  const weeklyData = {
    educationalTime: { value: 18, total: 24, percentage: 75 },
    recreationTime: { value: 4.8, total: 24, percentage: 20 },
    securityEvents: {
      blockedAttempts: 12,
      vpnBlocks: 3,
      contentFilters: 9
    },
    topCategories: [
      { name: 'Mathematics', percentage: 35 },
      { name: 'Science', percentage: 28 },
      { name: 'English', percentage: 22 },
      { name: 'Social Studies', percentage: 15 }
    ]
  }

  const children = [
    {
      name: 'Aarav',
      age: 12,
      screenTime: '2h 15m',
      educationalPercentage: 80,
      blockedAttempts: 2,
      focusScore: 87
    },
    {
      name: 'Priya',
      age: 8,
      screenTime: '1h 30m',
      educationalPercentage: 90,
      blockedAttempts: 1,
      focusScore: 92
    }
  ]

  const handleDownloadReport = () => {
    console.log('Downloading analytics report...')
    alert('Analytics report downloaded successfully!')
  }

  const handleSettings = () => {
    console.log('Opening analytics settings...')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-3xl shadow-xl p-6 animate-slide-in">
          {/* Header */}
          <div className="border-b border-gray-200 pb-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <BarChart3 className="w-8 h-8 mr-3 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">📈 The Sharma Family Analytics</h1>
                  <p className="text-gray-600">Comprehensive family digital wellness report</p>
                </div>
              </div>
              <div className="flex space-x-2">
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                >
                  <option value="day">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </select>
              </div>
            </div>
          </div>

          {/* Time Summary */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">📅 This Week's Summary</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Educational Time */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                    🎓 Educational Time
                  </h3>
                  <div className="text-2xl font-bold text-green-600">
                    {weeklyData.educationalTime.percentage}%
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
                  <div 
                    className="bg-green-500 h-4 rounded-full transition-all duration-1000"
                    style={{ width: `${weeklyData.educationalTime.percentage}%` }}
                  ></div>
                </div>
                <div className="text-sm text-gray-600">
                  {weeklyData.educationalTime.value}h/{weeklyData.educationalTime.total}h
                </div>
              </div>

              {/* Recreation Time */}
              <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                    🎮 Recreation Time
                  </h3>
                  <div className="text-2xl font-bold text-orange-600">
                    {weeklyData.recreationTime.percentage}%
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
                  <div 
                    className="bg-orange-500 h-4 rounded-full transition-all duration-1000"
                    style={{ width: `${weeklyData.recreationTime.percentage}%` }}
                  ></div>
                </div>
                <div className="text-sm text-gray-600">
                  {weeklyData.recreationTime.value}h/{weeklyData.recreationTime.total}h
                </div>
              </div>
            </div>
          </div>

          {/* Security Events */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Shield className="w-6 h-6 mr-2 text-red-600" />
              🛡️ Security Events
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
                <div className="text-3xl font-bold text-red-600">{weeklyData.securityEvents.blockedAttempts}</div>
                <div className="text-sm text-gray-600">Blocked attempts</div>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 text-center">
                <div className="text-3xl font-bold text-orange-600">{weeklyData.securityEvents.vpnBlocks}</div>
                <div className="text-sm text-gray-600">VPN blocks</div>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-center">
                <div className="text-3xl font-bold text-yellow-600">{weeklyData.securityEvents.contentFilters}</div>
                <div className="text-sm text-gray-600">Content filters</div>
              </div>
            </div>
          </div>

          {/* Top Educational Categories */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">📚 Top Educational Categories</h2>
            
            <div className="space-y-3">
              {weeklyData.topCategories.map((category, index) => (
                <div key={index} className="bg-gray-50 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-800">{index + 1}. {category.name}</span>
                    <span className="text-blue-600 font-semibold">{category.percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-1000"
                      style={{ width: `${category.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Individual Child Analytics */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">👨‍👩‍👧‍👦 Individual Child Analytics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {children.map((child, index) => (
                <div key={index} className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-blue-500 rounded-full flex items-center justify-center mr-3">
                        <span className="text-white font-bold">{child.name[0]}</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-800">{child.name}</h3>
                        <p className="text-sm text-gray-600">Age {child.age}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-purple-600">{child.focusScore}%</div>
                      <div className="text-xs text-gray-600">Focus Score</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Screen Time:</span>
                      <span className="font-medium">{child.screenTime}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Educational:</span>
                      <span className="font-medium text-green-600">{child.educationalPercentage}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Blocked Attempts:</span>
                      <span className="font-medium text-red-600">{child.blockedAttempts}</span>
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all duration-1000"
                        style={{ width: `${child.educationalPercentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={handleDownloadReport}
              className="flex items-center px-6 py-3 cittaa-primary rounded-xl font-medium hover:bg-blue-700 transition-colors"
            >
              <Download className="w-5 h-5 mr-2" />
              Download Report
            </button>
            <button
              onClick={handleSettings}
              className="flex items-center px-6 py-3 bg-gray-600 text-white rounded-xl font-medium hover:bg-gray-700 transition-colors"
            >
              <Settings className="w-5 h-5 mr-2" />
              Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
