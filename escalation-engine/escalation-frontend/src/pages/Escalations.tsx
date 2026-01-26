import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Search, Download, Eye,
  Clock, CheckCircle
} from 'lucide-react';
import { CITTAA_COLORS, ESCALATION_COLORS, formatDateTime, getEscalationLevelText } from '@/lib/utils';

interface EscalationCase {
  case_id: string;
  student_id: string;
  psychologist_id: string;
  institution_id: string;
  escalation_level: string;
  risk_category: string;
  ai_confidence_score: number;
  keywords_detected: string[];
  escalation_reason: string;
  status: string;
  escalated_at: string;
  resolved_at: string | null;
}

export default function Escalations() {
  const [cases, setCases] = useState<EscalationCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [levelFilter, setLevelFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCases();
  }, [statusFilter, levelFilter]);

  const loadCases = async () => {
    setIsLoading(true);
    try {
      const data = await api.getEscalationCases({
        status_filter: statusFilter || undefined,
        level_filter: levelFilter || undefined,
        days: 30,
      });
      setCases(data as EscalationCase[]);
    } catch (error) {
      console.error('Failed to load escalation cases:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getLevelBadgeStyle = (level: string) => {
    const color = ESCALATION_COLORS[level as keyof typeof ESCALATION_COLORS] || CITTAA_COLORS.warmGray;
    return {
      backgroundColor: `${color}20`,
      color: color,
      borderColor: color,
    };
  };

  const getStatusBadgeStyle = (status: string) => {
    const colors: Record<string, string> = {
      open: ESCALATION_COLORS.level_3_high,
      in_progress: CITTAA_COLORS.teal,
      resolved: '#059669',
      referred: CITTAA_COLORS.purple,
    };
    const color = colors[status] || CITTAA_COLORS.warmGray;
    return {
      backgroundColor: `${color}20`,
      color: color,
    };
  };

  const filteredCases = cases.filter(c => 
    searchTerm === '' || 
    c.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.risk_category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
            Escalation Cases
          </h1>
          <p className="text-gray-500 mt-1">
            Monitor and manage AI-detected risk cases
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search cases..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border rounded-md text-sm"
              >
                <option value="">All Status</option>
                <option value="open">Open</option>
                <option value="in_progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="referred">Referred</option>
              </select>
              <select
                value={levelFilter}
                onChange={(e) => setLevelFilter(e.target.value)}
                className="px-3 py-2 border rounded-md text-sm"
              >
                <option value="">All Levels</option>
                <option value="level_4_emergency">Emergency</option>
                <option value="level_3_high">High Risk</option>
                <option value="level_2_moderate">Moderate</option>
                <option value="level_1_low">Low</option>
              </select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
              <p className="mt-2 text-gray-500">Loading cases...</p>
            </div>
          ) : filteredCases.length === 0 ? (
            <div className="text-center py-8">
              <CheckCircle className="h-12 w-12 mx-auto mb-2" style={{ color: CITTAA_COLORS.teal }} />
              <p className="text-gray-500">No escalation cases found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredCases.map((caseItem) => (
                <div
                  key={caseItem.case_id}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
                  style={{ 
                    borderLeftWidth: '4px',
                    borderLeftColor: ESCALATION_COLORS[caseItem.escalation_level as keyof typeof ESCALATION_COLORS] || CITTAA_COLORS.warmGray
                  }}
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Badge style={getLevelBadgeStyle(caseItem.escalation_level)}>
                          {getEscalationLevelText(caseItem.escalation_level)}
                        </Badge>
                        <Badge variant="outline" style={getStatusBadgeStyle(caseItem.status)}>
                          {caseItem.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                        {caseItem.ai_confidence_score && (
                          <span className="text-xs text-gray-500">
                            AI Confidence: {(caseItem.ai_confidence_score * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-medium" style={{ color: CITTAA_COLORS.darkText }}>
                        {caseItem.risk_category?.replace('_', ' ').toUpperCase() || 'General Concern'}
                      </p>
                      <p className="text-sm text-gray-500 line-clamp-2">
                        {caseItem.escalation_reason || 'No description provided'}
                      </p>
                      {caseItem.keywords_detected && caseItem.keywords_detected.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {caseItem.keywords_detected.slice(0, 3).map((keyword, idx) => (
                            <span 
                              key={idx}
                              className="text-xs px-2 py-0.5 rounded-full"
                              style={{ 
                                backgroundColor: `${ESCALATION_COLORS.level_3_high}15`,
                                color: ESCALATION_COLORS.level_3_high
                              }}
                            >
                              {keyword}
                            </span>
                          ))}
                          {caseItem.keywords_detected.length > 3 && (
                            <span className="text-xs text-gray-400">
                              +{caseItem.keywords_detected.length - 3} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Clock className="h-3 w-3" />
                        {formatDateTime(caseItem.escalated_at)}
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
                          style={{ borderColor: CITTAA_COLORS.teal, color: CITTAA_COLORS.teal }}
                        >
                          <Download className="h-4 w-4 mr-1" />
                          PDF
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
