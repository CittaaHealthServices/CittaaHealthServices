import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Shield, Heart, Users } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { familyApi } from '@/lib/api'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const formData = new FormData(e.target as HTMLFormElement)
    const emailValue = formData.get('email') as string
    const passwordValue = formData.get('password') as string

    console.log('Login attempt with:', { email: emailValue, password: passwordValue ? '***' : 'empty' })

    try {
      const response = await familyApi.login({ email: emailValue, password: passwordValue })
      console.log('Login response:', response)
      login((response as any).access_token, (response as any).parent_id, (response as any).family_id)
      navigate('/dashboard')
    } catch (err: any) {
      console.error('Login error:', err)
      setError(err.message || 'Invalid email or password. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="bg-[#8B5A96] p-3 rounded-full">
              <Shield className="h-8 w-8 text-white" />
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-[#8B5A96]">CITTAA Family Safety</h1>
            <p className="text-gray-600 mt-2">Transparent & Compliant Digital Protection</p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Parent Login</CardTitle>
            <CardDescription>
              Access your family's transparent safety dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(e) => {
                    console.log('Email onChange:', e.target.value)
                    setEmail(e.target.value)
                  }}
                  required
                  placeholder="parent@example.com"
                  autoComplete="email"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={password}
                  onChange={(e) => {
                    console.log('Password onChange:', e.target.value)
                    setPassword(e.target.value)
                  }}
                  required
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
              </div>
              
              <Button type="submit" className="w-full bg-[#8B5A96] hover:bg-[#8B5A96]/90" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>
            
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <Link to="/register" className="text-[#8B5A96] hover:underline">
                  Create a family account
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="space-y-2">
            <Shield className="h-6 w-6 text-[#8B5A96] mx-auto" />
            <p className="text-xs text-gray-600">Transparent Protection</p>
          </div>
          <div className="space-y-2">
            <Heart className="h-6 w-6 text-[#7BB3A8] mx-auto" />
            <p className="text-xs text-gray-600">Family Communication</p>
          </div>
          <div className="space-y-2">
            <Users className="h-6 w-6 text-[#7BB3A8] mx-auto" />
            <p className="text-xs text-gray-600">Age-Appropriate Consent</p>
          </div>
        </div>
      </div>
    </div>
  )
}
