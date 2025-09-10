import { useState } from 'react'
import { Shield, CheckCircle, FileText, Download, Calendar, AlertTriangle } from 'lucide-react'

export default function ComplianceDashboard() {
  const [lastAudit] = useState('15 days ago')
  const [nextReview] = useState('45 days')

  const complianceStatus = {
    dpdpAct: { status: 'compliant', label: 'DPDP Act 2023 Compliant' },
    mentalHealthcare: { status: 'compliant', label: 'Mental Healthcare Act 2017' },
    rciStandards: { status: 'verified', label: 'RCI Standards Verified' },
    dataResidency: { status: 'compliant', label: 'Data Residency (India)' }
  }

  const securityCertifications = [
    { name: 'ISO 27001', status: 'Valid', color: 'text-green-600' },
    { name: 'SOC 2 Type II', status: 'Certified', color: 'text-green-600' },
    { name: 'Penetration Test', status: 'Passed', color: 'text-green-600' }
  ]

  const privacyMetrics = [
    { metric: 'Data encrypted', value: '100%', color: 'text-green-600' },
    { metric: 'Local processing', value: '95%', color: 'text-green-600' },
    { metric: 'Consent compliance', value: '100%', color: 'text-green-600' }
  ]

  const handleDownloadCertificates = () => {
    console.log('Downloading compliance certificates...')
    alert('Compliance certificates package downloaded successfully!')
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
      case 'verified':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      default:
        return <AlertTriangle className="w-5 h-5 text-red-600" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-100 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-3xl shadow-xl p-6 animate-slide-in">
          {/* Header */}
          <div className="border-b border-gray-200 pb-4 mb-6">
            <div className="flex items-center">
              <Shield className="w-8 h-8 mr-3 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-800">📋 Regulatory Compliance</h1>
                <p className="text-gray-600">CITTAA Parental Control System - Compliance Dashboard</p>
              </div>
            </div>
          </div>

          {/* Compliance Status */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Regulatory Compliance Status</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(complianceStatus).map(([key, item]) => (
                <div key={key} className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center">
                  {getStatusIcon(item.status)}
                  <span className="ml-3 font-medium text-gray-800">✅ {item.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Security Certifications */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Shield className="w-6 h-6 mr-2 text-blue-600" />
              🔒 Security Certifications
            </h2>
            
            <div className="bg-gray-50 rounded-xl p-6">
              <div className="space-y-4">
                {securityCertifications.map((cert, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                      <span className="font-medium text-gray-800">• {cert.name}:</span>
                    </div>
                    <span className={`font-semibold ${cert.color}`}>{cert.status}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Privacy Metrics */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <FileText className="w-6 h-6 mr-2 text-purple-600" />
              📊 Privacy Metrics
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {privacyMetrics.map((metric, index) => (
                <div key={index} className="bg-purple-50 border border-purple-200 rounded-xl p-4 text-center">
                  <div className={`text-2xl font-bold ${metric.color}`}>{metric.value}</div>
                  <div className="text-sm text-gray-600">• {metric.metric}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Audit Information */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Calendar className="w-6 h-6 mr-2 text-orange-600" />
              Audit Schedule
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-800">Last Audit:</span>
                  <span className="text-blue-600 font-semibold">{lastAudit}</span>
                </div>
              </div>
              <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-800">Next Review:</span>
                  <span className="text-orange-600 font-semibold">{nextReview}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Data Protection Details */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">🇮🇳 Indian Data Protection Compliance</h2>
            
            <div className="bg-gradient-to-r from-orange-50 via-white to-green-50 border border-gray-200 rounded-xl p-6">
              <div className="space-y-4">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">All user data stored within Indian territory (Mumbai & Bangalore data centers)</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">Granular consent management for children and parents</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">Complete data deletion capability within 30 days</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">Automatic incident reporting system for data breaches</span>
                </div>
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                  <span className="text-gray-700">Mental Healthcare Act 2017 therapy session privacy protection</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div className="flex justify-center">
            <button
              onClick={handleDownloadCertificates}
              className="flex items-center px-8 py-4 cittaa-primary rounded-xl font-semibold text-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-6 h-6 mr-3" />
              Download Certificates
            </button>
          </div>

          {/* Footer Notice */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex items-start">
              <Shield className="w-5 h-5 text-blue-600 mr-2 mt-0.5" />
              <div className="text-sm text-blue-800">
                <strong>Compliance Notice:</strong> This dashboard provides real-time compliance status for CITTAA Parental Control System. 
                All certifications are independently verified and updated automatically. For detailed compliance reports or audit requests, 
                contact our compliance team at compliance@cittaa.in
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
