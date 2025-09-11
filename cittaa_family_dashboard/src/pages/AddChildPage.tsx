import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useFamily } from '../contexts/FamilyContext'
import { useToast } from '../hooks/use-toast'
import { familyApi } from '../lib/api'

function AddChildPage() {
  const navigate = useNavigate()
  const { token } = useAuth()
  const { refreshFamily } = useFamily()
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    fullName: '',
    age: '',
    dateOfBirth: '',
    safetyPassword: '',
    confirmPassword: '',
    biometricEnabled: false
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.safetyPassword !== formData.confirmPassword) {
      toast({
        title: "Password Mismatch",
        description: "Safety passwords do not match",
        variant: "destructive"
      })
      return
    }

    const dateValue = formData.dateOfBirth
    if (!dateValue || dateValue.length !== 10) {
      toast({
        title: "Invalid Date",
        description: "Please enter a valid date in YYYY-MM-DD format",
        variant: "destructive"
      })
      return
    }

    const dateParts = dateValue.split('-')
    if (dateParts.length !== 3) {
      toast({
        title: "Invalid Date Format",
        description: "Please enter date in YYYY-MM-DD format (e.g., 2010-03-15)",
        variant: "destructive"
      })
      return
    }

    const year = parseInt(dateParts[0])
    const month = parseInt(dateParts[1])
    const day = parseInt(dateParts[2])

    if (year < 1900 || year > new Date().getFullYear() || month < 1 || month > 12 || day < 1 || day > 31) {
      toast({
        title: "Invalid Date",
        description: "Please enter a valid date",
        variant: "destructive"
      })
      return
    }

    const isoDate = `${year.toString().padStart(4, '0')}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`

    setLoading(true)
    try {
      if (!token) {
        throw new Error('No authentication token found')
      }
      
      await familyApi.createChild(token, {
        full_name: formData.fullName,
        age: parseInt(formData.age),
        date_of_birth: isoDate,
        safety_password: formData.safetyPassword
      })
      
      await refreshFamily()
      toast({
        title: "Child Added Successfully",
        description: `${formData.fullName} has been added to your family with transparent safety protection.`
      })
      navigate('/dashboard')
    } catch (error) {
      console.error('Error creating child:', error)
      toast({
        title: "Error Adding Child",
        description: "Failed to add child to family. Please try again.",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center mb-8">
          <div className="mx-auto h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center">
            <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">Add Child Profile</h2>
          <p className="mt-2 text-sm text-gray-600">
            Create a transparent safety profile with age-appropriate consent
          </p>
        </div>

        <div className="bg-white py-8 px-6 shadow rounded-lg">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700">
                Child's Full Name
              </label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                required
                value={formData.fullName}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter child's full name"
              />
            </div>

            <div>
              <label htmlFor="age" className="block text-sm font-medium text-gray-700">
                Age
              </label>
              <input
                id="age"
                name="age"
                type="number"
                min="1"
                max="18"
                required
                value={formData.age}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Child's age"
              />
            </div>

            <div>
              <label htmlFor="dateOfBirth" className="block text-sm font-medium text-gray-700">
                Date of Birth
              </label>
              <input
                id="dateOfBirth"
                name="dateOfBirth"
                type="text"
                required
                value={formData.dateOfBirth}
                onChange={handleInputChange}
                placeholder="YYYY-MM-DD (e.g., 2010-03-15)"
                pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">
                Format: YYYY-MM-DD (e.g., 2010-03-15)
              </p>
            </div>

            <div>
              <label htmlFor="safetyPassword" className="block text-sm font-medium text-gray-700">
                Safety Password
              </label>
              <input
                id="safetyPassword"
                name="safetyPassword"
                type="password"
                required
                value={formData.safetyPassword}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Create a safety password for your child"
              />
              <p className="mt-1 text-xs text-gray-500">
                This password will activate transparent safety protection when your child uses their device
              </p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm Safety Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Confirm the safety password"
              />
            </div>

            <div className="flex items-center">
              <input
                id="biometricEnabled"
                name="biometricEnabled"
                type="checkbox"
                checked={formData.biometricEnabled}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="biometricEnabled" className="ml-2 block text-sm text-gray-900">
                Enable transparent biometric authentication
              </label>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    Transparent Safety Commitment
                  </h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Your child will know when safety protection is active</li>
                      <li>All content blocking will include educational explanations</li>
                      <li>Age-appropriate consent will be obtained for all features</li>
                      <li>Your child can ask questions about any safety measures</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => navigate('/dashboard')}
                className="flex-1 py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading ? 'Adding Child...' : 'Add Child'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

const AddChildPageComponent = AddChildPage
export default AddChildPageComponent
