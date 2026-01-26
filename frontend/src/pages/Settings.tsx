import { useAuth } from '../contexts/AuthContext'
import { User, Mail, Shield, Globe, Calendar, Phone } from 'lucide-react'

export default function Settings() {
  const { user } = useAuth()

  const formatRole = (role: string) => {
    return role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'Not available'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-400 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold">Account Settings</h1>
        <p className="mt-1 text-white/80">
          View your account information and preferences
        </p>
      </div>

      {/* Profile Information */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-800 mb-6">Profile Information</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Full Name */}
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <User className="w-5 h-5 text-primary-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Full Name</p>
              <p className="font-medium text-gray-800">{user?.full_name || 'Not set'}</p>
            </div>
          </div>

          {/* Email */}
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-secondary-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Mail className="w-5 h-5 text-secondary-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Email Address</p>
              <p className="font-medium text-gray-800">{user?.email || 'Not set'}</p>
            </div>
          </div>

          {/* Role */}
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Shield className="w-5 h-5 text-accent-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Account Role</p>
              <p className="font-medium text-gray-800">{user?.role ? formatRole(user.role) : 'Not set'}</p>
            </div>
          </div>

          {/* Phone */}
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Phone className="w-5 h-5 text-primary-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Phone Number</p>
              <p className="font-medium text-gray-800">{user?.phone || 'Not set'}</p>
            </div>
          </div>

          {/* Language */}
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-secondary-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Globe className="w-5 h-5 text-secondary-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Language Preference</p>
              <p className="font-medium text-gray-800 capitalize">{user?.language_preference || 'English'}</p>
            </div>
          </div>

          {/* Account Created */}
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <Calendar className="w-5 h-5 text-accent-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Account Created</p>
              <p className="font-medium text-gray-800">{formatDate(user?.created_at)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Security Section */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Security</h2>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-gray-600">
            To change your password, please use the "Forgot Password" option on the login page. 
            A password reset link will be sent to your registered email address.
          </p>
        </div>
      </div>

      {/* Account Status */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Account Status</h2>
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${user?.is_active ? 'bg-success' : 'bg-error'}`} />
          <span className="text-gray-700">
            {user?.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
        {user?.is_clinical_trial_participant && (
          <div className="mt-3 flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${
              user?.trial_status === 'approved' ? 'bg-success' : 
              user?.trial_status === 'pending' ? 'bg-warning' : 'bg-gray-400'
            }`} />
            <span className="text-gray-700">
              Clinical Trial: {user?.trial_status ? formatRole(user.trial_status) : 'Not enrolled'}
            </span>
          </div>
        )}
      </div>

      {/* Coming Soon */}
      <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-2">Coming Soon</h2>
        <p className="text-gray-600">
          Profile editing, notification preferences, and more settings options will be available in future updates.
        </p>
      </div>
    </div>
  )
}
