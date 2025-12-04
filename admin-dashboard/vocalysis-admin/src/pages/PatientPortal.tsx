import { useState, useEffect } from 'react';
import { 
  Mic, 
  TrendingUp, 
  Calendar, 
  Activity,
  Heart,
  Brain,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  Download
} from 'lucide-react';

// Mock data - will be replaced with real API calls
const mockAnalysisHistory = [
  {
    id: '1',
    date: '2024-12-04',
    mental_health_score: 78,
    phq9_score: 4,
    gad7_score: 5,
    pss_score: 12,
    wemwbs_score: 52,
    risk_level: 'low',
    predicted_condition: 'Normal',
    confidence: 0.87
  },
  {
    id: '2',
    date: '2024-12-01',
    mental_health_score: 72,
    phq9_score: 6,
    gad7_score: 7,
    pss_score: 15,
    wemwbs_score: 48,
    risk_level: 'moderate',
    predicted_condition: 'Mild Anxiety',
    confidence: 0.82
  },
  {
    id: '3',
    date: '2024-11-28',
    mental_health_score: 68,
    phq9_score: 8,
    gad7_score: 9,
    pss_score: 18,
    wemwbs_score: 45,
    risk_level: 'moderate',
    predicted_condition: 'Moderate Anxiety',
    confidence: 0.79
  }
];

const getRiskColor = (risk: string) => {
  switch (risk) {
    case 'low': return 'text-[#10B981] bg-[#10B981]/10';
    case 'moderate': return 'text-[#F59E0B] bg-[#F59E0B]/10';
    case 'high': return 'text-[#F97316] bg-[#F97316]/10';
    case 'critical': return 'text-[#DC2626] bg-[#DC2626]/10';
    default: return 'text-gray-500 bg-gray-100';
  }
};

const getScoreColor = (score: number) => {
  if (score >= 70) return 'text-[#10B981]';
  if (score >= 50) return 'text-[#F59E0B]';
  if (score >= 30) return 'text-[#F97316]';
  return 'text-[#DC2626]';
};

const getSeverityLabel = (scale: string, score: number) => {
  if (scale === 'phq9') {
    if (score <= 4) return { label: 'Minimal', color: 'text-[#10B981]' };
    if (score <= 9) return { label: 'Mild', color: 'text-[#F59E0B]' };
    if (score <= 14) return { label: 'Moderate', color: 'text-[#F97316]' };
    return { label: 'Severe', color: 'text-[#DC2626]' };
  }
  if (scale === 'gad7') {
    if (score <= 4) return { label: 'Minimal', color: 'text-[#10B981]' };
    if (score <= 9) return { label: 'Mild', color: 'text-[#F59E0B]' };
    if (score <= 14) return { label: 'Moderate', color: 'text-[#F97316]' };
    return { label: 'Severe', color: 'text-[#DC2626]' };
  }
  if (scale === 'pss') {
    if (score <= 13) return { label: 'Low', color: 'text-[#10B981]' };
    if (score <= 26) return { label: 'Moderate', color: 'text-[#F59E0B]' };
    return { label: 'High', color: 'text-[#DC2626]' };
  }
  if (scale === 'wemwbs') {
    if (score >= 52) return { label: 'Good', color: 'text-[#10B981]' };
    if (score >= 40) return { label: 'Average', color: 'text-[#F59E0B]' };
    return { label: 'Low', color: 'text-[#DC2626]' };
  }
  return { label: 'Unknown', color: 'text-gray-500' };
};

export default function PatientPortal() {
  const [analysisHistory, setAnalysisHistory] = useState(mockAnalysisHistory);
  const [selectedAnalysis, setSelectedAnalysis] = useState(mockAnalysisHistory[0]);
  const [isLoading, setIsLoading] = useState(false);

  // In production, this would fetch from the API
  useEffect(() => {
    // fetchAnalysisHistory();
  }, []);

  const latestAnalysis = analysisHistory[0];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">My Mental Health Dashboard</h1>
        <p className="text-gray-600 mt-1">Track your voice analysis results and mental health progress</p>
      </div>

      {/* Latest Score Card */}
      <div className="bg-gradient-to-br from-[#8B5A96] to-[#7BB3A8] rounded-2xl p-6 text-white mb-8">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/80 text-sm">Latest Mental Health Score</p>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-5xl font-bold">{latestAnalysis.mental_health_score}</span>
              <span className="text-white/80">/100</span>
            </div>
            <p className="text-white/80 text-sm mt-2">
              Last analyzed: {new Date(latestAnalysis.date).toLocaleDateString()}
            </p>
          </div>
          <div className="text-right">
            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
              latestAnalysis.risk_level === 'low' ? 'bg-white/20' : 'bg-white/30'
            }`}>
              {latestAnalysis.risk_level === 'low' ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <AlertCircle className="w-5 h-5" />
              )}
              <span className="font-medium capitalize">{latestAnalysis.risk_level} Risk</span>
            </div>
            <p className="text-white/80 text-sm mt-3">
              Confidence: {(latestAnalysis.confidence * 100).toFixed(0)}%
            </p>
          </div>
        </div>
      </div>

      {/* Clinical Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {/* PHQ-9 Depression */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-[#DC2626]/10 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-[#DC2626]" />
            </div>
            <div>
              <p className="text-xs text-gray-500">PHQ-9</p>
              <p className="text-sm font-medium text-gray-700">Depression</p>
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-bold text-gray-900">{latestAnalysis.phq9_score}</span>
            <span className={`text-sm font-medium ${getSeverityLabel('phq9', latestAnalysis.phq9_score).color}`}>
              {getSeverityLabel('phq9', latestAnalysis.phq9_score).label}
            </span>
          </div>
          <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-[#DC2626] rounded-full transition-all"
              style={{ width: `${(latestAnalysis.phq9_score / 27) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">Scale: 0-27</p>
        </div>

        {/* GAD-7 Anxiety */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-[#F59E0B]/10 rounded-lg flex items-center justify-center">
              <Activity className="w-5 h-5 text-[#F59E0B]" />
            </div>
            <div>
              <p className="text-xs text-gray-500">GAD-7</p>
              <p className="text-sm font-medium text-gray-700">Anxiety</p>
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-bold text-gray-900">{latestAnalysis.gad7_score}</span>
            <span className={`text-sm font-medium ${getSeverityLabel('gad7', latestAnalysis.gad7_score).color}`}>
              {getSeverityLabel('gad7', latestAnalysis.gad7_score).label}
            </span>
          </div>
          <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-[#F59E0B] rounded-full transition-all"
              style={{ width: `${(latestAnalysis.gad7_score / 21) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">Scale: 0-21</p>
        </div>

        {/* PSS Stress */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-[#F97316]/10 rounded-lg flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-[#F97316]" />
            </div>
            <div>
              <p className="text-xs text-gray-500">PSS</p>
              <p className="text-sm font-medium text-gray-700">Stress</p>
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-bold text-gray-900">{latestAnalysis.pss_score}</span>
            <span className={`text-sm font-medium ${getSeverityLabel('pss', latestAnalysis.pss_score).color}`}>
              {getSeverityLabel('pss', latestAnalysis.pss_score).label}
            </span>
          </div>
          <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-[#F97316] rounded-full transition-all"
              style={{ width: `${(latestAnalysis.pss_score / 40) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">Scale: 0-40</p>
        </div>

        {/* WEMWBS Wellbeing */}
        <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-[#10B981]/10 rounded-lg flex items-center justify-center">
              <Heart className="w-5 h-5 text-[#10B981]" />
            </div>
            <div>
              <p className="text-xs text-gray-500">WEMWBS</p>
              <p className="text-sm font-medium text-gray-700">Wellbeing</p>
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-bold text-gray-900">{latestAnalysis.wemwbs_score}</span>
            <span className={`text-sm font-medium ${getSeverityLabel('wemwbs', latestAnalysis.wemwbs_score).color}`}>
              {getSeverityLabel('wemwbs', latestAnalysis.wemwbs_score).label}
            </span>
          </div>
          <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className="h-full bg-[#10B981] rounded-full transition-all"
              style={{ width: `${((latestAnalysis.wemwbs_score - 14) / 56) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">Scale: 14-70</p>
        </div>
      </div>

      {/* Analysis History */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-5 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Analysis History</h2>
            <button className="flex items-center gap-2 text-[#8B5A96] hover:text-[#5D3D66] text-sm font-medium">
              <Download className="w-4 h-4" />
              Export Report
            </button>
          </div>
        </div>
        <div className="divide-y divide-gray-100">
          {analysisHistory.map((analysis) => (
            <div 
              key={analysis.id}
              className="p-5 hover:bg-gray-50 transition-colors cursor-pointer"
              onClick={() => setSelectedAnalysis(analysis)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#8B5A96]/10 to-[#7BB3A8]/10 rounded-xl flex items-center justify-center">
                    <Mic className="w-6 h-6 text-[#8B5A96]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-gray-900">Voice Analysis</p>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getRiskColor(analysis.risk_level)}`}>
                        {analysis.risk_level.charAt(0).toUpperCase() + analysis.risk_level.slice(1)} Risk
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {new Date(analysis.date).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {analysis.predicted_condition}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-2xl font-bold ${getScoreColor(analysis.mental_health_score)}`}>
                    {analysis.mental_health_score}
                  </p>
                  <p className="text-xs text-gray-500">Mental Health Score</p>
                </div>
              </div>
              
              {/* Clinical Scores Summary */}
              <div className="mt-4 grid grid-cols-4 gap-4">
                <div className="text-center p-2 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">PHQ-9</p>
                  <p className="font-semibold text-[#DC2626]">{analysis.phq9_score}</p>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">GAD-7</p>
                  <p className="font-semibold text-[#F59E0B]">{analysis.gad7_score}</p>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">PSS</p>
                  <p className="font-semibold text-[#F97316]">{analysis.pss_score}</p>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-500">WEMWBS</p>
                  <p className="font-semibold text-[#10B981]">{analysis.wemwbs_score}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations Card */}
      <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Personalized Recommendations</h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-[#10B981]/5 rounded-lg border border-[#10B981]/20">
            <CheckCircle className="w-5 h-5 text-[#10B981] mt-0.5" />
            <div>
              <p className="font-medium text-gray-900">Continue your current wellness routine</p>
              <p className="text-sm text-gray-600 mt-1">Your mental health score is in a healthy range. Keep up the good work!</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-[#8B5A96]/5 rounded-lg border border-[#8B5A96]/20">
            <Brain className="w-5 h-5 text-[#8B5A96] mt-0.5" />
            <div>
              <p className="font-medium text-gray-900">Practice mindfulness exercises</p>
              <p className="text-sm text-gray-600 mt-1">Consider 10-15 minutes of daily meditation to maintain emotional balance.</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-[#7BB3A8]/5 rounded-lg border border-[#7BB3A8]/20">
            <Activity className="w-5 h-5 text-[#7BB3A8] mt-0.5" />
            <div>
              <p className="font-medium text-gray-900">Regular voice check-ins</p>
              <p className="text-sm text-gray-600 mt-1">Record a voice sample every 2-3 days to track your mental health trends.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
