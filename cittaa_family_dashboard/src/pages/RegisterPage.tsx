import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Shield, Users, Heart, CheckCircle } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { familyApi } from '@/lib/api'

export default function RegisterPage() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    family_name: '',
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
    confirmPassword: ''
  })
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    console.log('Form submission started')
    console.log('Form data from state:', formData)

    const form = e.target as HTMLFormElement
    const formDataDOM = new FormData(form)
    
    const family_name = formData.family_name || formDataDOM.get('family_name') as string || ''
    const full_name = formData.full_name || formDataDOM.get('full_name') as string || ''
    const email = formData.email || formDataDOM.get('email') as string || ''
    const phone_number = formData.phone_number || formDataDOM.get('phone_number') as string || ''
    const password = formData.password || formDataDOM.get('password') as string || ''
    const confirmPassword = formData.confirmPassword || formDataDOM.get('confirmPassword') as string || ''

    console.log('Extracted values:', { family_name, full_name, email, phone_number, password: '***', confirmPassword: '***' })

    if (!email || !password || !full_name || !family_name) {
      setError('Please fill in all required fields')
      setLoading(false)
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long')
      setLoading(false)
      return
    }

    try {
      console.log('Calling registration API...')
      const response = await familyApi.register({
        email,
        password,
        full_name,
        phone_number: phone_number || undefined,
        family_name
      })
      
      console.log('Registration successful, logging in...')
      login((response as any).access_token, (response as any).parent_id, (response as any).family_id)
      navigate('/dashboard')
    } catch (err: any) {
      console.error('Registration error:', err)
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl space-y-6">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="bg-blue-600 p-3 rounded-full">
              <Shield className="h-8 w-8 text-white" />
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Your Family Account</h1>
            <p className="text-gray-600 mt-2">Join CITTAA's transparent family safety platform</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center p-4 bg-white rounded-lg shadow-sm">
            <Shield className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-semibold">Transparent Protection</h3>
            <p className="text-sm text-gray-600">Children understand all safety measures</p>
          </div>
          <div className="text-center p-4 bg-white rounded-lg shadow-sm">
            <Users className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <h3 className="font-semibold">Age-Appropriate Consent</h3>
            <p className="text-sm text-gray-600">Proper consent for all age groups</p>
          </div>
          <div className="text-center p-4 bg-white rounded-lg shadow-sm">
            <Heart className="h-8 w-8 text-red-500 mx-auto mb-2" />
            <h3 className="font-semibold">Family Communication</h3>
            <p className="text-sm text-gray-600">Open discussions about digital safety</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Family Registration</CardTitle>
            <CardDescription>
              Create your transparent family safety account with full DPDP Act 2023 compliance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} method="post" className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="family_name">Family Name</Label>
                  <Input
                    id="family_name"
                    name="family_name"
                    value={formData.family_name}
                    onChange={(e) => {
                      console.log('Family name input changed:', e.target.value);
                      handleInputChange(e);
                    }}
                    required
                    placeholder="The Sharma Family"
                    autoComplete="organization"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="full_name">Your Full Name</Label>
                  <Input
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={(e) => {
                      console.log('Full name input changed:', e.target.value);
                      handleInputChange(e);
                    }}
                    required
                    placeholder="Rajesh Sharma"
                    autoComplete="name"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    placeholder="rajesh@example.com"
                    autoComplete="email"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="phone_number">Phone Number (Optional)</Label>
                  <Input
                    id="phone_number"
                    name="phone_number"
                    type="tel"
                    value={formData.phone_number}
                    onChange={handleInputChange}
                    placeholder="+91 98765 43210"
                    autoComplete="tel"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    placeholder="Minimum 8 characters"
                    autoComplete="new-password"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    required
                    placeholder="Confirm your password"
                    autoComplete="new-password"
                  />
                </div>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg space-y-2">
                <h4 className="font-semibold text-blue-900">Compliance Commitment</h4>
                <div className="space-y-1 text-sm text-blue-800">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>Full transparency with children about all safety measures</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>Age-appropriate consent mechanisms for all features</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>Complete DPDP Act 2023 and children's privacy compliance</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4" />
                    <span>Educational approach to digital citizenship</span>
                  </div>
                </div>
              </div>
              
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? 'Creating Account...' : 'Create Family Account'}
              </Button>
            </form>
            
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600">
                Already have an account?{' '}
                <Link to="/login" className="text-blue-600 hover:underline">
                  Sign in here
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
