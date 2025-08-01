import { useState, useEffect } from 'react'
import './App.css'
import adventurous from './assets/images/adventurous.png'
import comforting from './assets/images/comforting.png'
import energizing from './assets/images/energizing.png'
import romantic from './assets/images/romantic.png'
import cozy from './assets/images/cozy.png'
import festive from './assets/images/festive.png'
import indulgent from './assets/images/indulgent.png'
import refreshing from './assets/images/refreshing.png'

// API base URL
const API_BASE_URL = 'https://backend-restless-meadow-2397.fly.dev'

/**
 * Array of mood images with their corresponding names and sources
 */
const moodImages = [
  { name: 'Adventurous', src: adventurous },
  { name: 'Comforting', src: comforting },
  { name: 'Energizing', src: energizing },
  { name: 'Romantic', src: romantic },
  { name: 'Cozy', src: cozy },
  { name: 'Festive', src: festive },
  { name: 'Indulgent', src: indulgent },
  { name: 'Refreshing', src: refreshing }
]

/**
 * Main App component for restaurant recommendation system
 * @returns {JSX.Element} The main application component
 */
function App() {
  // State management for application
  const [selectedMood, setSelectedMood] = useState('Adventurous')
  const [recommendation, setRecommendation] = useState('')
  const [originalRecommendation, setOriginalRecommendation] = useState('')
  const [showTranslation, setShowTranslation] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('English')
  const [loading, setLoading] = useState(false)
  const [translating, setTranslating] = useState(false)
  const [userLocation, setUserLocation] = useState('Atlanta, GA')



  /**
   * Gets user's location using geolocation API
   */
  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const { latitude, longitude } = position.coords
            // Use reverse geocoding to get city/state
            const response = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`)
            const data = await response.json()
            const location = `${data.city}, ${data.principalSubdivision}`
            setUserLocation(location)
          } catch (error) {
            console.log('Geocoding failed, using default location')
          }
        },
        (error) => {
          console.log('Geolocation failed, using default location')
        }
      )
    }
  }

  // Get user location on component mount
  useEffect(() => {
    getUserLocation()
  }, [])

  /**
   * Fetches restaurant recommendation from backend API
   * @param {string} mood - Selected mood for recommendation
   */
  const getRecommendation = async (mood) => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mood: mood || selectedMood,
          location: userLocation 
        })
      })
      const data = await response.json()
      if (data.error) {
        setRecommendation(data.error)
      } else {
        const lines = data.recommendation.split('\n').filter(line => line.trim())
        setRecommendation(lines)
        setOriginalRecommendation(lines)
        setShowTranslation(true)
      }
    } catch (error) {
      setRecommendation('Error getting recommendation')
    }
    setLoading(false)
  }

  // Auto-scroll to bottom when recommendation appears
  useEffect(() => {
    if (recommendation) {
      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
      }, 100)
    }
  }, [recommendation])



  /**
   * Translates recommendation text to selected language
   * Replaces the original recommendation with translated version
   */
  const translateText = async () => {
    if (selectedLanguage === 'English') {
      setRecommendation(originalRecommendation)
      return
    }
    setTranslating(true)
    try {
      const originalText = originalRecommendation.join('\n')
      const response = await fetch(`${API_BASE_URL}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: originalText, language: selectedLanguage })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      const translatedLines = data.translated_text.split('\n').filter(line => line.trim())
      
      setRecommendation(translatedLines)
    } catch (error) {
      console.error('Translation error:', error)
      setRecommendation(['Translation error: ' + error.message])
    }
    setTranslating(false)
  }

  return (
    <div className="app">
      <h1>What type of restaurant are you in the mood for?</h1>
      
      <div className="mood-gallery">
        {moodImages.map((mood) => (
          <button
            key={mood.name}
            className={`mood-button ${loading && selectedMood === mood.name ? 'loading' : ''}`}
            onClick={() => {
              setSelectedMood(mood.name)
              setShowTranslation(false)
              setRecommendation('')
              setOriginalRecommendation('')
              setSelectedLanguage('English')
              getRecommendation(mood.name)
            }}
            disabled={loading}
          >
            <img src={mood.src} alt={mood.name} />
            {loading && selectedMood === mood.name && <div className="loading-overlay">Finding...</div>}
          </button>
        ))}
      </div>

      {recommendation && Array.isArray(recommendation) && (
        <div className="recommendation">
          <ol>
            {recommendation.map((line, index) => (
              <li key={index} dangerouslySetInnerHTML={{ __html: line }}></li>
            ))}
          </ol>
        </div>
      )}

      {showTranslation && (
        <div className="translation-section">
          <select 
            value={selectedLanguage} 
            onChange={(e) => {
              setSelectedLanguage(e.target.value)
              if (e.target.value === 'English') {
                setRecommendation(originalRecommendation)
              }
            }}
          >
            <option value="English">English</option>
            <option value="Spanish">Spanish</option>
            <option value="French">French</option>
            <option value="German">German</option>
            <option value="Romanian">Romanian</option>
          </select>
          <button onClick={translateText} disabled={translating}>
            {translating ? 'Translating...' : 'Translate'}
          </button>
        </div>
      )}
    </div>
  )
}

export default App