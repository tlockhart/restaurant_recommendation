# Philadelphia Restaurant Recommendation System

An AI-powered restaurant recommendation system that suggests Philadelphia restaurants based on your mood. The application features a React frontend with mood-based image selection and a FastAPI backend that uses machine learning to provide personalized restaurant recommendations with multilingual translation support.

## Description

> **Important Note:** The original version used a dataset of 74.8K pre-classified Yelp restaurant reviews labeled by mood to generate personalized suggestions. However, the system now uses Google Gemini for real-time classification, due to the file size limitation below, instead of the philly_reviews_with_mood.parquet file.

This application helps users discover restaurants that match their current mood through an intuitive visual interface. Users can:

- Select from 8 different mood categories (Adventurous, Comforting, Energizing, Romantic, Cozy, Festive, Indulgent, Refreshing)
- Get AI-generated restaurant recommendations with detailed information including summary, contact details, address, hours, pricing, and popular items
- Translate recommendations into multiple languages (Spanish, French, German, Romanian)
- Enjoy a responsive dark-themed interface with smooth scrolling and loading animations

The system uses a curated dataset of Philadelphia restaurant reviews with mood classifications and leverages Google's Gemini AI for generating detailed restaurant information and translations.

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Conda (recommended for Python environment management)

### Backend Setup

1. Navigate to the project directory:
```bash
cd restaurant_recommendation
```

2. Create and activate a conda environment:
```bash
conda create -n restaurant-rec python=3.9
conda activate restaurant-rec
```

3. Install Python dependencies:
```bash
pip install -r backend/requirements.txt
```

4. Create a `.env` file in the root directory with your API credentials:
```
GEMINI_API_KEY=your_gemini_api_key_here
REPO_ID=tlockhart/philly_reviews_with_mood.parquet
FILE_NAME=philly_reviews_with_mood.parquet
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

## Running the Application

### Start the Backend Server

1. Ensure you're in the project root directory and conda environment is activated:
```bash
conda activate restaurant-rec
cd backend
python main.py
```

The backend server will start on `http://localhost:8000`

### Start the Frontend Development Server

1. In a new terminal, navigate to the frontend directory:
```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### Access the Application

Open your web browser and go to `http://localhost:5173` to use the restaurant recommendation system.

## Usage

1. **Select a Mood**: Click on one of the 8 mood images that best represents how you're feeling
2. **Get Recommendation**: The system will automatically fetch and display a restaurant recommendation
3. **View Details**: Review the restaurant information including summary, contact details, hours, and popular items
4. **Translate (Optional)**: Select a language from the dropdown and click "Translate" to view the recommendation in Spanish, French, German, or Romanian

## Deployment

### Render.com Deployment

**Backend Deployment:**
1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Configure the service:
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3.9+
4. Add environment variables in Render dashboard:
   - `GEMINI_API_KEY=your_api_key`
   - `REPO_ID=tlockhart/philly_reviews_with_mood.parquet`
   - `FILE_NAME=philly_reviews_with_mood.parquet`

**Frontend Deployment:**
1. Create a new Static Site on Render.com
2. Configure:
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
3. Update API URL in frontend code to your Render backend URL

## Architecture Changes

### Original Implementation
The system was initially designed to use a 74.8k restaurant review dataset from Hugging Face with pre-classified mood embeddings. However, deployment constraints required architectural modifications.

### Current Implementation
Due to memory limitations on deployment platforms (Fly.io free tier: 512MB-1GB), the system now uses:
- **Google Gemini AI** for real-time restaurant recommendations
- **Geolocation detection** for user location-based suggestions
- **Direct AI generation** instead of dataset querying

### Platform Constraints
- **Fly.io Memory Limits**: Free tier (512MB), paid tier (1GB+)
- **MongoDB Document Size**: 16MB BSON document limit
- **Dataset Size**: Original 74.8k reviews (~200MB+ in memory) exceeded limits

### Future Improvements
For production scale, consider:
- **Vector Database** (Pinecone, Weaviate, Chroma) for efficient similarity search
- **Chunked data loading** with pagination
- **Caching strategies** for frequently accessed data
- See `VECTOR_DB_NOTES.md` for detailed migration plan

## Technology Stack

- **Frontend**: React, Vite, CSS3
- **Backend**: FastAPI, Python
- **AI/ML**: Google Gemini API
- **Deployment**: Fly.io
- **Translation**: Google Gemini AI translation capabilities