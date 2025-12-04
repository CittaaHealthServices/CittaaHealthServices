import { 
  TrendingUp, 
  TrendingDown,
  Users,
  Activity,
  Clock,
  Target
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
  Cell,
  AreaChart,
  Area
} from 'recharts'

const monthlyData = [
  { month: 'Jul', users: 2400, analyses: 4800, revenue: 120000 },
  { month: 'Aug', users: 3200, analyses: 6400, revenue: 160000 },
  { month: 'Sep', users: 4100, analyses: 8200, revenue: 205000 },
  { month: 'Oct', users: 5800, analyses: 11600, revenue: 290000 },
  { month: 'Nov', users: 7200, analyses: 14400, revenue: 360000 },
  { month: 'Dec', users: 9100, analyses: 18200, revenue: 455000 },
  { month: 'Jan', users: 12847, analyses: 25694, revenue: 642000 },
]

const conditionDistribution = [
  { name: 'Normal', value: 45, color: '#4CAF50' },
  { name: 'Mild Anxiety', value: 25, color: '#FFC107' },
  { name: 'Moderate Anxiety', value: 12, color: '#FF9800' },
  { name: 'Depression Signs', value: 10, color: '#9C27B0' },
  { name: 'High Stress', value: 8, color: '#E53935' },
]

const accuracyData = [
  { model: 'PHQ-9', accuracy: 82, target: 85 },
  { model: 'GAD-7', accuracy: 79, target: 85 },
  { model: 'PSS', accuracy: 84, target: 85 },
  { model: 'WEMWBS', accuracy: 88, target: 85 },
  { model: 'Overall', accuracy: 87, target: 85 },
]

const hourlyUsage = [
  { hour: '00', users: 120 },
  { hour: '04', users: 45 },
  { hour: '08', users: 890 },
  { hour: '12', users: 1200 },
  { hour: '16', users: 980 },
  { hour: '20', users: 1450 },
]

const kpiCards = [
  { title: 'User Growth', value: '+32%', subtitle: 'vs last month', icon: Users, color: 'text-green-600', bgColor: 'bg-green-100', trend: 'up' },
  { title: 'Avg. Session Time', value: '4.2 min', subtitle: '+18% vs last month', icon: Clock, color: 'text-blue-600', bgColor: 'bg-blue-100', trend: 'up' },
  { title: 'Analysis Accuracy', value: '87.2%', subtitle: '-0.3% vs last month', icon: Target, color: 'text-purple-600', bgColor: 'bg-purple-100', trend: 'down' },
  { title: 'Processing Time', value: '1.8s', subtitle: '-12% vs last month', icon: Activity, color: 'text-orange-600', bgColor: 'bg-orange-100', trend: 'up' },
]

export function Analytics() {
  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Analytics & Insights</h1>
        <p className="text-gray-600 mt-1">Monitor system performance and user engagement</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {kpiCards.map((kpi) => {
          const Icon = kpi.icon
          return (
            <div key={kpi.title} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 card-hover">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-600">{kpi.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{kpi.value}</p>
                  <div className={`flex items-center mt-2 text-sm ${kpi.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                    {kpi.trend === 'up' ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    {kpi.subtitle}
                  </div>
                </div>
                <div className={`${kpi.bgColor} p-3 rounded-lg`}>
                  <Icon className={`w-6 h-6 ${kpi.color}`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Growth Chart */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User & Analysis Growth</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="users" 
                stackId="1"
                stroke="#2E7D32" 
                fill="#2E7D32"
                fillOpacity={0.3}
              />
              <Area 
                type="monotone" 
                dataKey="analyses" 
                stackId="2"
                stroke="#1565C0" 
                fill="#1565C0"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
          <div className="flex items-center justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-600" />
              <span className="text-sm text-gray-600">Users</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-600" />
              <span className="text-sm text-gray-600">Analyses</span>
            </div>
          </div>
        </div>

        {/* Condition Distribution */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Mental Health Distribution</h3>
          <div className="flex items-center">
            <ResponsiveContainer width="50%" height={250}>
              <PieChart>
                <Pie
                  data={conditionDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {conditionDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-3">
              {conditionDistribution.map((item) => (
                <div key={item.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-gray-600">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{item.value}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Model Accuracy */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Model Accuracy</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={accuracyData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" domain={[0, 100]} stroke="#9ca3af" />
              <YAxis dataKey="model" type="category" stroke="#9ca3af" width={80} />
              <Tooltip />
              <Bar dataKey="accuracy" fill="#2E7D32" radius={[0, 4, 4, 0]} />
              <Bar dataKey="target" fill="#E0E0E0" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="flex items-center justify-center gap-6 mt-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-600" />
              <span className="text-sm text-gray-600">Current Accuracy</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-300" />
              <span className="text-sm text-gray-600">Target (85%)</span>
            </div>
          </div>
        </div>

        {/* Hourly Usage */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage by Hour</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={hourlyUsage}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="hour" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="users" 
                stroke="#FF6F00" 
                strokeWidth={3}
                dot={{ fill: '#FF6F00', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-500 text-center mt-4">
            Peak usage: 8 PM - 10 PM IST
          </p>
        </div>
      </div>

      {/* Revenue & Metrics */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={monthlyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" tickFormatter={(value) => `₹${value/1000}K`} />
            <Tooltip formatter={(value: number) => [`₹${value.toLocaleString()}`, 'Revenue']} />
            <Area 
              type="monotone" 
              dataKey="revenue" 
              stroke="#7B1FA2" 
              fill="#7B1FA2"
              fillOpacity={0.2}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
        <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
          <div className="text-center">
            <p className="text-sm text-gray-600">Total Revenue (7 months)</p>
            <p className="text-2xl font-bold text-gray-900">₹22.32L</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Avg. Revenue Per User</p>
            <p className="text-2xl font-bold text-gray-900">₹1,736</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">MoM Growth</p>
            <p className="text-2xl font-bold text-green-600">+41%</p>
          </div>
        </div>
      </div>
    </div>
  )
}
