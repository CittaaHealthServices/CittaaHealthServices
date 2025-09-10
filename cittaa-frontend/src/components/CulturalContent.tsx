import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { MapPin, Calendar, Utensils, Music, Palette, ArrowLeft } from 'lucide-react'

export default function CulturalContent() {
  const { region } = useParams<{ region: string }>()
  const [language, setLanguage] = useState('english')
  const navigate = useNavigate()

  const culturalData = {
    tamil_nadu: {
      name: 'Tamil Nadu',
      flag: '🇮🇳',
      festivals: ['Pongal', 'Diwali', 'Tamil New Year'],
      traditions: ['Classical Dance', 'Temple Architecture', 'Tamil Literature'],
      food: ['Sambar', 'Rasam', 'Idli', 'Dosa'],
      colors: 'from-red-400 to-yellow-400'
    },
    maharashtra: {
      name: 'Maharashtra',
      flag: '🇮🇳',
      festivals: ['Ganesh Chaturthi', 'Gudi Padwa', 'Navratri'],
      traditions: ['Lavani Dance', 'Warli Art', 'Marathi Literature'],
      food: ['Vada Pav', 'Puran Poli', 'Misal Pav'],
      colors: 'from-orange-400 to-red-400'
    },
    west_bengal: {
      name: 'West Bengal',
      flag: '🇮🇳',
      festivals: ['Durga Puja', 'Kali Puja', 'Poila Boishakh'],
      traditions: ['Rabindra Sangeet', 'Bengali Literature', 'Terracotta Art'],
      food: ['Fish Curry', 'Rasgulla', 'Sandesh'],
      colors: 'from-yellow-400 to-green-400'
    }
  }

  const currentRegion = culturalData[region as keyof typeof culturalData] || culturalData.tamil_nadu

  const translations = {
    english: {
      title: 'Indian Cultural Learning',
      upcoming: 'Upcoming: Diwali Festival',
      todaysContent: "Today's Cultural Content:",
      regionalFocus: 'Regional Focus:',
      familyValues: 'Family Values Module:',
      respectElders: 'Respect for elders',
      jointFamily: 'Joint family importance',
      traditions: 'Cultural traditions',
      exploreMore: 'Explore More',
      parentGuide: 'Parent Guide',
      festivals: 'Festivals',
      culture: 'Traditions',
      cuisine: 'Cuisine'
    },
    hindi: {
      title: 'भारतीय सांस्कृतिक शिक्षा',
      upcoming: 'आगामी: दिवाली त्योहार',
      todaysContent: 'आज की सांस्कृतिक सामग्री:',
      regionalFocus: 'क्षेत्रीय फोकस:',
      familyValues: 'पारिवारिक मूल्य मॉड्यूल:',
      respectElders: 'बुजुर्गों का सम्मान',
      jointFamily: 'संयुक्त परिवार का महत्व',
      traditions: 'सांस्कृतिक परंपराएं',
      exploreMore: 'और अन्वेषण करें',
      parentGuide: 'माता-पिता गाइड',
      festivals: 'त्योहार',
      culture: 'परंपराएं',
      cuisine: 'व्यंजन'
    }
  }

  const t = translations[language as keyof typeof translations]

  const culturalContent = [
    { icon: '🕉️', title: 'Sanskrit Slokas', category: 'spiritual' },
    { icon: '🎨', title: 'Rangoli Patterns', category: 'art' },
    { icon: '📖', title: 'Panchatantra Stories', category: 'literature' },
    { icon: '🎵', title: 'Classical Music Basics', category: 'music' },
    { icon: '🍽️', title: 'Traditional Recipes', category: 'food' }
  ]

  const handleBack = () => {
    navigate('/child-dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-green-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-3xl shadow-xl p-6 animate-slide-in">
          {/* Header */}
          <div className="border-b border-gray-200 pb-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <button
                  onClick={handleBack}
                  className="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <ArrowLeft className="w-6 h-6 text-gray-600" />
                </button>
                <div>
                  <h1 className="text-2xl font-bold text-gray-800 flex items-center">
                    🇮🇳 {t.title}
                  </h1>
                  <p className="text-gray-600">{currentRegion.flag} {currentRegion.name}</p>
                </div>
              </div>
              <div className="cultural-gradient w-16 h-16 rounded-full flex items-center justify-center festival-glow">
                <span className="text-2xl">🎉</span>
              </div>
            </div>
          </div>

          {/* Upcoming Festival */}
          <div className="bg-gradient-to-r from-orange-100 to-yellow-100 rounded-xl p-4 mb-6">
            <div className="flex items-center">
              <Calendar className="w-6 h-6 mr-3 text-orange-600" />
              <span className="font-medium text-gray-800">{t.upcoming}</span>
            </div>
          </div>

          {/* Today's Cultural Content */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">{t.todaysContent}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {culturalContent.map((content, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-4 hover:shadow-lg transition-all duration-300 cursor-pointer animate-bounce-gentle"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="text-center">
                    <div className="text-3xl mb-2">{content.icon}</div>
                    <div className="font-medium text-gray-800">{content.title}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Regional Focus */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <MapPin className="w-6 h-6 mr-2 text-blue-600" />
              {t.regionalFocus} {currentRegion.name}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Festivals */}
              <div className="bg-red-50 rounded-xl p-4">
                <h3 className="font-semibold text-red-700 mb-3 flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  {t.festivals}
                </h3>
                <ul className="space-y-2">
                  {currentRegion.festivals.map((festival, index) => (
                    <li key={index} className="text-gray-700">• {festival}</li>
                  ))}
                </ul>
              </div>

              {/* Traditions */}
              <div className="bg-blue-50 rounded-xl p-4">
                <h3 className="font-semibold text-blue-700 mb-3 flex items-center">
                  <Palette className="w-5 h-5 mr-2" />
                  {t.culture}
                </h3>
                <ul className="space-y-2">
                  {currentRegion.traditions.map((tradition, index) => (
                    <li key={index} className="text-gray-700">• {tradition}</li>
                  ))}
                </ul>
              </div>

              {/* Food */}
              <div className="bg-green-50 rounded-xl p-4">
                <h3 className="font-semibold text-green-700 mb-3 flex items-center">
                  <Utensils className="w-5 h-5 mr-2" />
                  {t.cuisine}
                </h3>
                <ul className="space-y-2">
                  {currentRegion.food.map((food, index) => (
                    <li key={index} className="text-gray-700">• {food}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Family Values Module */}
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">👨‍👩‍👧‍👦 {t.familyValues}</h2>
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-6">
              <ul className="space-y-3">
                <li className="flex items-center text-gray-700">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  • {t.respectElders}
                </li>
                <li className="flex items-center text-gray-700">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  • {t.jointFamily}
                </li>
                <li className="flex items-center text-gray-700">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                  • {t.traditions}
                </li>
              </ul>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 mb-6">
            <button className="flex items-center px-6 py-3 cittaa-primary rounded-xl font-medium hover:bg-blue-700 transition-colors">
              <Music className="w-5 h-5 mr-2" />
              {t.exploreMore}
            </button>
            <button className="flex items-center px-6 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700 transition-colors">
              <Palette className="w-5 h-5 mr-2" />
              {t.parentGuide}
            </button>
          </div>

          {/* Language Toggle */}
          <div className="flex justify-center space-x-2">
            <button
              onClick={() => setLanguage('hindi')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                language === 'hindi' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => setLanguage('english')}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                language === 'english' ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              English
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
