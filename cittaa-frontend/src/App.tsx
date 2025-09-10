import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ChildPasswordEntry from './components/ChildPasswordEntry'
import ChildDashboard from './components/ChildDashboard'
import ParentDashboard from './components/ParentDashboard'
import SchoolDashboard from './components/SchoolDashboard'
import HospitalDashboard from './components/HospitalDashboard'
import ContentBlocked from './components/ContentBlocked'
import CulturalContent from './components/CulturalContent'
import Analytics from './components/Analytics'
import EmergencyOverride from './components/EmergencyOverride'
import ComplianceDashboard from './components/ComplianceDashboard'
import DeviceSync from './components/DeviceSync'
import VPNAlert from './components/VPNAlert'

function App() {
  const [currentUser, setCurrentUser] = useState<any>(null)

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Routes>
          <Route path="/" element={<ChildPasswordEntry onLogin={setCurrentUser} />} />
          <Route path="/child-dashboard" element={<ChildDashboard user={currentUser} />} />
          <Route path="/parent-dashboard" element={<ParentDashboard user={currentUser} />} />
          <Route path="/school-dashboard" element={<SchoolDashboard user={currentUser} />} />
          <Route path="/hospital-dashboard" element={<HospitalDashboard user={currentUser} />} />
          <Route path="/content-blocked" element={<ContentBlocked />} />
          <Route path="/cultural-content/:region" element={<CulturalContent />} />
          <Route path="/analytics" element={<Analytics user={currentUser} />} />
          <Route path="/emergency-override" element={<EmergencyOverride />} />
          <Route path="/compliance" element={<ComplianceDashboard />} />
          <Route path="/device-sync" element={<DeviceSync />} />
          <Route path="/vpn-alert" element={<VPNAlert />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
