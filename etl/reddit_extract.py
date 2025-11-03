import praw

reddit = praw.Reddit(
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_SECRET',
    user_agent='imdb_sentiment_project'
)

def get_reddit_comments(movie_title, subreddit='movies', limit=50):
    comments = []
    for submission in reddit.subreddit(subreddit).search(movie_title, limit=limit):
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            comments.append({"text": comment.body, "author": comment.author.name if comment.author else None})
    return comments
