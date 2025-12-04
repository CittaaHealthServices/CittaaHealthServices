import { 
  Users, 
  Mic, 
  TrendingUp, 
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'

const statsCards = [
  { 
    title: 'Total Users', 
    value: '12,847', 
    change: '+12.5%', 
    isPositive: true,
    icon: Users,
    color: 'bg-blue-500'
  },
  { 
    title: 'Voice Analyses', 
    value: '45,231', 
    change: '+8.2%', 
    isPositive: true,
    icon: Mic,
    color: 'bg-green-500'
  },
  { 
    title: 'Active Subscriptions', 
    value: '3,456', 
    change: '+15.3%', 
    isPositive: true,
    icon: TrendingUp,
    color: 'bg-purple-500'
  },
  { 
    title: 'AI Accuracy', 
    value: '87.2%', 
    change: '-0.3%', 
    isPositive: false,
    icon: Activity,
    color: 'bg-orange-500'
  },
]

const analysisData = [
  { name: 'Mon', analyses: 1200, users: 340 },
  { name: 'Tue', analyses: 1400, users: 380 },
  { name: 'Wed', analyses: 1100, users: 320 },
  { name: 'Thu', analyses: 1600, users: 420 },
  { name: 'Fri', analyses: 1800, users: 480 },
  { name: 'Sat', analyses: 900, users: 250 },
  { name: 'Sun', analyses: 700, users: 200 },
]

const riskDistribution = [
  { name: 'Low Risk', value: 65, color: '#4CAF50' },
  { name: 'Moderate', value: 25, color: '#FFC107' },
  { name: 'High Risk', value: 8, color: '#FF9800' },
  { name: 'Critical', value: 2, color: '#E53935' },
]

const platformData = [
  { name: 'iOS', users: 5234 },
  { name: 'Android', users: 4892 },
  { name: 'Watch', users: 1823 },
  { name: 'Web', users: 898 },
]

const recentActivities = [
  { id: 1, type: 'approval', message: 'New patient registration pending approval', time: '5 min ago', status: 'pending' },
  { id: 2, type: 'analysis', message: 'High risk detected for user #12847', time: '12 min ago', status: 'alert' },
  { id: 3, type: 'subscription', message: 'New Premium Plus subscription', time: '25 min ago', status: 'success' },
  { id: 4, type: 'coupon', message: 'Coupon CITTAA50 redeemed', time: '1 hour ago', status: 'success' },
  { id: 5, type: 'system', message: 'ML model updated to v2.3.1', time: '2 hours ago', status: 'info' },
]

export function Dashboard() {
  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back! Here's what's happening with Vocalysis.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statsCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.title} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 card-hover">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <div className={`flex items-center mt-2 text-sm ${stat.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                    {stat.isPositive ? (
                      <ArrowUpRight className="w-4 h-4 mr-1" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4 mr-1" />
                    )}
                    {stat.change} from last month
                  </div>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Analysis Trend */}
        <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analysisData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="analyses" 
                stroke="#2E7D32" 
                strokeWidth={2}
                dot={{ fill: '#2E7D32' }}
              />
              <Line 
                type="monotone" 
                dataKey="users" 
                stroke="#1565C0" 
                strokeWidth={2}
                dot={{ fill: '#1565C0' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-4">
            {riskDistribution.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-xs text-gray-600">{item.name}: {item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Platform Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Users by Platform</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={platformData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Bar dataKey="users" fill="#2E7D32" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${
                  activity.status === 'success' ? 'bg-green-100' :
                  activity.status === 'alert' ? 'bg-red-100' :
                  activity.status === 'pending' ? 'bg-yellow-100' :
                  'bg-blue-100'
                }`}>
                  {activity.status === 'success' ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : activity.status === 'alert' ? (
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                  ) : activity.status === 'pending' ? (
                    <Clock className="w-4 h-4 text-yellow-600" />
                  ) : (
                    <Activity className="w-4 h-4 text-blue-600" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
