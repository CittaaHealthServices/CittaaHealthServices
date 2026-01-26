import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Users, Shield, Download,
  CheckCircle, XCircle, FileText, AlertTriangle
} from 'lucide-react';
import { CITTAA_COLORS, formatDateTime } from '@/lib/utils';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

interface AuditLogEntry {
  log_id: string;
  user_id: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  details?: Record<string, any>;
  ip_address?: string;
  timestamp: string;
}

interface TrendData {
  date: string;
  sessions: number;
  escalations: number;
}

export default function Admin() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([]);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (user?.role === 'admin') {
      loadAdminData();
    }
  }, [user]);

  const loadAdminData = async () => {
    setIsLoading(true);
    try {
      const [usersData, auditData, trendsData] = await Promise.all([
        api.getAllUsers().catch(() => []),
        api.getAuditLog(7).catch(() => []),
        api.getDashboardTrends(30).catch(() => ({ sessions_per_day: [], escalations_per_day: [] })),
      ]);
      
      setUsers(usersData as User[]);
      setAuditLog(auditData as AuditLogEntry[]);
      
      const trendsResult = trendsData as { sessions_per_day: any[]; escalations_per_day: any[] };
      const combinedTrends = trendsResult.sessions_per_day?.map((s: any, idx: number) => ({
        date: s.date,
        sessions: s.count,
        escalations: trendsResult.escalations_per_day?.[idx]?.count || 0,
      })) || [];
      setTrends(combinedTrends);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRoleBadge = (role: string) => {
    const colors: Record<string, string> = {
      admin: CITTAA_COLORS.purple,
      psychologist: CITTAA_COLORS.teal,
      school_admin: '#CA8A04',
    };
    const color = colors[role] || CITTAA_COLORS.warmGray;
    return (
      <Badge style={{ backgroundColor: `${color}20`, color: color }}>
        {role.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const getActionBadge = (action: string) => {
    const colors: Record<string, string> = {
      login: CITTAA_COLORS.teal,
      logout: CITTAA_COLORS.warmGray,
      create: '#059669',
      update: CITTAA_COLORS.purple,
      delete: '#DC2626',
      escalation: '#EA580C',
    };
    const color = colors[action] || CITTAA_COLORS.warmGray;
    return (
      <Badge variant="outline" style={{ borderColor: color, color: color }}>
        {action.toUpperCase()}
      </Badge>
    );
  };

  if (user?.role !== 'admin') {
    return (
      <div className="flex items-center justify-center min-h-96">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <Shield className="h-12 w-12 mx-auto mb-4" style={{ color: CITTAA_COLORS.warmGray }} />
            <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
            <p className="text-gray-500">
              You don't have permission to access the admin panel.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
            Admin Panel
          </h1>
          <p className="text-gray-500 mt-1">
            System management and compliance monitoring
          </p>
        </div>
        <Button 
          variant="outline"
          style={{ borderColor: CITTAA_COLORS.purple, color: CITTAA_COLORS.purple }}
        >
          <Download className="h-4 w-4 mr-2" />
          Export DPDP Report
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="audit">Audit Log</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-500">Total Users</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
                  {users.length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-500">Active Users</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold" style={{ color: CITTAA_COLORS.teal }}>
                  {users.filter(u => u.is_active).length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-500">Psychologists</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
                  {users.filter(u => u.role === 'psychologist').length}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-500">Audit Events (7d)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold" style={{ color: CITTAA_COLORS.warmGray }}>
                  {auditLog.length}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle style={{ color: CITTAA_COLORS.purple }}>Activity Trends (30 days)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="sessions" 
                      stroke={CITTAA_COLORS.teal} 
                      name="Sessions"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="escalations" 
                      stroke={CITTAA_COLORS.purple} 
                      name="Escalations"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle style={{ color: CITTAA_COLORS.purple }}>User Management</CardTitle>
              <CardDescription>Manage system users and their roles</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
                </div>
              ) : (
                <div className="space-y-4">
                  {users.map((u) => (
                    <div
                      key={u.user_id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center gap-4">
                        <div 
                          className="w-10 h-10 rounded-full flex items-center justify-center"
                          style={{ backgroundColor: `${CITTAA_COLORS.purple}20` }}
                        >
                          <Users className="h-5 w-5" style={{ color: CITTAA_COLORS.purple }} />
                        </div>
                        <div>
                          <p className="font-medium">{u.full_name}</p>
                          <p className="text-sm text-gray-500">{u.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        {getRoleBadge(u.role)}
                        {u.is_active ? (
                          <CheckCircle className="h-5 w-5 text-green-500" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-500" />
                        )}
                        <Button variant="outline" size="sm">Edit</Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audit" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle style={{ color: CITTAA_COLORS.purple }}>Audit Log</CardTitle>
              <CardDescription>DPDP Act 2023 compliant activity tracking</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
                </div>
              ) : auditLog.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 mx-auto mb-4" style={{ color: CITTAA_COLORS.warmGray }} />
                  <p className="text-gray-500">No audit events recorded</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {auditLog.map((entry) => (
                    <div
                      key={entry.log_id}
                      className="flex items-center justify-between p-3 border rounded-lg text-sm"
                    >
                      <div className="flex items-center gap-3">
                        {getActionBadge(entry.action)}
                        <span className="text-gray-600">
                          {entry.entity_type} {entry.entity_id ? `#${entry.entity_id.slice(0, 8)}` : ''}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-gray-500">
                        <span>{entry.ip_address || 'N/A'}</span>
                        <span>{formatDateTime(entry.timestamp)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle style={{ color: CITTAA_COLORS.purple }}>
                  DPDP Act 2023 Compliance
                </CardTitle>
                <CardDescription>Data Protection and Privacy compliance status</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span>Data Encryption (AES-256)</span>
                  </div>
                  <Badge className="bg-green-100 text-green-700">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span>Audit Trail Logging</span>
                  </div>
                  <Badge className="bg-green-100 text-green-700">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span>Student Data Anonymization</span>
                  </div>
                  <Badge className="bg-green-100 text-green-700">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span>Role-Based Access Control</span>
                  </div>
                  <Badge className="bg-green-100 text-green-700">Active</Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle style={{ color: CITTAA_COLORS.purple }}>
                  POCSO Act Compliance
                </CardTitle>
                <CardDescription>Protection of Children from Sexual Offences</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span>Automatic Abuse Detection</span>
                  </div>
                  <Badge className="bg-green-100 text-green-700">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span>Mandatory Reporting Triggers</span>
                  </div>
                  <Badge className="bg-green-100 text-green-700">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span>Emergency Escalation Protocol</span>
                  </div>
                  <Badge className="bg-green-100 text-green-700">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-yellow-500" />
                    <span>Authority Notification System</span>
                  </div>
                  <Badge className="bg-yellow-100 text-yellow-700">Configure</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
