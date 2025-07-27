# Vector Database Migration Notes

## Current Implementation vs Vector DB Approach

### What Was Removed Due to Memory Constraints

**Original Dataset-Based Approach (Removed):**
- File: `backend/main.py` - Lines where dataset loading occurred
- Function: `get_dataset()` - Lazy loaded 74k restaurant reviews from Hugging Face
- Function: `recommend_restaurant_by_mood_content()` - Used pandas DataFrame for mood-based filtering
- Dataset: `philly_reviews_with_mood.parquet` (74.8k reviews with mood embeddings)

**Replaced With:**
- Direct AI generation using Google Gemini
- No dataset loading - uses AI's built-in restaurant knowledge
- Location-based recommendations via prompt engineering

### Vector Database Recommendation for Production

**Why Vector DB Would Be Better:**
1. **Memory Efficiency** - No need to load 74k rows into RAM
2. **True Mood Matching** - Uses actual review embeddings vs AI interpretation
3. **Scalability** - Can handle millions of reviews
4. **Performance** - Optimized similarity search

**Recommended Implementation:**

```python
# Instead of loading DataFrame:
# customer_reviews_df = load_parquet_from_huggingface(REPO_ID, FILE_NAME)

# Use vector DB query:
import pinecone  # or weaviate, chroma, etc.

def get_mood_recommendations(mood, location):
    # Convert mood to embedding
    mood_embedding = embedding_model.encode(mood)
    
    # Query vector DB
    results = vector_db.query(
        vector=mood_embedding,
        top_k=5,
        filter={"city": location},
        include_metadata=True
    )
    
    return results.matches[0].metadata  # Restaurant info

# Replace AI generation with:
recommendation = get_mood_recommendations(user_selected_mood, user_location)
```

**Vector DB Options:**
- **Pinecone** - Managed, easiest setup
- **Weaviate** - Open source, feature-rich
- **Chroma** - Lightweight, good for prototypes
- **Supabase Vector** - PostgreSQL + vectors

**Migration Steps:**
1. Pre-process dataset offline to create embeddings
2. Upload to vector database with metadata (name, address, city, etc.)
3. Replace current AI generation with vector similarity search
4. Keep AI for detail enhancement only

**Files That Would Change:**
- `backend/main.py` - Replace AI generation with vector queries
- `backend/utils.py` - Add vector DB connection and query functions
- `backend/requirements.txt` - Add vector DB client library
- Add new file: `backend/vector_setup.py` - One-time data migration script

This would restore the original mood-based recommendation accuracy while solving the memory constraints.