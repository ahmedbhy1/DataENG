# Real Data Sources Configuration

## Summary of Changes

Your pipeline now fetches **REAL data** from actual APIs instead of local/sample data:

### 1. **Movie Data** - Updated `extract.py`
- **OLD**: Used hardcoded fallback list of 2025 movies
- **NEW**: Fetches from **TMDB (The Movie Database) API**
  - Real trending movies
  - Real cast/actor information
  - Real ratings and metadata
  - Automatic fallback to IMDb classics if API fails

**API Used**: The Movie Database (TMDB) - Free API
- Endpoint: `https://api.themoviedb.org/3/trending/movie/week`
- Fetches top trending movies with full cast information
- API Key: Already configured in `config.py`

### 2. **Movie Comments** - Updated `reddit_extract.py`
- **OLD**: Would return empty list if Reddit failed
- **NEW**: Attempts multiple sources:
  1. Authenticated Reddit API (if credentials provided)
  2. Anonymous Reddit API (public data)
  3. Alternative IMDb reviews fallback
  - Returns actual user comments about movies
  - No sample/synthetic data

**APIs Used**: 
- Reddit API: `https://oauth.reddit.com/` & `https://www.reddit.com/`
- IMDb Reviews: Alternative source
- Sentiment analysis on real comments

### 3. **Actor Ratings** - Already Real
- `calculate_actor_ratings.py` aggregates ratings from database
- Based on actual film ratings and filmography
- No changes needed - it was already correct

---

## How to Get Better Comments (Optional but Recommended)

### Set up Reddit API Credentials
To get REAL Reddit comments for better analysis:

1. Go to: https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: "My Movie Analysis Project"
   - **App Type**: Select "script"
   - **Redirect URI**: http://localhost:8000
4. Copy the **Client ID** and **Client Secret**
5. Add to your `.env` file:
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   ```

### Optional: Custom TMDB API Key
If you want your own TMDB key:

1. Go to: https://www.themoviedb.org/settings/api
2. Create account and apply for API key
3. Add to `.env`:
   ```
   TMDB_API_KEY=your_api_key_here
   ```

---

## Data Flow Now

```
┌─────────────────────────────────────────────────────┐
│  REAL DATA SOURCES                                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🎬 Movies: TMDB API                              │
│     ├─ Trending movies (real current data)       │
│     ├─ Cast information                          │
│     └─ Ratings & metadata                        │
│                                                     │
│  💬 Comments: Reddit API                          │
│     ├─ Real user discussions                     │
│     ├─ Sentiment analysis                        │
│     └─ Movie ratings from comments               │
│                                                     │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────┐
        │ ETL Pipeline Processing    │
        │ - Extract                  │
        │ - Transform (Sentiment)    │
        │ - Load (PostgreSQL)        │
        └────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────┐
        │ Database (PostgreSQL)      │
        │ - Films table              │
        │ - Actors table             │
        │ - Actor-Film relations     │
        │ - Ratings                  │
        └────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────┐
        │ Analysis & Reports         │
        │ - Actor ratings            │
        │ - Sentiment scores         │
        │ - Web dashboard            │
        └────────────────────────────┘
```

---

## Files Modified

### 1. `etl/extract.py`
- Changed from BeautifulSoup IMDb scraping to TMDB API
- Now fetches real trending movies with cast info
- Better error handling with fallbacks

### 2. `etl/reddit_extract.py`
- Added authenticated Reddit API support
- Improved anonymous Reddit fetching
- Added alternative source fallback (IMDb)
- Better error messages and logging

### 3. `config.py`
- Added TMDB configuration details
- Added Reddit API setup instructions
- Better documentation for all credentials

---

## Testing

To test with real data:

```bash
# Run the pipeline
docker-compose up

# Or test locally:
from etl.extract import get_latest_films
from etl.reddit_extract import get_film_comments

movies = get_latest_films(limit=5)
print(f"Found {len(movies)} real movies")

for movie in movies:
    comments = get_film_comments(movie['title'], limit=10)
    print(f"Movie: {movie['title']}, Comments: {len(comments)}")
```

---

## Key Improvements

✅ **No more hardcoded movie data** - All movies are real and current  
✅ **Real cast information** - From TMDB, not placeholders  
✅ **Real user comments** - From Reddit or alternative sources  
✅ **Accurate sentiment analysis** - On real comments  
✅ **Better actor ratings** - Based on real data across database  
✅ **Automatic fallbacks** - If one source fails, tries alternatives  
✅ **Better logging** - See exactly what data is being fetched  

---

## Troubleshooting

### Getting empty comments?
- Reddit has rate limiting for anonymous users
- Solution: Get Reddit API credentials (see section above)

### API timeouts?
- Some APIs may be slow depending on network
- Timeouts are set to 10 seconds
- Check your internet connection

### TMDB API issues?
- Already configured with a public key
- Or get your own at: https://www.themoviedb.org/settings/api

