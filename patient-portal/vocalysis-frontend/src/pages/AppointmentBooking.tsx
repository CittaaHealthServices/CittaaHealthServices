import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Calendar, Clock, User, MapPin, Phone, Star, ChevronRight } from 'lucide-react'
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
}

interface Appointment {
  id: string
  patient_id: string
  doctor_id: string
  appointment_date: string
  duration_minutes: number
  appointment_type: string
  status: string
  notes?: string
  created_at: string
}

export default function AppointmentBooking() {
  const { user } = useAuth()
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null)
  const [selectedDate, setSelectedDate] = useState('')
  const [selectedTime, setSelectedTime] = useState('')
  const [appointmentType, setAppointmentType] = useState('consultation')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [activeTab, setActiveTab] = useState<'book' | 'upcoming'>('book')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [doctorsRes, appointmentsRes] = await Promise.all([
        axios.get('/api/v1/doctors'),
        axios.get('/api/v1/appointments')
      ])
      setDoctors(doctorsRes.data)
      setAppointments(appointmentsRes.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
      setError('Failed to load data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleBookAppointment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedDoctor || !selectedDate || !selectedTime) {
      setError('Please fill in all required fields')
      return
    }

    setSubmitting(true)
    setError('')

    try {
      const appointmentDateTime = new Date(`${selectedDate}T${selectedTime}:00`)
      
      await axios.post('/api/v1/appointments', {
        doctor_id: selectedDoctor.user_id,
        appointment_date: appointmentDateTime.toISOString(),
        duration_minutes: 60,
        appointment_type: appointmentType,
        notes: notes
      })

      setSuccess('Appointment booked successfully!')
      setSelectedDoctor(null)
      setSelectedDate('')
      setSelectedTime('')
      setNotes('')
      setActiveTab('upcoming')
      fetchData()
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to book appointment')
    } finally {
      setSubmitting(false)
    }
  }

  const getMinDate = () => {
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    return tomorrow.toISOString().split('T')[0]
  }

  const getAvailableTimeSlots = () => {
    if (!selectedDoctor) return []
    
    const slots = [
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
      '17:00', '17:30'
    ]
    
    return slots
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800'
      case 'confirmed':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      case 'completed':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
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
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('book')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'book'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Book Appointment
            </button>
            <button
              onClick={() => setActiveTab('upcoming')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'upcoming'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              My Appointments ({appointments.length})
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'book' ? (
            <div className="space-y-6">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}
              
              {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                  {success}
                </div>
              )}

              {!selectedDoctor ? (
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    Choose a Healthcare Provider
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {doctors.length > 0 ? (
                      doctors.map((doctor) => (
                        <div
                          key={doctor.id}
                          className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-200 cursor-pointer"
                          onClick={() => setSelectedDoctor(doctor)}
                        >
                          <div className="flex items-start space-x-4">
                            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
                              <User className="w-8 h-8 text-white" />
                            </div>
                            <div className="flex-1">
                              <h3 className="text-lg font-medium text-gray-900">
                                Dr. {doctor.full_name || 'Healthcare Provider'}
                              </h3>
                              <p className="text-sm text-gray-600 mb-2">
                                {doctor.specialization}
                              </p>
                              <div className="flex items-center space-x-4 text-sm text-gray-500 mb-2">
                                <span>{doctor.experience_years} years experience</span>
                                <div className="flex items-center">
                                  <Star className="w-4 h-4 text-yellow-400 mr-1" />
                                  <span>{doctor.rating.toFixed(1)} ({doctor.total_reviews} reviews)</span>
                                </div>
                              </div>
                              <p className="text-sm text-gray-600 mb-3">
                                Languages: {doctor.languages.join(', ')}
                              </p>
                              <div className="flex items-center justify-between">
                                <span className="text-lg font-semibold text-green-600">
                                  ₹{doctor.consultation_fee}
                                </span>
                                <ChevronRight className="w-5 h-5 text-gray-400" />
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="col-span-2 text-center py-8">
                        <User className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                        <p className="text-gray-500">No healthcare providers available</p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">
                      Book Appointment with Dr. {selectedDoctor.full_name}
                    </h2>
                    <button
                      onClick={() => setSelectedDoctor(null)}
                      className="text-sm text-blue-600 hover:text-blue-700"
                    >
                      ← Choose different doctor
                    </button>
                  </div>

                  <form onSubmit={handleBookAppointment} className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Preferred Date
                        </label>
                        <div className="relative">
                          <Calendar className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                          <input
                            type="date"
                            value={selectedDate}
                            onChange={(e) => setSelectedDate(e.target.value)}
                            min={getMinDate()}
                            required
                            className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Preferred Time
                        </label>
                        <div className="relative">
                          <Clock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                          <select
                            value={selectedTime}
                            onChange={(e) => setSelectedTime(e.target.value)}
                            required
                            className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">Select time</option>
                            {getAvailableTimeSlots().map((time) => (
                              <option key={time} value={time}>
                                {time}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Appointment Type
                      </label>
                      <select
                        value={appointmentType}
                        onChange={(e) => setAppointmentType(e.target.value)}
                        className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="consultation">General Consultation</option>
                        <option value="follow-up">Follow-up</option>
                        <option value="therapy">Therapy Session</option>
                        <option value="assessment">Mental Health Assessment</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Additional Notes (Optional)
                      </label>
                      <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        rows={3}
                        className="block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Any specific concerns or symptoms you'd like to discuss..."
                      />
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">Appointment Summary</h4>
                      <div className="space-y-1 text-sm text-gray-600">
                        <p>Doctor: Dr. {selectedDoctor.full_name}</p>
                        <p>Specialization: {selectedDoctor.specialization}</p>
                        <p>Date: {selectedDate ? new Date(selectedDate).toLocaleDateString() : 'Not selected'}</p>
                        <p>Time: {selectedTime || 'Not selected'}</p>
                        <p>Duration: 60 minutes</p>
                        <p className="font-medium text-gray-900">Fee: ₹{selectedDoctor.consultation_fee}</p>
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={submitting}
                      className="w-full bg-gradient-to-r from-blue-600 to-green-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                    >
                      {submitting ? (
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                          Booking...
                        </div>
                      ) : (
                        'Book Appointment'
                      )}
                    </button>
                  </form>
                </div>
              )}
            </div>
          ) : (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                My Appointments
              </h2>
              {appointments.length > 0 ? (
                <div className="space-y-4">
                  {appointments.map((appointment) => (
                    <div
                      key={appointment.id}
                      className="bg-white border border-gray-200 rounded-lg p-6"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="text-lg font-medium text-gray-900">
                              {appointment.appointment_type.charAt(0).toUpperCase() + appointment.appointment_type.slice(1)}
                            </h3>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(appointment.status)}`}>
                              {appointment.status}
                            </span>
                          </div>
                          <div className="space-y-1 text-sm text-gray-600">
                            <div className="flex items-center">
                              <Calendar className="w-4 h-4 mr-2" />
                              {new Date(appointment.appointment_date).toLocaleDateString()}
                            </div>
                            <div className="flex items-center">
                              <Clock className="w-4 h-4 mr-2" />
                              {new Date(appointment.appointment_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                            <div className="flex items-center">
                              <User className="w-4 h-4 mr-2" />
                              Duration: {appointment.duration_minutes} minutes
                            </div>
                          </div>
                          {appointment.notes && (
                            <p className="mt-2 text-sm text-gray-600">
                              <strong>Notes:</strong> {appointment.notes}
                            </p>
                          )}
                        </div>
                        <div className="ml-4">
                          {appointment.status === 'scheduled' && (
                            <button className="text-sm text-red-600 hover:text-red-700">
                              Cancel
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No appointments scheduled</p>
                  <button
                    onClick={() => setActiveTab('book')}
                    className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Book your first appointment
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
