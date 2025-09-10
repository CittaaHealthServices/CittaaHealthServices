import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { 
  User, 
  Star, 
  MapPin, 
  Clock, 
  Phone, 
  Mail, 
  Award, 
  Calendar,
  MessageCircle,
  Filter,
  Search
} from 'lucide-react'
import { Link } from 'react-router-dom'
import axios from 'axios'

interface Doctor {
  id: string
  user_id: string
  specialization: string
  experience_years: number
  qualifications: string[]
  languages: string[]
  consultation_fee: number
  available_slots: string[]
  rating: number
  total_reviews: number
  bio?: string
  profile_image?: string
  full_name?: string
  created_at: string
  updated_at: string
}

export default function DoctorProfiles() {
  const { user } = useAuth()
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [filteredDoctors, setFilteredDoctors] = useState<Doctor[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSpecialization, setSelectedSpecialization] = useState('')
  const [selectedLanguage, setSelectedLanguage] = useState('')
  const [sortBy, setSortBy] = useState<'rating' | 'experience' | 'fee'>('rating')
  const [error, setError] = useState('')

  useEffect(() => {
    fetchDoctors()
  }, [])

  useEffect(() => {
    filterAndSortDoctors()
  }, [doctors, searchTerm, selectedSpecialization, selectedLanguage, sortBy])

  const fetchDoctors = async () => {
    try {
      const response = await axios.get('/api/v1/doctors')
      setDoctors(response.data)
    } catch (error) {
      console.error('Failed to fetch doctors:', error)
      setError('Failed to load doctors. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const filterAndSortDoctors = () => {
    let filtered = [...doctors]

    if (searchTerm) {
      filtered = filtered.filter(doctor =>
        doctor.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doctor.specialization.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doctor.bio?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (selectedSpecialization) {
      filtered = filtered.filter(doctor =>
        doctor.specialization === selectedSpecialization
      )
    }

    if (selectedLanguage) {
      filtered = filtered.filter(doctor =>
        doctor.languages.includes(selectedLanguage)
      )
    }

    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating
        case 'experience':
          return b.experience_years - a.experience_years
        case 'fee':
          return a.consultation_fee - b.consultation_fee
        default:
          return 0
      }
    })

    setFilteredDoctors(filtered)
  }

  const getUniqueSpecializations = () => {
    return [...new Set(doctors.map(doctor => doctor.specialization))]
  }

  const getUniqueLanguages = () => {
    const allLanguages = doctors.flatMap(doctor => doctor.languages)
    return [...new Set(allLanguages)]
  }

  const renderStars = (rating: number) => {
    const stars: React.ReactElement[] = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 !== 0

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
      )
    }

    if (hasHalfStar) {
      stars.push(
        <Star key="half" className="w-4 h-4 text-yellow-400 fill-current opacity-50" />
      )
    }

    const emptyStars = 5 - Math.ceil(rating)
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <Star key={`empty-${i}`} className="w-4 h-4 text-gray-300" />
      )
    }

    return stars
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-2xl p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Find Healthcare Providers</h1>
        <p className="text-blue-100">
          Connect with qualified mental health professionals
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search doctors..."
                className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Specialization
            </label>
            <select
              value={selectedSpecialization}
              onChange={(e) => setSelectedSpecialization(e.target.value)}
              className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Specializations</option>
              {getUniqueSpecializations().map((spec) => (
                <option key={spec} value={spec}>
                  {spec}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Languages</option>
              {getUniqueLanguages().map((lang) => (
                <option key={lang} value={lang}>
                  {lang}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'rating' | 'experience' | 'fee')}
              className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="rating">Highest Rated</option>
              <option value="experience">Most Experienced</option>
              <option value="fee">Lowest Fee</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            {filteredDoctors.length} Healthcare Provider{filteredDoctors.length !== 1 ? 's' : ''} Found
          </h2>
        </div>

        <div className="p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {filteredDoctors.length > 0 ? (
            <div className="space-y-6">
              {filteredDoctors.map((doctor) => (
                <div
                  key={doctor.id}
                  className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-200"
                >
                  <div className="flex flex-col lg:flex-row lg:items-start lg:space-x-6">
                    {/* Profile Image */}
                    <div className="flex-shrink-0 mb-4 lg:mb-0">
                      <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
                        <User className="w-12 h-12 text-white" />
                      </div>
                    </div>

                    {/* Doctor Info */}
                    <div className="flex-1">
                      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
                        <div className="flex-1">
                          <h3 className="text-xl font-semibold text-gray-900 mb-1">
                            Dr. {doctor.full_name || 'Healthcare Provider'}
                          </h3>
                          
                          <p className="text-blue-600 font-medium mb-2">
                            {doctor.specialization}
                          </p>

                          <div className="flex items-center space-x-1 mb-3">
                            {renderStars(doctor.rating)}
                            <span className="text-sm text-gray-600 ml-2">
                              {doctor.rating.toFixed(1)} ({doctor.total_reviews} reviews)
                            </span>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div className="flex items-center text-sm text-gray-600">
                              <Award className="w-4 h-4 mr-2" />
                              {doctor.experience_years} years experience
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
                              <MessageCircle className="w-4 h-4 mr-2" />
                              Languages: {doctor.languages.join(', ')}
                            </div>
                          </div>

                          {doctor.qualifications && doctor.qualifications.length > 0 && (
                            <div className="mb-4">
                              <h4 className="text-sm font-medium text-gray-900 mb-2">Qualifications</h4>
                              <div className="flex flex-wrap gap-2">
                                {doctor.qualifications.map((qual, index) => (
                                  <span
                                    key={index}
                                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                                  >
                                    {qual}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {doctor.bio && (
                            <p className="text-sm text-gray-600 mb-4">
                              {doctor.bio}
                            </p>
                          )}
                        </div>

                        {/* Actions */}
                        <div className="flex-shrink-0 lg:ml-6">
                          <div className="text-right mb-4">
                            <p className="text-2xl font-bold text-green-600">
                              ₹{doctor.consultation_fee}
                            </p>
                            <p className="text-sm text-gray-500">per consultation</p>
                          </div>

                          <div className="space-y-2">
                            <Link
                              to="/appointments"
                              state={{ selectedDoctor: doctor }}
                              className="w-full bg-gradient-to-r from-blue-600 to-green-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-green-700 transition-all duration-200 text-center block"
                            >
                              <Calendar className="w-4 h-4 inline mr-2" />
                              Book Appointment
                            </Link>
                            
                            <Link
                              to="/messages"
                              state={{ doctorId: doctor.user_id }}
                              className="w-full bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors duration-200 text-center block"
                            >
                              <MessageCircle className="w-4 h-4 inline mr-2" />
                              Send Message
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No healthcare providers found
              </h3>
              <p className="text-gray-500 mb-4">
                Try adjusting your search criteria or filters
              </p>
              <button
                onClick={() => {
                  setSearchTerm('')
                  setSelectedSpecialization('')
                  setSelectedLanguage('')
                }}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
