from textblob import TextBlob
import logging

logger = logging.getLogger(__name__)

def rate_comments(comments):
    """Analyze sentiment: 0-100"""
    if not comments:
        return 0
    
    scores = []
    for comment in comments:
        try:
            text = comment.get('text', '') if isinstance(comment, dict) else str(comment)
            if text and len(text.strip()) > 5:
                sentiment = TextBlob(text).sentiment.polarity
                score = int((sentiment + 1) * 50)
                scores.append(score)
        except:
            pass
    
    return int(sum(scores) / len(scores)) if scores else 0


def rate_comments_with_details(comments):
    """
    Analyze sentiment and return comments with their individual scores.
    
    Args:
        comments: list of comment dicts with 'text' key
    
    Returns:
        dict with:
            - average_score: overall sentiment (0-100)
            - comments_with_sentiment: list of dicts {text, sentiment_score}
    """
    if not comments:
        return {'average_score': 0, 'comments_with_sentiment': []}
    
    scores = []
    comments_with_sentiment = []
    
    for comment in comments:
        try:
            text = comment.get('text', '') if isinstance(comment, dict) else str(comment)
            if text and len(text.strip()) > 5:
                sentiment = TextBlob(text).sentiment.polarity
                score = int((sentiment + 1) * 50)
                scores.append(score)
                comments_with_sentiment.append({
                    'text': text,
                    'sentiment_score': score
                })
        except Exception as e:
            logger.debug(f"Error processing comment: {e}")
            pass
    
    average_score = int(sum(scores) / len(scores)) if scores else 0
    
    return {
        'average_score': average_score,
        'comments_with_sentiment': comments_with_sentiment
    }
