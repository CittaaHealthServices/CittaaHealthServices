import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  GraduationCap, Search, Plus, Eye, History,
  User, AlertTriangle
} from 'lucide-react';
import { CITTAA_COLORS, ESCALATION_COLORS, formatDate } from '@/lib/utils';

interface Student {
  student_id: string;
  anonymized_code: string;
  grade: string;
  section?: string;
  institution_id: string;
  date_of_birth?: string;
  gender?: string;
  current_risk_level?: string;
  is_active: boolean;
  created_at: string;
}

export default function Students() {
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [gradeFilter, setGradeFilter] = useState('');

  useEffect(() => {
    loadStudents();
  }, [gradeFilter]);

  const loadStudents = async () => {
    setIsLoading(true);
    try {
      const data = await api.getStudents({
        grade: gradeFilter || undefined,
      });
      setStudents(data as Student[]);
    } catch (error) {
      console.error('Failed to load students:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskBadge = (riskLevel?: string) => {
    if (!riskLevel) return null;
    
    const colors: Record<string, string> = {
      high: ESCALATION_COLORS.level_3_high,
      moderate: ESCALATION_COLORS.level_2_moderate,
      low: ESCALATION_COLORS.level_1_low,
    };
    const color = colors[riskLevel] || CITTAA_COLORS.warmGray;
    
    return (
      <Badge 
        className="flex items-center gap-1"
        style={{ backgroundColor: `${color}20`, color: color }}
      >
        {riskLevel === 'high' && <AlertTriangle className="h-3 w-3" />}
        {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)} Risk
      </Badge>
    );
  };

  const filteredStudents = students.filter(s => 
    searchTerm === '' || 
    s.anonymized_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.grade?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const grades = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold" style={{ color: CITTAA_COLORS.purple }}>
            Students
          </h1>
          <p className="text-gray-500 mt-1">
            Manage student records with anonymized identifiers
          </p>
        </div>
        <Button 
          className="text-white"
          style={{ backgroundColor: CITTAA_COLORS.purple }}
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Student
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by code or grade..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={gradeFilter}
              onChange={(e) => setGradeFilter(e.target.value)}
              className="px-3 py-2 border rounded-md text-sm"
            >
              <option value="">All Grades</option>
              {grades.map(grade => (
                <option key={grade} value={grade}>Grade {grade}</option>
              ))}
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto" style={{ borderColor: CITTAA_COLORS.purple }}></div>
              <p className="mt-2 text-gray-500">Loading students...</p>
            </div>
          ) : filteredStudents.length === 0 ? (
            <div className="text-center py-12">
              <GraduationCap className="h-12 w-12 mx-auto mb-4" style={{ color: CITTAA_COLORS.warmGray }} />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No students found</h3>
              <p className="text-gray-500 mb-4">Add students to start tracking their counseling sessions</p>
              <Button 
                className="text-white"
                style={{ backgroundColor: CITTAA_COLORS.purple }}
              >
                <Plus className="h-4 w-4 mr-2" />
                Add First Student
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredStudents.map((student) => (
                <div
                  key={student.student_id}
                  className="border rounded-lg p-4 hover:shadow-md transition-all duration-200"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-10 h-10 rounded-full flex items-center justify-center"
                        style={{ backgroundColor: `${CITTAA_COLORS.purple}20` }}
                      >
                        <User className="h-5 w-5" style={{ color: CITTAA_COLORS.purple }} />
                      </div>
                      <div>
                        <p className="font-medium text-sm" style={{ color: CITTAA_COLORS.darkText }}>
                          {student.anonymized_code}
                        </p>
                        <p className="text-xs text-gray-500">
                          Grade {student.grade}{student.section ? ` - ${student.section}` : ''}
                        </p>
                      </div>
                    </div>
                    {getRiskBadge(student.current_risk_level)}
                  </div>
                  
                  <div className="space-y-1 text-sm text-gray-500 mb-3">
                    {student.gender && (
                      <p>Gender: {student.gender}</p>
                    )}
                    <p>Added: {formatDate(student.created_at)}</p>
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="flex-1"
                      style={{ borderColor: CITTAA_COLORS.purple, color: CITTAA_COLORS.purple }}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="flex-1"
                      style={{ borderColor: CITTAA_COLORS.teal, color: CITTAA_COLORS.teal }}
                    >
                      <History className="h-4 w-4 mr-1" />
                      History
                    </Button>
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
