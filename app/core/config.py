import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Reddit API Credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Basic PRAW settings (can be expanded)
PRAW_SITE_NAME = os.getenv("PRAW_SITE_NAME", "default") # Optional: for custom PRAW configurations

# Placeholder for other configurations
# For example, database URLs, API keys for other services, etc.
# DATABASE_URL = os.getenv("DATABASE_URL")

# Validate that essential credentials are loaded
if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
    raise ValueError(
        "Missing one or more Reddit API credentials. "
        "Ensure REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT are set in your .env file."
    )

# You can add more configurations and validations as needed
