import requests
import logging
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
import time

logger = logging.getLogger(__name__)

def get_film_comments(movie_title, limit=50):
    """Get REAL Reddit comments from live API (no local/sample data)"""
    try:
        logger.info(f"📝 Fetching REAL Reddit comments for '{movie_title}'...")
        comments = []
        
        # Try authenticated request first if credentials available
        if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
            logger.info("🔑 Using authenticated Reddit API...")
            comments = _get_authenticated_comments(movie_title, limit)
            if comments:
                logger.info(f"✓ Extracted {len(comments)} REAL comments (authenticated)")
                return comments
        
        # Fall back to anonymous request (REAL data from Reddit, may be rate limited)
        logger.info("🌐 Using anonymous Reddit API (real data)...")
        comments = _get_anonymous_comments(movie_title, limit)
        logger.info(f"✓ Extracted {len(comments)} REAL comments (anonymous/live)")
        
        # Return whatever we got from Reddit - REAL data only, no samples
        return comments if comments else _get_alternative_sources(movie_title, limit)
    
    except Exception as e:
        logger.error(f"Error fetching Reddit comments: {e}")
        # Try alternative sources
        return _get_alternative_sources(movie_title, limit)


def _get_authenticated_comments(movie_title, limit=50):
    """Get REAL comments using Reddit API authentication"""
    try:
        # Get OAuth token
        auth = (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
        headers = {'User-Agent': REDDIT_USER_AGENT}
        
        token_url = 'https://www.reddit.com/api/v1/access_token'
        token_data = {'grant_type': 'client_credentials'}
        
        token_response = requests.post(token_url, auth=auth, data=token_data, headers=headers, timeout=10)
        
        if token_response.status_code != 200:
            logger.warning(f"Failed to get Reddit token: {token_response.status_code}")
            return []
        
        access_token = token_response.json().get('access_token')
        if not access_token:
            logger.warning("No access token in response")
            return []
        
        # Search with authenticated token
        auth_headers = {
            'User-Agent': REDDIT_USER_AGENT,
            'Authorization': f'bearer {access_token}'
        }
        
        search_url = f"https://oauth.reddit.com/r/movies/search?q={movie_title}&sort=new&restrict_sr=on&limit=5"
        search_response = requests.get(search_url, headers=auth_headers, timeout=10)
        
        if search_response.status_code != 200:
            logger.warning(f"Search failed: {search_response.status_code}")
            return []
        
        data = search_response.json()
        comments = []
        
        if 'data' in data and 'children' in data['data']:
            for post in data['data']['children'][:3]:  # Limit to 3 posts
                post_data = post.get('data', {})
                post_id = post_data.get('id')
                
                if post_id:
                    comments_url = f"https://oauth.reddit.com/r/movies/comments/{post_id}?limit=10"
                    comments_response = requests.get(comments_url, headers=auth_headers, timeout=10)
                    
                    if comments_response.status_code == 200:
                        comments_data = comments_response.json()
                        
                        if isinstance(comments_data, list) and len(comments_data) > 1:
                            comments_section = comments_data[1]
                            
                            if 'data' in comments_section and 'children' in comments_section['data']:
                                for comment_obj in comments_section['data']['children']:
                                    if len(comments) >= limit:
                                        break
                                    
                                    comment_data = comment_obj.get('data', {})
                                    body = comment_data.get('body', '')
                                    
                                    if body and len(body.strip()) > 10 and body != '[deleted]':
                                        comments.append({"text": body})
                
                if len(comments) >= limit:
                    break
        
        return comments
    
    except Exception as e:
        logger.warning(f"Authenticated request failed: {e}")
        return []


def _get_anonymous_comments(movie_title, limit=50):
    """Get REAL comments using anonymous Reddit API (rate limited but REAL data from Reddit)"""
    try:
        comments = []
        
        # Search for posts about the movie
        url = f"https://www.reddit.com/r/movies/search.json?q={movie_title}&sort=new&restrict_sr=on&limit=10"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    post_data = post.get('data', {})
                    post_id = post_data.get('id')
                    
                    if post_id:
                        # Get actual comments from this post
                        comments_url = f"https://www.reddit.com/r/movies/comments/{post_id}.json"
                        comments_response = requests.get(comments_url, headers=headers, timeout=10)
                        
                        if comments_response.status_code == 200:
                            comments_data = comments_response.json()
                            
                            if isinstance(comments_data, list) and len(comments_data) > 1:
                                comments_section = comments_data[1]
                                
                                if 'data' in comments_section and 'children' in comments_section['data']:
                                    for comment_obj in comments_section['data']['children']:
                                        if len(comments) >= limit:
                                            break
                                        
                                        comment_data = comment_obj.get('data', {})
                                        body = comment_data.get('body', '')
                                        
                                        # Only add real comments
                                        if body and len(body.strip()) > 10 and body != '[deleted]':
                                            comments.append({"text": body})
                    
                    if len(comments) >= limit:
                        break
        else:
            logger.warning(f"Reddit returned status {response.status_code}")
        
        return comments
    
    except Exception as e:
        logger.error(f"Anonymous request failed: {e}")
        return []


def _get_alternative_sources(movie_title, limit=50):
    """Fallback: Try other sources or return minimal synthetic comments based on real patterns"""
    logger.info(f"⚠️  Using alternative comment sources for '{movie_title}'...")
    comments = []
    
    # Try IMDb user reviews (simple endpoint)
    try:
        # Search for movie on IMDb
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        search_url = f"https://www.imdb.com/find?q={movie_title}&s=tt"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Could parse IMDb reviews here if needed
            logger.info("✓ Checked IMDb for reviews")
    except Exception as e:
        logger.warning(f"IMDb review fetch failed: {e}")
    
    # If we still have no comments, return empty (don't use sample data)
    logger.warning(f"Could not fetch real comments for '{movie_title}' - returning empty list")
    return comments