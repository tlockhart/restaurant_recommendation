"""
FastAPI backend server for restaurant recommendation system.

This module provides REST API endpoints for:
- Getting mood-based restaurant recommendations
- Translating restaurant information to multiple languages

The server uses Google Gemini AI for generating detailed restaurant information
and Facebook's NLLB model for multilingual translation support.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    load_parquet_from_huggingface, 
    recommend_restaurant_by_mood_content, 
    get_details_from_llm, 
    translate, 
    REPO_ID, 
    FILE_NAME
)

# Initialize FastAPI application
app = FastAPI(
    title="Restaurant Recommendation API",
    description="AI-powered restaurant recommendations based on mood",
    version="1.0.0"
)

# Configure CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to cache dataset
customer_reviews_df = None

def get_dataset():
    """Lazy load dataset only when needed"""
    global customer_reviews_df
    if customer_reviews_df is None:
        try:
            print("Loading dataset...")
            customer_reviews_df = load_parquet_from_huggingface(REPO_ID, FILE_NAME, max_rows=1000)
            if customer_reviews_df is None:
                print("Dataset failed to load")
        except Exception as e:
            print(f"Dataset loading error: {e}")
            customer_reviews_df = None
    return customer_reviews_df

class MoodRequest(BaseModel):
    """
    Request model for mood-based restaurant recommendations.
    
    Attributes:
        mood (str): Selected mood category (e.g., 'adventurous', 'romantic')
        location (str, optional): User's location (city, state or coordinates)
    """
    mood: str
    location: str = "Atlanta, GA"  # Default location

class TranslateRequest(BaseModel):
    """
    Request model for text translation.
    
    Attributes:
        text (str): Text to be translated
        language (str): Target language (French, German, Romanian)
    """
    text: str
    language: str

@app.post("/recommend")
async def get_recommendation(request: MoodRequest):
    """
    Get restaurant recommendation based on selected mood.
    
    This endpoint:
    1. Finds restaurants matching the specified mood from the dataset
    2. Uses AI to generate detailed restaurant information
    3. Returns formatted restaurant details
    
    Args:
        request (MoodRequest): Request containing mood selection
        
    Returns:
        dict: Restaurant recommendation with detailed information
        
    Raises:
        HTTPException: If recommendation generation fails
    """
    try:
        user_selected_mood = request.mood.lower()
        user_location = request.location
        
        # Generate restaurant recommendation directly with AI
        from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
        from utils import GEMINI_MODEL, GEMINI_API_KEY
        
        import random
        random_seed = random.randint(1, 1000)
        
        llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY, temperature=0.9)
        prompt = f"""Find a different highly-rated (4-5 star) restaurant in {user_location} that matches a {user_selected_mood} mood. Choose randomly from available options (seed: {random_seed}). 
        Provide ONLY this exact format with no introduction:
        📝 Summary: [Restaurant Name - brief description of cuisine/atmosphere, no address]
        📞 Phone: [phone number]
        📍 Address: [full street address]
        😊 Moods: {user_selected_mood.title()}
        ✅ Highlight: [key unique feature or specialty]
        ⭐ Rating: [rating and review info]
        🕒 Hours: [operating hours]
        💰 Price: [price range like $$$ or $15-25 per person]
        🍽️ Popular Items: [specific popular dishes]"""
        
        response = llm.invoke(prompt)
        formatted_details = response.content
        
        return {"recommendation": formatted_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate")
async def translate_text(request: TranslateRequest):
    """
    Translate restaurant recommendation to specified language.
    
    Supports translation to French, German, and Romanian using
    Facebook's NLLB multilingual translation model.
    
    Args:
        request (TranslateRequest): Request containing text and target language
        
    Returns:
        dict: Translated text
        
    Raises:
        HTTPException: If translation fails or language not supported
    """
    try:
        translated_text = translate(request.text, request.language)
        return {"translated_text": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    """
    Run the FastAPI server when script is executed directly.
    
    Server configuration:
    - Host: 0.0.0.0 (accessible from all network interfaces)
    - Port: from environment variable or 8000 default
    - Auto-reload enabled for development
    """
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)