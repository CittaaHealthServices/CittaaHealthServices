/**
 * API Client for CITTAA Escalation Engine
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface LoginCredentials {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  institution_id?: string;
  rci_registration?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  }

  // Auth endpoints
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const data: TokenResponse = await response.json();
    this.setToken(data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    return data;
  }

  async logout(): Promise<void> {
    try {
      await this.request('/api/v1/auth/logout', { method: 'POST' });
    } finally {
      this.clearToken();
    }
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/auth/me');
  }

  // Reports endpoints
  async getDailyReports(params?: { start_date?: string; end_date?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request(`/api/v1/reports/daily${query}`);
  }

  async submitDailyReport(reportData: any) {
    return this.request('/api/v1/reports/daily', {
      method: 'POST',
      body: JSON.stringify(reportData),
    });
  }

  async getWeeklyReports(params?: { start_date?: string; end_date?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request(`/api/v1/reports/weekly${query}`);
  }

  async submitWeeklyReport(reportData: any) {
    return this.request('/api/v1/reports/weekly', {
      method: 'POST',
      body: JSON.stringify(reportData),
    });
  }

  async getMonthlyReports(params?: { year?: number }) {
    const queryParams = new URLSearchParams();
    if (params?.year) queryParams.append('year', params.year.toString());
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request(`/api/v1/reports/monthly${query}`);
  }

  async submitMonthlyReport(reportData: any) {
    return this.request('/api/v1/reports/monthly', {
      method: 'POST',
      body: JSON.stringify(reportData),
    });
  }

  async downloadReportPdf(reportType: string, reportId: string): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/reports/${reportType}/${reportId}/pdf`,
      {
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      }
    );
    if (!response.ok) throw new Error('Failed to download PDF');
    return response.blob();
  }

  // Escalation endpoints
  async analyzeSession(sessionData: any) {
    return this.request('/api/v1/escalation/analyze', {
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
  }

  async getEscalationCases(params?: {
    status_filter?: string;
    level_filter?: string;
    days?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.status_filter) queryParams.append('status_filter', params.status_filter);
    if (params?.level_filter) queryParams.append('level_filter', params.level_filter);
    if (params?.days) queryParams.append('days', params.days.toString());
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request(`/api/v1/escalation/cases${query}`);
  }

  async createEscalationCase(caseData: any) {
    return this.request('/api/v1/escalation/cases', {
      method: 'POST',
      body: JSON.stringify(caseData),
    });
  }

  async updateEscalationCase(caseId: string, updateData: any) {
    return this.request(`/api/v1/escalation/cases/${caseId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  async getEscalationDashboardStats() {
    return this.request('/api/v1/escalation/dashboard/stats');
  }

  // Admin endpoints
  async getDashboardOverview() {
    return this.request('/api/v1/admin/dashboard/overview');
  }

  async getDashboardTrends(days: number = 30) {
    return this.request(`/api/v1/admin/dashboard/trends?days=${days}`);
  }

  async getAllUsers(params?: { role?: string; is_active?: boolean }) {
    const queryParams = new URLSearchParams();
    if (params?.role) queryParams.append('role', params.role);
    if (params?.is_active !== undefined) queryParams.append('is_active', params.is_active.toString());
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request(`/api/v1/admin/users${query}`);
  }

  async getAuditLog(days: number = 7) {
    return this.request(`/api/v1/admin/audit-log?days=${days}`);
  }

  async getDPDPComplianceReport() {
    return this.request('/api/v1/admin/compliance/dpdp-report');
  }

  // Students endpoints
  async getStudents(params?: { institution_id?: string; grade?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.institution_id) queryParams.append('institution_id', params.institution_id);
    if (params?.grade) queryParams.append('grade', params.grade);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return this.request(`/api/v1/students${query}`);
  }

  async getStudentHistory(studentId: string) {
    return this.request(`/api/v1/students/${studentId}/history`);
  }

  // Institutions endpoints
  async getInstitutions() {
    return this.request('/api/v1/institutions');
  }

  async getInstitutionStats(institutionId: string) {
    return this.request(`/api/v1/institutions/${institutionId}/stats`);
  }
}

export const api = new ApiClient(API_URL);
export type { User, TokenResponse, LoginCredentials };
