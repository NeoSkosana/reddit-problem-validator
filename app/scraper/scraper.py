import praw
import pandas as pd
import os
from datetime import datetime
from app.core.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, PRAW_SITE_NAME

class RedditScraper:
    def __init__(self):
        """
        Initializes the Reddit API connection using PRAW.
        """
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
                # site_name=PRAW_SITE_NAME # Include if you have custom praw.ini configurations
            )
            print("Attempting to connect to Reddit API...")
            # Perform a simple read operation to check connection, 
            # e.g., try to access a known subreddit or a general API endpoint
            # For script applications, self.reddit.user.me() might require specific OAuth setup.
            # A less intrusive check:
            self.reddit.subreddits.search_by_name("test", exact=True) 
            print("Successfully connected to Reddit API (validated by simple read operation).")
        except Exception as e:
            print(f"Error connecting to Reddit API: {e}")
            # Potentially re-raise the exception or handle it as per application's needs
            raise

    # We will add more methods here in the next steps.

if __name__ == '__main__':
    # Example usage (for testing purposes)
    try:
        scraper = RedditScraper()
        # Further testing code will go here
        print("RedditScraper initialized successfully in __main__ block.")
    except Exception as e:
        print(f"Failed to initialize scraper in __main__ block: {e}")
