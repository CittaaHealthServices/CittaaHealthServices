import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  FileText, Download, Calendar, Plus, Eye,
  Clock, CheckCircle, AlertCircle
} from 'lucide-react';
import { CITTAA_COLORS, formatDate } from '@/lib/utils';

interface Report {
  report_id: string;
  report_date?: string;
  week_start_date?: string;
  week_end_date?: string;
  report_month?: string;
  status: string;
  submitted_at: string;
  sessions_conducted?: number;
  total_sessions?: number;
  crisis_interventions?: number;
}

export default function Reports() {
  const [dailyReports, setDailyReports] = useState<Report[]>([]);
  const [weeklyReports, setWeeklyReports] = useState<Report[]>([]);
  const [monthlyReports, setMonthlyReports] = useState<Report[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('daily');

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    setIsLoading(true);
    try {
      const [daily, weekly, monthly] = await Promise.all([
        api.getDailyReports().catch(() => []),
        api.getWeeklyReports().catch(() => []),
        api.getMonthlyReports().catch(() => []),
      ]);
      setDailyReports(daily as Report[]);
      setWeeklyReports(weekly as Report[]);
      setMonthlyReports(monthly as Report[]);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadPdf = async (reportType: string, reportId: string) => {
    try {
      const blob = await api.downloadReportPdf(reportType, reportId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}_report_${reportId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download PDF:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, { bg: string; color: string; icon: React.ReactNode }> = {
      submitted: { 
        bg: `${CITTAA_COLORS.teal}20`, 
        color: CITTAA_COLORS.teal,
        icon: <CheckCircle className="h-3 w-3" />
      },
      draft: { 
        bg: `${CITTAA_COLORS.warmGray}20`, 
        color: CITTAA_COLORS.warmGray,
        icon: <Clock className="h-3 w-3" />
      },
      pending: { 
        bg: '#CA8A0420', 
        color: '#CA8A04',
        icon: <AlertCircle className="h-3 w-3" />
      },
    };
    const style = styles[status] || styles.draft;
    return (
      <Badge 
        className="flex items-center gap-1"
        style={{ backgroundColor: style.bg, color: style.color }}
      >
        {style.icon}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const ReportCard = ({ report, type }: { report: Report; type: string }) => {
    const getDateDisplay = () => {
      if (type === 'daily' && report.report_date) {
        return formatDate(report.report_date);
      } else if (type === 'weekly' && report.week_start_date && report.week_end_date) {
        return `${formatDate(report.week_start_date)} - ${formatDate(report.week_end_date)}`;
      } else if (type === 'monthly' && report.report_month) {
        return new Date(report.report_month).toLocaleDateString('en-IN', { year: 'numeric', month: 'long' });
      }
      return 'N/A';
    };

    return (
      <div className="border rounded-lg p-4 hover:shadow-md transition-all duration-200">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" style={{ color: CITTAA_COLORS.purple }} />
              <span className="font-medium" style={{ color: CITTAA_COLORS.darkText }}>
                {getDateDisplay()}
              </span>
              {getStatusBadge(report.status)}
            </div>
            <div className="flex gap-4 text-sm text-gray-500">
              {type === 'daily' && (
                <>
                  <span>Sessions: {report.sessions_conducted || 0}</span>
                  <span>Crisis: {report.crisis_interventions || 0}</span>
                </>
              )}
              {type === 'weekly' && (
                <span>Total Sessions: {report.total_sessions || 0}</span>
              )}
            </div>
            {report.submitted_at && (
              <p className="text-xs text-gray-400">
                Submitted: {formatDate(report.submitted_at)}
              </p>
            )}
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm"
              style={{ borderColor: CITTAA_COLORS.purple, color: CITTAA_COLORS.purple }}
            >
              <Eye className="h-4 w-4 mr-1" />
              View
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => downloadPdf(type, report.report_id)}
              style={{ borderColor: CITTAA_COLORS.teal, color: CITTAA_COLORS.teal }}
            >
              <Download className="h-4 w-4 mr-1" />
              PDF
            </Button>
          </div>
        </div>
      </div>
    );
  };

  const EmptyState = ({ type }: { type: string }) => (
    <div className="text-center py-12">
      <FileText className="h-12 w-12 mx-auto mb-4" style={{ color: CITTAA_COLORS.warmGray }} />
      <h3 className="text-lg font-medium text-gray-900 mb-2">No {type} reports yet</h3>
      <p className="text-gray-500 mb-4">Start by creating your first {type} report</p>
      <Button 
        className="text-white"
        style={{ backgroundColor: CITTAA_COLORS.purple }}
      >
        <Plus className="h-4 w-4 mr-2" />
        Create {type.charAt(0).toUpperCase() + type.slice(1)} Report
      </Button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
            Reports
          </h1>
          <p className="text-gray-500 mt-1">
            View and manage your activity reports
          </p>
        </div>
        <Button 
          className="text-white"
          style={{ backgroundColor: CITTAA_COLORS.purple }}
        >
          <Plus className="h-4 w-4 mr-2" />
          New Report
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3 max-w-md">
          <TabsTrigger 
            value="daily"
            className="data-[state=active]:text-white"
            style={{ 
              backgroundColor: activeTab === 'daily' ? CITTAA_COLORS.purple : 'transparent',
            }}
          >
            Daily
          </TabsTrigger>
          <TabsTrigger 
            value="weekly"
            className="data-[state=active]:text-white"
            style={{ 
              backgroundColor: activeTab === 'weekly' ? CITTAA_COLORS.purple : 'transparent',
            }}
          >
            Weekly
          </TabsTrigger>
          <TabsTrigger 
            value="monthly"
            className="data-[state=active]:text-white"
            style={{ 
              backgroundColor: activeTab === 'monthly' ? CITTAA_COLORS.purple : 'transparent',
            }}
          >
            Monthly
          </TabsTrigger>
        </TabsList>

        <TabsContent value="daily" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle style={{ color: CITTAA_COLORS.purple }}>Daily Activity Reports</CardTitle>
              <CardDescription>
                Track daily sessions, assessments, consultations, and crisis interventions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
                </div>
              ) : dailyReports.length === 0 ? (
                <EmptyState type="daily" />
              ) : (
                <div className="space-y-4">
                  {dailyReports.map((report) => (
                    <ReportCard key={report.report_id} report={report} type="daily" />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="weekly" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle style={{ color: CITTAA_COLORS.purple }}>Weekly Summary Reports</CardTitle>
              <CardDescription>
                Comprehensive weekly summaries with service delivery statistics
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
                </div>
              ) : weeklyReports.length === 0 ? (
                <EmptyState type="weekly" />
              ) : (
                <div className="space-y-4">
                  {weeklyReports.map((report) => (
                    <ReportCard key={report.report_id} report={report} type="weekly" />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monthly" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle style={{ color: CITTAA_COLORS.purple }}>Monthly Metrics Reports</CardTitle>
              <CardDescription>
                Monthly metrics tracking with trends and outcomes analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
                </div>
              ) : monthlyReports.length === 0 ? (
                <EmptyState type="monthly" />
              ) : (
                <div className="space-y-4">
                  {monthlyReports.map((report) => (
                    <ReportCard key={report.report_id} report={report} type="monthly" />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
