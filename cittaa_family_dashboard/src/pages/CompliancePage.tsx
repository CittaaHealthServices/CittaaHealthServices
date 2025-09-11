import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  ArrowLeft, 
  Shield, 
  CheckCircle, 
  FileText,
  Scale,
  Globe,
  Users,
  Download,
  Eye,
  Lock,
  AlertTriangle
} from 'lucide-react'
import { useFamily } from '@/contexts/FamilyContext'

export default function CompliancePage() {
  const { children, consentOverview } = useFamily()

  const complianceFrameworks = [
    {
      id: 'dpdp_2023',
      name: 'DPDP Act 2023',
      description: 'Digital Personal Data Protection Act 2023 compliance',
      status: 'compliant',
      requirements: [
        'Lawful basis for processing children\'s data',
        'Verifiable parental consent for children under 18',
        'Data minimization principles strictly followed',
        'Right to erasure implemented with clear procedures',
        'Transparent privacy notices in age-appropriate language'
      ]
    },
    {
      id: 'coppa',
      name: 'COPPA',
      description: 'Children\'s Online Privacy Protection Act compliance',
      status: 'compliant',
      requirements: [
        'Parental consent for children under 13',
        'No behavioral advertising to children',
        'Limited data collection from children',
        'Safe harbor provisions followed',
        'Clear privacy policy for children\'s services'
      ]
    },
    {
      id: 'gdpr',
      name: 'GDPR Article 8',
      description: 'EU General Data Protection Regulation compliance',
      status: 'compliant',
      requirements: [
        'Enhanced protections for children under 16',
        'Parental consent verification systems',
        'Data protection by design and default',
        'Regular privacy impact assessments',
        'Child-friendly privacy explanations'
      ]
    },
    {
      id: 'un_crc',
      name: 'UN Convention on Rights of Child',
      description: 'International children\'s rights compliance',
      status: 'compliant',
      requirements: [
        'Best interests of the child principle',
        'Right to privacy and protection',
        'Age-appropriate participation in decisions',
        'Protection from harmful content',
        'Educational and developmental support'
      ]
    }
  ]

  const auditLogs = [
    {
      id: 1,
      timestamp: new Date().toISOString(),
      action: 'Consent Updated',
      user: 'Parent: Rajesh Sharma',
      details: 'Updated content filtering consent for Aarav (Age 12)',
      compliance: 'DPDP Act 2023'
    },
    {
      id: 2,
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      action: 'Data Access Request',
      user: 'Child: Priya Sharma',
      details: 'Requested access to personal data collected',
      compliance: 'GDPR Article 15'
    },
    {
      id: 3,
      timestamp: new Date(Date.now() - 7200000).toISOString(),
      action: 'Privacy Policy Updated',
      user: 'System',
      details: 'Age-appropriate privacy explanations updated',
      compliance: 'DPDP Act 2023'
    }
  ]

  const getComplianceScore = () => {
    if (consentOverview.length === 0) return 100

    let totalRequiredConsents = 0
    let totalGivenConsents = 0

    consentOverview.forEach(child => {
      const consents = Object.values(child.consents)
      totalRequiredConsents += consents.length
      totalGivenConsents += consents.filter((c: any) => c.given).length
    })

    return totalRequiredConsents > 0 ? Math.round((totalGivenConsents / totalRequiredConsents) * 100) : 100
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16 space-x-4">
            <Button variant="ghost" asChild>
              <Link to="/dashboard">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Link>
            </Button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Compliance Dashboard</h1>
              <p className="text-sm text-gray-600">Regulatory compliance and audit trail</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{getComplianceScore()}%</div>
              <p className="text-xs text-muted-foreground">
                Overall compliance rating
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Frameworks</CardTitle>
              <Scale className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{complianceFrameworks.length}</div>
              <p className="text-xs text-muted-foreground">
                Regulatory frameworks
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Audit Events</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{auditLogs.length}</div>
              <p className="text-xs text-muted-foreground">
                Recent audit entries
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Data Subjects</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{children.length}</div>
              <p className="text-xs text-muted-foreground">
                Protected children
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="frameworks" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="frameworks">Compliance Frameworks</TabsTrigger>
            <TabsTrigger value="consent">Consent Management</TabsTrigger>
            <TabsTrigger value="audit">Audit Trail</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="frameworks" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {complianceFrameworks.map((framework) => (
                <Card key={framework.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>{framework.name}</span>
                      <Badge variant={framework.status === 'compliant' ? 'default' : 'destructive'}>
                        {framework.status === 'compliant' ? 'Compliant' : 'Non-Compliant'}
                      </Badge>
                    </CardTitle>
                    <CardDescription>{framework.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <h4 className="font-medium">Key Requirements:</h4>
                      <div className="space-y-2">
                        {framework.requirements.map((requirement, index) => (
                          <div key={index} className="flex items-start space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                            <span className="text-sm">{requirement}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="consent" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Consent Management Overview</CardTitle>
                <CardDescription>
                  Age-appropriate consent tracking and compliance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {consentOverview.map((child) => (
                    <Card key={child.child_id}>
                      <CardHeader>
                        <CardTitle className="text-lg">
                          {child.child_name} (Age {child.age})
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {Object.entries(child.consents).map(([type, consent]: [string, any]) => (
                            <div key={type} className="p-3 border rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium capitalize">
                                  {type.replace('_', ' ')}
                                </h4>
                                {consent.given ? (
                                  <CheckCircle className="h-5 w-5 text-green-600" />
                                ) : (
                                  <AlertTriangle className="h-5 w-5 text-red-600" />
                                )}
                              </div>
                              <div className="text-sm text-gray-600 space-y-1">
                                <p>Status: {consent.given ? 'Consented' : 'Not Consented'}</p>
                                {consent.date && (
                                  <p>Date: {new Date(consent.date).toLocaleDateString()}</p>
                                )}
                                {consent.parent_consent && (
                                  <Badge variant="secondary" className="text-xs">
                                    Parent Consent
                                  </Badge>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="audit" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Audit Trail</span>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Export Logs
                  </Button>
                </CardTitle>
                <CardDescription>
                  Complete audit trail of all compliance-related activities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {auditLogs.map((log) => (
                    <div key={log.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="p-2 bg-blue-100 rounded-full">
                          <FileText className="h-4 w-4 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-medium">{log.action}</h4>
                          <p className="text-sm text-gray-600">{log.details}</p>
                          <p className="text-xs text-gray-500">
                            {log.user} • {new Date(log.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <Badge variant="outline">{log.compliance}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reports" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Compliance Reports</CardTitle>
                  <CardDescription>
                    Generate detailed compliance documentation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button className="w-full justify-start">
                    <FileText className="h-4 w-4 mr-2" />
                    DPDP Act 2023 Compliance Report
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Globe className="h-4 w-4 mr-2" />
                    GDPR Compliance Assessment
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Users className="h-4 w-4 mr-2" />
                    Children's Privacy Impact Assessment
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <Eye className="h-4 w-4 mr-2" />
                    Transparency Report
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Data Subject Rights</CardTitle>
                  <CardDescription>
                    Manage data subject requests and rights
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-3 border rounded-lg">
                    <h4 className="font-medium mb-2">Right to Access</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      Children and parents can request access to all collected data
                    </p>
                    <Button size="sm" variant="outline">
                      Process Request
                    </Button>
                  </div>

                  <div className="p-3 border rounded-lg">
                    <h4 className="font-medium mb-2">Right to Erasure</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      Complete data deletion with verification procedures
                    </p>
                    <Button size="sm" variant="outline">
                      Process Deletion
                    </Button>
                  </div>

                  <div className="p-3 border rounded-lg">
                    <h4 className="font-medium mb-2">Data Portability</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      Export data in machine-readable format
                    </p>
                    <Button size="sm" variant="outline">
                      Export Data
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Privacy by Design</CardTitle>
                <CardDescription>
                  Built-in privacy protections and compliance measures
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <Lock className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <h4 className="font-medium">Data Minimization</h4>
                    <p className="text-sm text-gray-600">
                      Only collect necessary data for safety purposes
                    </p>
                  </div>

                  <div className="text-center p-4 border rounded-lg">
                    <Eye className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <h4 className="font-medium">Transparency</h4>
                    <p className="text-sm text-gray-600">
                      Clear explanations for all data processing
                    </p>
                  </div>

                  <div className="text-center p-4 border rounded-lg">
                    <Users className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                    <h4 className="font-medium">User Control</h4>
                    <p className="text-sm text-gray-600">
                      Granular consent and easy withdrawal options
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
