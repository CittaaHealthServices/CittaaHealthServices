import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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
  total_students?: number;
  crisis_interventions?: number;
  key_highlights?: string;
  notes_and_observations?: string;
  summary?: string;
  challenges?: string;
  executive_summary?: string;
  recommendations?: string;
}

export default function Reports() {
  const [dailyReports, setDailyReports] = useState<Report[]>([]);
  const [weeklyReports, setWeeklyReports] = useState<Report[]>([]);
  const [monthlyReports, setMonthlyReports] = useState<Report[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('daily');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [reportType, setReportType] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  
  const [dailyFormData, setDailyFormData] = useState({
    report_date: new Date().toISOString().split('T')[0],
    key_highlights: '',
    notes_and_observations: '',
    sessions_details: [] as Array<{
      student_code: string;
      session_type: string;
      duration_minutes: number;
      presenting_issue: string;
      notes: string;
      follow_up_needed: boolean;
    }>
  });
  
  const [weeklyFormData, setWeeklyFormData] = useState({
    week_start_date: '',
    week_end_date: '',
    total_sessions: 0,
    total_students: 0,
    summary: '',
    challenges: ''
  });
  
    const [monthlyFormData, setMonthlyFormData] = useState({
      report_month: new Date().toISOString().slice(0, 7),
      executive_summary: '',
      recommendations: ''
    });

    const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
    const [viewingReport, setViewingReport] = useState<Report | null>(null);
    const [viewingReportType, setViewingReportType] = useState<string>('daily');

    const openViewDialog = (report: Report, type: string) => {
      setViewingReport(report);
      setViewingReportType(type);
      setIsViewDialogOpen(true);
    };

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

    const openNewReportDialog = (type: 'daily' | 'weekly' | 'monthly') => {
      setReportType(type);
      if (type === 'daily') {
        setDailyFormData({
          report_date: new Date().toISOString().split('T')[0],
          key_highlights: '',
          notes_and_observations: '',
          sessions_details: []
        });
      } else if (type === 'weekly') {
        const today = new Date();
        const startOfWeek = new Date(today);
        startOfWeek.setDate(today.getDate() - today.getDay());
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6);
        setWeeklyFormData({
          week_start_date: startOfWeek.toISOString().split('T')[0],
          week_end_date: endOfWeek.toISOString().split('T')[0],
          total_sessions: 0,
          total_students: 0,
          summary: '',
          challenges: ''
        });
      } else {
        setMonthlyFormData({
          report_month: new Date().toISOString().slice(0, 7),
          executive_summary: '',
          recommendations: ''
        });
      }
      setIsDialogOpen(true);
    };

    const handleSubmitReport = async () => {
      setIsSubmitting(true);
      try {
        if (reportType === 'daily') {
          await api.submitDailyReport(dailyFormData);
        } else if (reportType === 'weekly') {
          await api.submitWeeklyReport(weeklyFormData);
        } else {
          await api.submitMonthlyReport(monthlyFormData);
        }
        setIsDialogOpen(false);
        loadReports();
      } catch (error) {
        console.error('Failed to submit report:', error);
        alert('Failed to submit report. Please try again.');
      } finally {
        setIsSubmitting(false);
      }
    };

    const downloadPdf= async (reportType: string, reportId: string) => {
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
                          onClick={() => openViewDialog(report, type)}
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
          onClick={() => openNewReportDialog(type as 'daily' | 'weekly' | 'monthly')}
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
                onClick={() => openNewReportDialog(activeTab as 'daily' | 'weekly' | 'monthly')}
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

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle style={{ color: CITTAA_COLORS.purple }}>
              Create {reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report
            </DialogTitle>
            <DialogDescription>
              Fill in the details for your {reportType} activity report.
            </DialogDescription>
          </DialogHeader>

          {reportType === 'daily' && (
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="report_date" className="text-right">Date</Label>
                <Input
                  id="report_date"
                  type="date"
                  value={dailyFormData.report_date}
                  onChange={(e) => setDailyFormData({ ...dailyFormData, report_date: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="key_highlights" className="text-right">Key Highlights</Label>
                <Textarea
                  id="key_highlights"
                  placeholder="Enter key highlights from today's sessions..."
                  value={dailyFormData.key_highlights}
                  onChange={(e) => setDailyFormData({ ...dailyFormData, key_highlights: e.target.value })}
                  className="col-span-3"
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="notes" className="text-right">Notes</Label>
                <Textarea
                  id="notes"
                  placeholder="Additional notes and observations..."
                  value={dailyFormData.notes_and_observations}
                  onChange={(e) => setDailyFormData({ ...dailyFormData, notes_and_observations: e.target.value })}
                  className="col-span-3"
                  rows={3}
                />
              </div>
            </div>
          )}

          {reportType === 'weekly' && (
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="week_start" className="text-right">Week Start</Label>
                <Input
                  id="week_start"
                  type="date"
                  value={weeklyFormData.week_start_date}
                  onChange={(e) => setWeeklyFormData({ ...weeklyFormData, week_start_date: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="week_end" className="text-right">Week End</Label>
                <Input
                  id="week_end"
                  type="date"
                  value={weeklyFormData.week_end_date}
                  onChange={(e) => setWeeklyFormData({ ...weeklyFormData, week_end_date: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="total_sessions" className="text-right">Total Sessions</Label>
                <Input
                  id="total_sessions"
                  type="number"
                  value={weeklyFormData.total_sessions}
                  onChange={(e) => setWeeklyFormData({ ...weeklyFormData, total_sessions: parseInt(e.target.value) || 0 })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="total_students" className="text-right">Total Students</Label>
                <Input
                  id="total_students"
                  type="number"
                  value={weeklyFormData.total_students}
                  onChange={(e) => setWeeklyFormData({ ...weeklyFormData, total_students: parseInt(e.target.value) || 0 })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="summary" className="text-right">Summary</Label>
                <Textarea
                  id="summary"
                  placeholder="Weekly summary..."
                  value={weeklyFormData.summary}
                  onChange={(e) => setWeeklyFormData({ ...weeklyFormData, summary: e.target.value })}
                  className="col-span-3"
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="challenges" className="text-right">Challenges</Label>
                <Textarea
                  id="challenges"
                  placeholder="Challenges faced this week..."
                  value={weeklyFormData.challenges}
                  onChange={(e) => setWeeklyFormData({ ...weeklyFormData, challenges: e.target.value })}
                  className="col-span-3"
                  rows={3}
                />
              </div>
            </div>
          )}

          {reportType === 'monthly' && (
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="report_month" className="text-right">Month</Label>
                <Input
                  id="report_month"
                  type="month"
                  value={monthlyFormData.report_month}
                  onChange={(e) => setMonthlyFormData({ ...monthlyFormData, report_month: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="executive_summary" className="text-right">Executive Summary</Label>
                <Textarea
                  id="executive_summary"
                  placeholder="Monthly executive summary..."
                  value={monthlyFormData.executive_summary}
                  onChange={(e) => setMonthlyFormData({ ...monthlyFormData, executive_summary: e.target.value })}
                  className="col-span-3"
                  rows={4}
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="recommendations" className="text-right">Recommendations</Label>
                <Textarea
                  id="recommendations"
                  placeholder="Recommendations for next month..."
                  value={monthlyFormData.recommendations}
                  onChange={(e) => setMonthlyFormData({ ...monthlyFormData, recommendations: e.target.value })}
                  className="col-span-3"
                  rows={4}
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleSubmitReport}
              disabled={isSubmitting}
              className="text-white"
              style={{ backgroundColor: CITTAA_COLORS.purple }}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Report'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle style={{ color: CITTAA_COLORS.purple }}>
              {viewingReportType.charAt(0).toUpperCase() + viewingReportType.slice(1)} Report Details
            </DialogTitle>
            <DialogDescription>
              View the details of this {viewingReportType} activity report.
            </DialogDescription>
          </DialogHeader>

          {viewingReport && (
            <div className="space-y-4 py-4">
              {viewingReportType === 'daily' && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Date</Label>
                      <p className="mt-1">{viewingReport.report_date ? formatDate(viewingReport.report_date) : 'N/A'}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Status</Label>
                      <div className="mt-1">{getStatusBadge(viewingReport.status)}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Sessions Conducted</Label>
                      <p className="mt-1">{viewingReport.sessions_conducted || 0}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Crisis Interventions</Label>
                      <p className="mt-1">{viewingReport.crisis_interventions || 0}</p>
                    </div>
                  </div>
                  {viewingReport.key_highlights && (
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Key Highlights</Label>
                      <p className="mt-1 p-3 bg-gray-50 rounded-md">{viewingReport.key_highlights}</p>
                    </div>
                  )}
                </>
              )}

              {viewingReportType === 'weekly' && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Week Period</Label>
                      <p className="mt-1">
                        {viewingReport.week_start_date && viewingReport.week_end_date 
                          ? `${formatDate(viewingReport.week_start_date)} - ${formatDate(viewingReport.week_end_date)}`
                          : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Status</Label>
                      <div className="mt-1">{getStatusBadge(viewingReport.status)}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Total Sessions</Label>
                      <p className="mt-1">{viewingReport.total_sessions || 0}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Total Students</Label>
                      <p className="mt-1">{viewingReport.total_students || 0}</p>
                    </div>
                  </div>
                  {viewingReport.summary && (
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Summary</Label>
                      <p className="mt-1 p-3 bg-gray-50 rounded-md">{viewingReport.summary}</p>
                    </div>
                  )}
                  {viewingReport.challenges && (
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Challenges</Label>
                      <p className="mt-1 p-3 bg-gray-50 rounded-md">{viewingReport.challenges}</p>
                    </div>
                  )}
                </>
              )}

              {viewingReportType === 'monthly' && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Month</Label>
                      <p className="mt-1">
                        {viewingReport.report_month 
                          ? new Date(viewingReport.report_month).toLocaleDateString('en-IN', { year: 'numeric', month: 'long' })
                          : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Status</Label>
                      <div className="mt-1">{getStatusBadge(viewingReport.status)}</div>
                    </div>
                  </div>
                  {viewingReport.executive_summary && (
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Executive Summary</Label>
                      <p className="mt-1 p-3 bg-gray-50 rounded-md">{viewingReport.executive_summary}</p>
                    </div>
                  )}
                  {viewingReport.recommendations && (
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Recommendations</Label>
                      <p className="mt-1 p-3 bg-gray-50 rounded-md">{viewingReport.recommendations}</p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            <Button 
              onClick={() => viewingReport && downloadPdf(viewingReportType, viewingReport.report_id)}
              className="text-white"
              style={{ backgroundColor: CITTAA_COLORS.teal }}
            >
              <Download className="h-4 w-4 mr-2" />
              Download PDF
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
