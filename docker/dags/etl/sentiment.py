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
