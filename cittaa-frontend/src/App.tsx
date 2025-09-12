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
import ForgotPassword from './components/ForgotPassword'
import type { User } from './types'

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null)

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-[#F3F4F6] to-white">
        <Routes>
          <Route path="/" element={<ChildPasswordEntry onLogin={setCurrentUser} />} />
          <Route path="/child-dashboard" element={<ChildDashboard user={currentUser} />} />
          <Route path="/parent-dashboard" element={<ParentDashboard />} />
          <Route path="/school-dashboard" element={<SchoolDashboard />} />
          <Route path="/hospital-dashboard" element={<HospitalDashboard />} />
          <Route path="/content-blocked" element={<ContentBlocked />} />
          <Route path="/cultural-content/:region" element={<CulturalContent />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/emergency-override" element={<EmergencyOverride />} />
          <Route path="/compliance" element={<ComplianceDashboard />} />
          <Route path="/device-sync" element={<DeviceSync />} />
          <Route path="/vpn-alert" element={<VPNAlert />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
