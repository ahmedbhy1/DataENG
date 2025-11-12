from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

analyzer = SentimentIntensityAnalyzer()

def compute_sentiment(comments):
    if not comments:
        return 0.0, 0
    scores = [analyzer.polarity_scores(c['text'])['compound'] for c in comments]
    avg_score = sum(scores) / len(scores)
    return avg_score, len(scores)
