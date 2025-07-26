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
    format_restaurant_details, 
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

# Load restaurant dataset at application startup
customer_reviews_df = load_parquet_from_huggingface(REPO_ID, FILE_NAME)
if customer_reviews_df is None:
    raise ValueError("Dataset failed to load.")

class MoodRequest(BaseModel):
    """
    Request model for mood-based restaurant recommendations.
    
    Attributes:
        mood (str): Selected mood category (e.g., 'adventurous', 'romantic')
    """
    mood: str

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
        
        # Find restaurant recommendation based on mood
        recommendation = recommend_restaurant_by_mood_content(customer_reviews_df, user_selected_mood)
        
        if recommendation is None:
            return {"error": "No restaurants found for this mood!"}
        
        # Extract restaurant basic information
        rec_object = {
            "name": recommendation["business_name"],
            "address": recommendation["address"],
            "city": recommendation["city"]
        }
        
        # Get detailed information using AI
        restaurant_details = get_details_from_llm(
            rec_object["name"], 
            rec_object["city"], 
            rec_object["address"]
        )
        
        # Format details for frontend display
        formatted_details = format_restaurant_details(restaurant_details, user_selected_mood.title())
        
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)