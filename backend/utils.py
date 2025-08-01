"""
Utility functions for restaurant recommendation system.

This module provides core functionality for:
- Loading and processing restaurant data from Hugging Face datasets
- Generating detailed restaurant information using Google Gemini AI
- Translating restaurant recommendations to multiple languages
- Mood-based restaurant recommendation logic
"""

from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import Field, BaseModel
# from transformers import pipeline  # Removed to reduce memory usage
import pandas as pd
from huggingface_hub import hf_hub_download
import os
import random

# Load environment variables (optional for local development)
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

# Configuration constants
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO_ID = os.getenv("REPO_ID")
FILE_NAME = os.getenv("FILE_NAME")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing! Check your .env file.")

class restaurant_detail(BaseModel):
    """
    Pydantic model for structured restaurant information.
    
    Attributes:
        phone (str): Restaurant phone number
        address (str): Restaurant address
        summary (str): Brief description of the restaurant
        moods (str): Mood categories the restaurant fits
        highlight (str): Key highlight or specialty
        rating (str): Restaurant rating information
        hours (str): Operating hours
        price (str): Price range information
        popular_items (str): Popular menu items
    """
    phone: str
    address: str
    summary: str
    moods: str
    highlight: str
    rating: str
    hours: str
    price: str
    popular_items: str

def setup_prompt_template(query):
    """
    Creates a prompt template for restaurant information queries.
    
    Args:
        query (str): The restaurant query string
        
    Returns:
        PromptTemplate: Configured prompt template for LLM
    """
    format = """You are a world famous restaurant expert. ...
    Question: {query}
    Answer: ... (format)
    """
    return PromptTemplate(input_variables=["query"], template=format)

def get_details_from_llm(restaurant_name, restaurant_city, restaurant_street):
    """
    Retrieves detailed restaurant information using Google Gemini AI.
    
    Args:
        restaurant_name (str): Name of the restaurant
        restaurant_city (str): City where restaurant is located
        restaurant_street (str): Street address of restaurant
        
    Returns:
        restaurant_detail: Structured restaurant information
    """
    query = f"Give me the details of {restaurant_name} in {restaurant_city} on {restaurant_street}"
    prompt_template = setup_prompt_template(query)
    parser = PydanticOutputParser(pydantic_object=restaurant_detail)
    instructions = parser.get_format_instructions()
    query += "\n\n" + instructions
    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY, temperature=0.3)
    response = (prompt_template | llm).invoke(query)
    data = parser.parse(response.content)
    return data

def format_restaurant_details(data, mood):
    """
    Formats restaurant details into a structured string format.
    
    Args:
        data (restaurant_detail): Restaurant information object
        mood (str): Selected mood category
        
    Returns:
        str: Formatted restaurant details string
    """
    return f"""📝 Summary: {data.summary}
📞 Phone: {data.phone}
📍 Address: {data.address}
😊 Moods: {mood}
✅ Highlight: {data.highlight}
⭐ Rating: {data.rating}
🕒 Hours: {data.hours}
💰 Price: {data.price}
🍽️ Popular Items: {data.popular_items}
"""

def translate(input_text, target_language):
    """
    Translates text to specified target language using Google Gemini.
    
    Args:
        input_text (str): Text to translate
        target_language (str): Target language (Spanish, French, German, Romanian)
        
    Returns:
        str: Translated text
        
    Raises:
        ValueError: If target language is not supported
    """
    supported_languages = ["Spanish", "French", "German", "Romanian"]
    if target_language not in supported_languages:
        raise ValueError(f"Language {target_language} not supported!")

    llm = ChatGoogleGenerativeAI(model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY, temperature=0.1)
    prompt = f"Translate the following text to {target_language}. Return ONLY the translated text with the same formatting and structure, no introduction:\n\n{input_text}"
    
    response = llm.invoke(prompt)
    # Remove any introductory text
    content = response.content
    if "Here's the translation" in content:
        content = content.split("Here's the translation", 1)[1]
        content = content.split(":", 1)[1] if ":" in content else content
        content = content.strip()
    return content

def load_parquet_from_huggingface(repo_id, filename, max_rows=1000):
    """
    Downloads and loads a limited parquet dataset from Hugging Face Hub.
    
    Args:
        repo_id (str): Hugging Face repository ID
        filename (str): Name of the parquet file
        max_rows (int): Maximum number of rows to load
        
    Returns:
        pd.DataFrame or None: Loaded dataset or None if failed
    """
    import time
    for attempt in range(3):
        try:
            print(f"Download attempt {attempt + 1}/3...")
            file_path = hf_hub_download(
                repo_id=repo_id, 
                filename=filename, 
                repo_type="dataset",
                force_download=False
            )
            # Read only first max_rows to save memory
            df = pd.read_parquet(file_path, engine='pyarrow')
            if len(df) > max_rows:
                df = df.sample(n=max_rows, random_state=42)
            print(f"Dataset loaded: {len(df)} rows")
            return df
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5)  # Wait before retry
            else:
                print(f"All attempts failed to load dataset")
                return None

def recommend_restaurant_by_mood_content(df, mood, num_of_recommendations=5):
    """
    Recommends a restaurant based on mood using expert reviewer analysis.
    
    Finds the most active reviewer for the specified mood and selects their
    highest-rated restaurant recommendation.
    
    Args:
        df (pd.DataFrame): Restaurant reviews dataset
        mood (str): Target mood for recommendation
        num_of_recommendations (int): Number of top recommendations to consider
        
    Returns:
        pd.Series or None: Restaurant recommendation or None if no matches
    """
    mood_matches = df[df["mood"] == mood]
    if mood_matches.empty:
        return None
    
    # Find the most active reviewer for this mood (mood expert)
    mood_expert_id = mood_matches["user_id"].value_counts().idxmax()
    mood_expert_reviews = mood_matches[mood_matches["user_id"] == mood_expert_id].copy()
    
    # Create short review summaries
    mood_expert_reviews["short_review"] = mood_expert_reviews["review"].apply(
        lambda x: x[:50] + "..." if isinstance(x, str) and len(x) > 50 else x
    )
    
    # Sort by rating and select top recommendations
    mood_expert_reviews = mood_expert_reviews.sort_values(by="review_stars", ascending=False)
    top_recommendations = mood_expert_reviews.head(num_of_recommendations)
    
    # Select randomly from highest-rated restaurants
    max_score = top_recommendations["review_stars"].max()
    top_scoring_restaurants = top_recommendations[top_recommendations["review_stars"] == max_score]
    final_best = top_scoring_restaurants.sample(1, random_state=random.randint(1, 9999)).iloc[0]
    
    return final_best