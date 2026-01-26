import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Users, Shield, Download, Plus, Edit2, UserPlus,
  CheckCircle, XCircle, FileText, AlertTriangle, Eye,
  ClipboardList, Activity
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
  phone?: string;
  rci_registration?: string;
}

interface Role {
  role_id: string;
  name: string;
  display_name: string;
  description?: string;
  permissions: Record<string, string[]>;
  is_system_role: boolean;
  is_active: boolean;
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

interface ReportSummary {
  report_id: string;
  report_date: string;
  psychologist_name: string;
  psychologist_email: string;
  status: string;
  submitted_at?: string;
}

interface EscalationSummary {
  case_id: string;
  escalation_level: string;
  status: string;
  risk_score: number;
  psychologist_name: string;
  student_code: string;
  escalated_at: string;
}

interface SessionSummary {
  session_id: string;
  session_date: string;
  session_type: string;
  psychologist_name: string;
  student_code: string;
  ai_risk_level?: string;
}

const AVAILABLE_ROLES = [
  { value: 'admin', label: 'Administrator', description: 'Full system access' },
  { value: 'psychologist', label: 'Psychologist', description: 'Submit reports and manage students' },
  { value: 'school_admin', label: 'School Admin', description: 'View institution data' },
  { value: 'manager', label: 'Manager', description: 'Psychology team manager - view all data' },
  { value: 'quality_manager', label: 'Quality Manager', description: 'Quality oversight and compliance' },
];

export default function Admin() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([]);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [reports, setReports] = useState<{ daily_reports: ReportSummary[], weekly_reports: ReportSummary[], monthly_reports: ReportSummary[] }>({ daily_reports: [], weekly_reports: [], monthly_reports: [] });
  const [escalations, setEscalations] = useState<EscalationSummary[]>([]);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  const [showCreateUserDialog, setShowCreateUserDialog] = useState(false);
  const [showCreateRoleDialog, setShowCreateRoleDialog] = useState(false);
  const [showChangeRoleDialog, setShowChangeRoleDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  
  const [newUser, setNewUser] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'psychologist',
    phone: '',
    rci_registration: '',
  });
  
  const [newRole, setNewRole] = useState({
    name: '',
    display_name: '',
    description: '',
  });

  const isManagerOrAdmin = user?.role === 'admin' || user?.role === 'manager' || user?.role === 'quality_manager';

  useEffect(() => {
    if (isManagerOrAdmin) {
      loadAdminData();
    }
  }, [user]);

  const loadAdminData = async () => {
    setIsLoading(true);
    try {
      const promises = [
        api.getAllUsers().catch(() => []),
        api.getAuditLog(7).catch(() => ({ events: [] })),
        api.getDashboardTrends(30).catch(() => ({ sessions_trend: [], escalations_trend: [] })),
      ];
      
      if (user?.role === 'admin') {
        promises.push(api.getRoles().catch(() => []));
      }
      
      if (isManagerOrAdmin) {
        promises.push(api.getManagerReports().catch(() => ({ daily_reports: [], weekly_reports: [], monthly_reports: [] })));
        promises.push(api.getManagerEscalations().catch(() => ({ escalations: [] })));
        promises.push(api.getManagerSessions().catch(() => ({ sessions: [] })));
      }
      
      const results = await Promise.all(promises);
      
      setUsers(results[0] as User[]);
      const auditResult = results[1] as { events?: AuditLogEntry[] };
      setAuditLog(auditResult.events || []);
      
      const trendsResult = results[2] as { sessions_trend?: any[]; escalations_trend?: any[] };
      const combinedTrends = trendsResult.sessions_trend?.map((s: any, idx: number) => ({
        date: s.date,
        sessions: s.count,
        escalations: trendsResult.escalations_trend?.[idx]?.count || 0,
      })) || [];
      setTrends(combinedTrends);
      
      if (user?.role === 'admin' && results[3]) {
        setRoles(results[3] as Role[]);
      }
      
      if (isManagerOrAdmin) {
        const reportsIdx = user?.role === 'admin' ? 4 : 3;
        if (results[reportsIdx]) {
          setReports(results[reportsIdx] as any);
        }
        if (results[reportsIdx + 1]) {
          setEscalations((results[reportsIdx + 1] as any).escalations || []);
        }
        if (results[reportsIdx + 2]) {
          setSessions((results[reportsIdx + 2] as any).sessions || []);
        }
      }
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateUser = async () => {
    try {
      await api.createUser(newUser);
      setShowCreateUserDialog(false);
      setNewUser({ email: '', password: '', full_name: '', role: 'psychologist', phone: '', rci_registration: '' });
      loadAdminData();
    } catch (error) {
      console.error('Failed to create user:', error);
      alert('Failed to create user. Please try again.');
    }
  };

  const handleCreateRole = async () => {
    try {
      await api.createRole(newRole);
      setShowCreateRoleDialog(false);
      setNewRole({ name: '', display_name: '', description: '' });
      loadAdminData();
    } catch (error) {
      console.error('Failed to create role:', error);
      alert('Failed to create role. Please try again.');
    }
  };

  const handleChangeUserRole = async (newRoleValue: string) => {
    if (!selectedUser) return;
    try {
      await api.changeUserRole(selectedUser.user_id, newRoleValue);
      setShowChangeRoleDialog(false);
      setSelectedUser(null);
      loadAdminData();
    } catch (error) {
      console.error('Failed to change user role:', error);
      alert('Failed to change user role. Please try again.');
    }
  };

  const getRoleBadge = (role: string) => {
    const colors: Record<string, string> = {
      admin: CITTAA_COLORS.purple,
      psychologist: CITTAA_COLORS.teal,
      school_admin: '#CA8A04',
      manager: '#2563EB',
      quality_manager: '#7C3AED',
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

  const getEscalationLevelBadge = (level: string) => {
    const colors: Record<string, string> = {
      level_1_low: '#22C55E',
      level_2_moderate: '#EAB308',
      level_3_high: '#F97316',
      level_4_emergency: '#EF4444',
    };
    const labels: Record<string, string> = {
      level_1_low: 'LOW',
      level_2_moderate: 'MODERATE',
      level_3_high: 'HIGH',
      level_4_emergency: 'EMERGENCY',
    };
    const color = colors[level] || CITTAA_COLORS.warmGray;
    return (
      <Badge style={{ backgroundColor: color, color: 'white' }}>
        {labels[level] || level}
      </Badge>
    );
  };

  if (!isManagerOrAdmin) {
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
            {user?.role === 'admin' ? 'Admin Panel' : 'Manager Dashboard'}
          </h1>
          <p className="text-gray-500 mt-1">
            {user?.role === 'admin' ? 'System management and compliance monitoring' : 'Team oversight and data review'}
          </p>
        </div>
        <div className="flex gap-2">
          {user?.role === 'admin' && (
            <Dialog open={showCreateUserDialog} onOpenChange={setShowCreateUserDialog}>
              <DialogTrigger asChild>
                <Button style={{ backgroundColor: CITTAA_COLORS.purple }}>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Create User
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle>Create New User</DialogTitle>
                  <DialogDescription>
                    Add a new user to the system with a specific role.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="user@example.com"
                      value={newUser.email}
                      onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter password"
                      value={newUser.password}
                      onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      placeholder="John Doe"
                      value={newUser.full_name}
                      onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="role">Role</Label>
                    <Select value={newUser.role} onValueChange={(value) => setNewUser({ ...newUser, role: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select role" />
                      </SelectTrigger>
                      <SelectContent>
                        {AVAILABLE_ROLES.map((role) => (
                          <SelectItem key={role.value} value={role.value}>
                            {role.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone (Optional)</Label>
                    <Input
                      id="phone"
                      placeholder="+91 9876543210"
                      value={newUser.phone}
                      onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="rci">RCI Registration (For Psychologists)</Label>
                    <Input
                      id="rci"
                      placeholder="RCI Registration Number"
                      value={newUser.rci_registration}
                      onChange={(e) => setNewUser({ ...newUser, rci_registration: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowCreateUserDialog(false)}>
                    Cancel
                  </Button>
                  <Button 
                    onClick={handleCreateUser}
                    style={{ backgroundColor: CITTAA_COLORS.purple }}
                    disabled={!newUser.email || !newUser.password || !newUser.full_name}
                  >
                    Create User
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          )}
          <Button 
            variant="outline"
            style={{ borderColor: CITTAA_COLORS.purple, color: CITTAA_COLORS.purple }}
          >
            <Download className="h-4 w-4 mr-2" />
            Export DPDP Report
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          {user?.role === 'admin' && <TabsTrigger value="roles">Roles</TabsTrigger>}
          {isManagerOrAdmin && <TabsTrigger value="reports">Reports</TabsTrigger>}
          {isManagerOrAdmin && <TabsTrigger value="escalations">Escalations</TabsTrigger>}
          {isManagerOrAdmin && <TabsTrigger value="sessions">Sessions</TabsTrigger>}
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
                        {user?.role === 'admin' && (
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              setSelectedUser(u);
                              setShowChangeRoleDialog(true);
                            }}
                          >
                            <Edit2 className="h-4 w-4 mr-1" />
                            Change Role
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Dialog open={showChangeRoleDialog} onOpenChange={setShowChangeRoleDialog}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Change User Role</DialogTitle>
                <DialogDescription>
                  Change the role for {selectedUser?.full_name} ({selectedUser?.email})
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <Label>Select New Role</Label>
                <div className="grid grid-cols-1 gap-2 mt-2">
                  {AVAILABLE_ROLES.map((role) => (
                    <Button
                      key={role.value}
                      variant={selectedUser?.role === role.value ? "default" : "outline"}
                      className="justify-start h-auto py-3"
                      onClick={() => handleChangeUserRole(role.value)}
                      disabled={selectedUser?.role === role.value}
                    >
                      <div className="text-left">
                        <div className="font-medium">{role.label}</div>
                        <div className="text-xs opacity-70">{role.description}</div>
                      </div>
                    </Button>
                  ))}
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </TabsContent>

        {user?.role === 'admin' && (
          <TabsContent value="roles" className="mt-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle style={{ color: CITTAA_COLORS.purple }}>Role Management</CardTitle>
                  <CardDescription>Manage system roles and permissions</CardDescription>
                </div>
                <Dialog open={showCreateRoleDialog} onOpenChange={setShowCreateRoleDialog}>
                  <DialogTrigger asChild>
                    <Button style={{ backgroundColor: CITTAA_COLORS.purple }}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Role
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create New Role</DialogTitle>
                      <DialogDescription>
                        Add a new custom role to the system.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="role_name">Role Name (lowercase, no spaces)</Label>
                        <Input
                          id="role_name"
                          placeholder="custom_role"
                          value={newRole.name}
                          onChange={(e) => setNewRole({ ...newRole, name: e.target.value.toLowerCase().replace(/\s/g, '_') })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="display_name">Display Name</Label>
                        <Input
                          id="display_name"
                          placeholder="Custom Role"
                          value={newRole.display_name}
                          onChange={(e) => setNewRole({ ...newRole, display_name: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Input
                          id="description"
                          placeholder="Role description"
                          value={newRole.description}
                          onChange={(e) => setNewRole({ ...newRole, description: e.target.value })}
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setShowCreateRoleDialog(false)}>
                        Cancel
                      </Button>
                      <Button 
                        onClick={handleCreateRole}
                        style={{ backgroundColor: CITTAA_COLORS.purple }}
                        disabled={!newRole.name || !newRole.display_name}
                      >
                        Create Role
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {AVAILABLE_ROLES.map((role) => (
                    <div
                      key={role.value}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        <div 
                          className="w-10 h-10 rounded-full flex items-center justify-center"
                          style={{ backgroundColor: `${CITTAA_COLORS.purple}20` }}
                        >
                          <Shield className="h-5 w-5" style={{ color: CITTAA_COLORS.purple }} />
                        </div>
                        <div>
                          <p className="font-medium">{role.label}</p>
                          <p className="text-sm text-gray-500">{role.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {getRoleBadge(role.value)}
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          System Role
                        </Badge>
                      </div>
                    </div>
                  ))}
                  {roles.filter(r => !r.is_system_role).map((role) => (
                    <div
                      key={role.role_id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        <div 
                          className="w-10 h-10 rounded-full flex items-center justify-center"
                          style={{ backgroundColor: `${CITTAA_COLORS.teal}20` }}
                        >
                          <Shield className="h-5 w-5" style={{ color: CITTAA_COLORS.teal }} />
                        </div>
                        <div>
                          <p className="font-medium">{role.display_name}</p>
                          <p className="text-sm text-gray-500">{role.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {getRoleBadge(role.name)}
                        <Badge variant="outline" className="text-blue-600 border-blue-600">
                          Custom Role
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {isManagerOrAdmin && (
          <TabsContent value="reports" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle style={{ color: CITTAA_COLORS.purple }}>
                  <ClipboardList className="h-5 w-5 inline mr-2" />
                  Submitted Reports
                </CardTitle>
                <CardDescription>View all reports submitted by psychologists</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-semibold mb-3">Daily Reports ({reports.daily_reports.length})</h3>
                      {reports.daily_reports.length === 0 ? (
                        <p className="text-gray-500 text-sm">No daily reports found</p>
                      ) : (
                        <div className="space-y-2">
                          {reports.daily_reports.slice(0, 10).map((report) => (
                            <div key={report.report_id} className="flex items-center justify-between p-3 border rounded-lg text-sm">
                              <div className="flex items-center gap-3">
                                <FileText className="h-4 w-4" style={{ color: CITTAA_COLORS.purple }} />
                                <span className="font-medium">{report.report_date}</span>
                                <span className="text-gray-500">by {report.psychologist_name}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge variant={report.status === 'submitted' ? 'default' : 'outline'}>
                                  {report.status}
                                </Badge>
                                <Button variant="ghost" size="sm">
                                  <Eye className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold mb-3">Weekly Reports ({reports.weekly_reports.length})</h3>
                      {reports.weekly_reports.length === 0 ? (
                        <p className="text-gray-500 text-sm">No weekly reports found</p>
                      ) : (
                        <div className="space-y-2">
                          {reports.weekly_reports.slice(0, 5).map((report) => (
                            <div key={report.report_id} className="flex items-center justify-between p-3 border rounded-lg text-sm">
                              <div className="flex items-center gap-3">
                                <FileText className="h-4 w-4" style={{ color: CITTAA_COLORS.teal }} />
                                <span className="font-medium">{report.report_date}</span>
                                <span className="text-gray-500">by {report.psychologist_name}</span>
                              </div>
                              <Badge variant={report.status === 'submitted' ? 'default' : 'outline'}>
                                {report.status}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {isManagerOrAdmin && (
          <TabsContent value="escalations" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle style={{ color: CITTAA_COLORS.purple }}>
                  <AlertTriangle className="h-5 w-5 inline mr-2" />
                  Escalation Cases
                </CardTitle>
                <CardDescription>Monitor all escalation cases across the system</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
                  </div>
                ) : escalations.length === 0 ? (
                  <div className="text-center py-8">
                    <AlertTriangle className="h-12 w-12 mx-auto mb-4" style={{ color: CITTAA_COLORS.warmGray }} />
                    <p className="text-gray-500">No escalation cases found</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {escalations.map((esc) => (
                      <div
                        key={esc.case_id}
                        className="flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-center gap-4">
                          <div 
                            className="w-10 h-10 rounded-full flex items-center justify-center"
                            style={{ backgroundColor: '#FEE2E2' }}
                          >
                            <AlertTriangle className="h-5 w-5 text-red-500" />
                          </div>
                          <div>
                            <p className="font-medium">Student: {esc.student_code}</p>
                            <p className="text-sm text-gray-500">
                              By {esc.psychologist_name} | {formatDateTime(esc.escalated_at)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          {getEscalationLevelBadge(esc.escalation_level)}
                          <Badge variant={esc.status === 'open' ? 'destructive' : 'outline'}>
                            {esc.status.toUpperCase()}
                          </Badge>
                          <span className="text-sm font-medium">
                            Risk: {Math.round(esc.risk_score * 100)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {isManagerOrAdmin && (
          <TabsContent value="sessions" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle style={{ color: CITTAA_COLORS.purple }}>
                  <Activity className="h-5 w-5 inline mr-2" />
                  Counseling Sessions
                </CardTitle>
                <CardDescription>View all counseling sessions conducted</CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
                  </div>
                ) : sessions.length === 0 ? (
                  <div className="text-center py-8">
                    <Activity className="h-12 w-12 mx-auto mb-4" style={{ color: CITTAA_COLORS.warmGray }} />
                    <p className="text-gray-500">No sessions found</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {sessions.map((session) => (
                      <div
                        key={session.session_id}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex items-center gap-4">
                          <div 
                            className="w-10 h-10 rounded-full flex items-center justify-center"
                            style={{ backgroundColor: `${CITTAA_COLORS.teal}20` }}
                          >
                            <Activity className="h-5 w-5" style={{ color: CITTAA_COLORS.teal }} />
                          </div>
                          <div>
                            <p className="font-medium">
                              {session.session_type.replace('_', ' ')} - {session.student_code}
                            </p>
                            <p className="text-sm text-gray-500">
                              By {session.psychologist_name} | {session.session_date}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          {session.ai_risk_level && (
                            <Badge 
                              variant="outline"
                              style={{ 
                                borderColor: session.ai_risk_level === 'high' ? '#EF4444' : 
                                            session.ai_risk_level === 'moderate' ? '#F97316' : '#22C55E',
                                color: session.ai_risk_level === 'high' ? '#EF4444' : 
                                       session.ai_risk_level === 'moderate' ? '#F97316' : '#22C55E'
                              }}
                            >
                              AI: {session.ai_risk_level.toUpperCase()}
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        )}

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
