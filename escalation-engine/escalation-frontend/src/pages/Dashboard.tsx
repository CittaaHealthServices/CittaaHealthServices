import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Users, Building2, GraduationCap, AlertTriangle, 
  FileText, Shield, Activity,
  AlertCircle, Clock, CheckCircle
} from 'lucide-react';
import { CITTAA_COLORS, ESCALATION_COLORS } from '@/lib/utils';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface DashboardStats {
  users: { total: number; active: number; psychologists: number };
  institutions: { total: number; active: number };
  students: { total: number; active: number };
  today: { sessions: number; date: string };
  escalations: { open: number; emergency: number; high_risk: number };
  reports_last_7_days: { daily: number; weekly: number };
}

interface EscalationStats {
  total_open_cases: number;
  emergency_cases: number;
  high_risk_cases: number;
  moderate_cases: number;
  low_cases: number;
  resolved_today: number;
  average_resolution_time_hours: number | null;
}

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [escalationStats, setEscalationStats] = useState<EscalationStats | null>(null);
  const [, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [dashboardData, escalationData] = await Promise.all([
        api.getDashboardOverview().catch(() => null),
        api.getEscalationDashboardStats().catch(() => null),
      ]);
      
      if (dashboardData) setStats(dashboardData as DashboardStats);
      if (escalationData) setEscalationStats(escalationData as EscalationStats);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const escalationPieData = escalationStats ? [
    { name: 'Emergency', value: escalationStats.emergency_cases, color: ESCALATION_COLORS.level_4_emergency },
    { name: 'High Risk', value: escalationStats.high_risk_cases, color: ESCALATION_COLORS.level_3_high },
    { name: 'Moderate', value: escalationStats.moderate_cases, color: ESCALATION_COLORS.level_2_moderate },
    { name: 'Low', value: escalationStats.low_cases, color: ESCALATION_COLORS.level_1_low },
  ].filter(d => d.value > 0) : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
            Dashboard
          </h1>
          <p className="text-gray-500 mt-1">
            Welcome back, {user?.full_name}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span 
            className="px-3 py-1 rounded-full text-sm font-medium text-white"
            style={{ backgroundColor: CITTAA_COLORS.teal }}
          >
            {user?.role?.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      {escalationStats && escalationStats.emergency_cases > 0 && (
        <Card className="border-2" style={{ borderColor: ESCALATION_COLORS.level_4_emergency }}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div 
                className="p-2 rounded-full"
                style={{ backgroundColor: `${ESCALATION_COLORS.level_4_emergency}20` }}
              >
                <AlertTriangle 
                  className="h-6 w-6" 
                  style={{ color: ESCALATION_COLORS.level_4_emergency }} 
                />
              </div>
              <div>
                <p className="font-semibold" style={{ color: ESCALATION_COLORS.level_4_emergency }}>
                  {escalationStats.emergency_cases} Emergency Case{escalationStats.emergency_cases > 1 ? 's' : ''} Require Immediate Attention
                </p>
                <p className="text-sm text-gray-500">
                  Please review and take action immediately
                </p>
              </div>
              <Button 
                className="ml-auto text-white"
                style={{ backgroundColor: ESCALATION_COLORS.level_4_emergency }}
              >
                View Cases
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Open Escalations
            </CardTitle>
            <AlertCircle className="h-5 w-5" style={{ color: ESCALATION_COLORS.level_3_high }} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
              {escalationStats?.total_open_cases || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {escalationStats?.resolved_today || 0} resolved today
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Sessions Today
            </CardTitle>
            <Activity className="h-5 w-5" style={{ color: CITTAA_COLORS.teal }} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
              {stats?.today?.sessions || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {stats?.today?.date || 'Today'}
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Active Students
            </CardTitle>
            <GraduationCap className="h-5 w-5" style={{ color: CITTAA_COLORS.teal }} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
              {stats?.students?.active || 0}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              of {stats?.students?.total || 0} total
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow duration-200">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">
              Reports (7 days)
            </CardTitle>
            <FileText className="h-5 w-5" style={{ color: CITTAA_COLORS.teal }} />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
              {(stats?.reports_last_7_days?.daily || 0) + (stats?.reports_last_7_days?.weekly || 0)}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {stats?.reports_last_7_days?.daily || 0} daily, {stats?.reports_last_7_days?.weekly || 0} weekly
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle style={{ color: CITTAA_COLORS.purple }}>
              Escalation Cases by Level
            </CardTitle>
            <CardDescription>
              Distribution of open escalation cases
            </CardDescription>
          </CardHeader>
          <CardContent>
            {escalationPieData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={escalationPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}`}
                    >
                      {escalationPieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center">
                <div className="text-center">
                  <CheckCircle className="h-12 w-12 mx-auto mb-2" style={{ color: CITTAA_COLORS.teal }} />
                  <p className="text-gray-500">No open escalation cases</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle style={{ color: CITTAA_COLORS.purple }}>
              Quick Actions
            </CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              className="w-full justify-start text-white"
              style={{ backgroundColor: CITTAA_COLORS.purple }}
            >
              <FileText className="mr-2 h-4 w-4" />
              Submit Daily Report
            </Button>
            <Button 
              variant="outline"
              className="w-full justify-start"
              style={{ borderColor: CITTAA_COLORS.teal, color: CITTAA_COLORS.teal }}
            >
              <AlertTriangle className="mr-2 h-4 w-4" />
              View Escalation Cases
            </Button>
            <Button 
              variant="outline"
              className="w-full justify-start"
              style={{ borderColor: CITTAA_COLORS.purple, color: CITTAA_COLORS.purple }}
            >
              <GraduationCap className="mr-2 h-4 w-4" />
              Manage Students
            </Button>
            {user?.role === 'admin' && (
              <Button 
                variant="outline"
                className="w-full justify-start"
                style={{ borderColor: CITTAA_COLORS.warmGray, color: CITTAA_COLORS.warmGray }}
              >
                <Shield className="mr-2 h-4 w-4" />
                Compliance Report
              </Button>
            )}
          </CardContent>
        </Card>
      </div>

      {user?.role === 'admin' && stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                Total Users
              </CardTitle>
              <Users className="h-5 w-5" style={{ color: CITTAA_COLORS.purple }} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
                {stats.users.total}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {stats.users.psychologists} psychologists
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                Institutions
              </CardTitle>
              <Building2 className="h-5 w-5" style={{ color: CITTAA_COLORS.purple }} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
                {stats.institutions.active}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                of {stats.institutions.total} total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-500">
                Avg Resolution Time
              </CardTitle>
              <Clock className="h-5 w-5" style={{ color: CITTAA_COLORS.purple }} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
                {escalationStats?.average_resolution_time_hours 
                  ? `${escalationStats.average_resolution_time_hours.toFixed(1)}h`
                  : 'N/A'}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Average case resolution
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
