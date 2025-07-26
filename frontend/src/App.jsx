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
const API_BASE_URL = 'https://restaurant-recommendation-daad.onrender.com'

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

  /**
   * Formats recommendation text by adding emojis to field labels
   * @param {string} text - Raw recommendation text
   * @returns {Array<string>} Formatted lines with emojis
   */
  const formatRecommendation = (text) => {
    const lines = text.split('\n').filter(line => line.trim())
    const formattedLines = lines.map(line => {
      if (line.startsWith('**') && line.includes(':')) {
        const match = line.match(/\*\*([^*]+):\*\*/)
        if (match) {
          const fieldName = match[1].toLowerCase()
          let emoji = ''
          
          if (fieldName.includes('summary')) emoji = '📝'
          else if (fieldName.includes('phone')) emoji = '📞'
          else if (fieldName.includes('address')) emoji = '📍'
          else if (fieldName.includes('mood')) emoji = '😊'
          else if (fieldName.includes('highlight')) emoji = '✅'
          else if (fieldName.includes('rating')) emoji = '⭐'
          else if (fieldName.includes('hour')) emoji = '🕒'
          else if (fieldName.includes('price')) emoji = '💰'
          else if (fieldName.includes('popular')) emoji = '🍽️'
          
          return line.replace(/\*\*([^*]+):\*\*/g, `<strong>${emoji} $1:</strong>`)
        }
      }
      return line
    })
    return formattedLines
  }

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
        body: JSON.stringify({ mood: mood || selectedMood })
      })
      const data = await response.json()
      if (data.error) {
        setRecommendation(data.error)
      } else {
        const formatted = formatRecommendation(data.recommendation)
        setRecommendation(formatted)
        setOriginalRecommendation(formatted)
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
      
      // Map emojis based on line index to match original order
      const emojis = ['📝', '📞', '📍', '😊', '✅', '⭐', '🕒', '💰', '🍽️']
      
      const formattedTranslation = translatedLines.map((line, index) => {
        const emoji = emojis[index] || ''
        
        // Check if line already has emoji to prevent duplicates
        if (line.includes('📝') || line.includes('📞') || line.includes('📍') || 
            line.includes('😊') || line.includes('✅') || line.includes('⭐') || 
            line.includes('🕒') || line.includes('💰') || line.includes('🍽️')) {
          return line
        }
        
        // Always add emoji and formatting based on position
        if (line.includes(':')) {
          const colonIndex = line.indexOf(':')
          const label = line.substring(0, colonIndex + 1)
          const content = line.substring(colonIndex + 1)
          return `<strong>${emoji} ${label}</strong>${content}`
        } else {
          // For lines without colons, add a generic label based on position
          const labels = ['Summary:', 'Phone:', 'Address:', 'Moods:', 'Highlight:', 'Rating:', 'Hours:', 'Price:', 'Popular Items:']
          const label = labels[index] || 'Info:'
          return `<strong>${emoji} ${label}</strong> ${line}`
        }
      })
      
      setRecommendation(formattedTranslation)
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