import requests
import logging

logger = logging.getLogger(__name__)

def get_film_comments(movie_title, limit=50):
    """Get real Reddit comments"""
    try:
        logger.info(f"Fetching Reddit comments for '{movie_title}'...")
        comments = []
        
        url = f"https://www.reddit.com/r/movies/search.json?q={movie_title}&sort=new&restrict_sr=on&limit=10"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    post_data = post.get('data', {})
                    post_id = post_data.get('id')
                    
                    if post_id:
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
                                        
                                        if body and len(body.strip()) > 10 and body != '[deleted]':
                                            comments.append({"text": body})
                    
                    if len(comments) >= limit:
                        break
        
        logger.info(f"Extracted {len(comments)} comments")
        return comments
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return []
