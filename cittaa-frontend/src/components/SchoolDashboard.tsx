import { useState } from 'react'
import { School, Users, AlertTriangle, BarChart3, BookOpen, Shield } from 'lucide-react'

interface SchoolDashboardProps {
  user: any
}

export default function SchoolDashboard({}: SchoolDashboardProps) {
  const [activeStudents] = useState(847)
  const [totalStudents] = useState(950)
  const [currentSubject] = useState('Mathematics')
  const [classrooms] = useState([
    {
      name: 'Class 8A',
      totalStudents: 32,
      onTask: 28,
      distracted: 3,
      offline: 1,
      focusScore: 87
    }
  ])
  const [blockedAttempts] = useState([
    { type: 'VPN access attempt', class: 'Class 9B', time: '5 min ago' },
    { type: 'Gaming site', class: 'Class 7C', time: '12 min ago' },
    { type: 'Social media', class: 'Class 10A', time: '18 min ago' }
  ])

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-3xl shadow-xl p-6 animate-slide-in">
          {/* Header */}
          <div className="border-b border-gray-200 pb-4 mb-6">
            <div className="flex items-center">
              <School className="w-8 h-8 mr-3 text-green-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Delhi Public School - CITTAA</h1>
                <p className="text-gray-600">School Administrator Dashboard</p>
              </div>
            </div>
          </div>

          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">🏫 Active Students</h3>
                  <p className="text-3xl font-bold text-green-600">{activeStudents}/{totalStudents}</p>
                </div>
                <Users className="w-12 h-12 text-green-500" />
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">📚 Current Subject</h3>
                  <p className="text-xl font-bold text-blue-600">{currentSubject}</p>
                </div>
                <BookOpen className="w-12 h-12 text-blue-500" />
              </div>
            </div>

            <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">🚨 Security Events</h3>
                  <p className="text-3xl font-bold text-orange-600">{blockedAttempts.length}</p>
                </div>
                <Shield className="w-12 h-12 text-orange-500" />
              </div>
            </div>
          </div>

          {/* Classroom Analytics */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <BarChart3 className="w-6 h-6 mr-2 text-blue-600" />
              📊 Classroom Analytics
            </h2>

            <div className="space-y-4">
              {classrooms.map((classroom, index) => (
                <div key={index} className="bg-gray-50 rounded-xl p-6 border-l-4 border-l-green-500">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-800">{classroom.name} ({classroom.totalStudents} students)</h3>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">{classroom.focusScore}%</div>
                      <div className="text-sm text-gray-600">Focus Score</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{classroom.onTask}</div>
                      <div className="text-sm text-gray-600">On Task ✅</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-600">{classroom.distracted}</div>
                      <div className="text-sm text-gray-600">Distracted ⚠️</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{classroom.offline}</div>
                      <div className="text-sm text-gray-600">Offline 🔴</div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div className="flex h-3 rounded-full overflow-hidden">
                        <div 
                          className="bg-green-500" 
                          style={{ width: `${(classroom.onTask / classroom.totalStudents) * 100}%` }}
                        ></div>
                        <div 
                          className="bg-yellow-500" 
                          style={{ width: `${(classroom.distracted / classroom.totalStudents) * 100}%` }}
                        ></div>
                        <div 
                          className="bg-red-500" 
                          style={{ width: `${(classroom.offline / classroom.totalStudents) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Blocked Attempts */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <AlertTriangle className="w-6 h-6 mr-2 text-red-600" />
              🚨 Recent Blocked Attempts
            </h2>

            <div className="space-y-3">
              {blockedAttempts.map((attempt, index) => (
                <div key={index} className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
                    <div>
                      <span className="font-medium text-gray-800">• {attempt.type}</span>
                      <span className="text-gray-600 ml-2">({attempt.class})</span>
                    </div>
                  </div>
                  <div className="text-sm text-gray-600">{attempt.time}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button className="flex items-center px-6 py-3 cittaa-primary rounded-xl font-medium hover:bg-blue-700 transition-colors">
              <Users className="w-5 h-5 mr-2" />
              Teacher Controls
            </button>
            <button className="flex items-center px-6 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors">
              <BarChart3 className="w-5 h-5 mr-2" />
              Reports
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
