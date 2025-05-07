import praw
import pandas as pd
import os
from datetime import datetime, timezone
try:
    from app.core.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, PRAW_SITE_NAME
except ImportError:
    # Fallback for direct script execution
    import sys
    from pathlib import Path
    root_dir = str(Path(__file__).resolve().parents[2])
    if root_dir not in sys.path:
        sys.path.append(root_dir)
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

    def _discover_subreddits(self, keywords: list[str], search_limit_per_keyword: int = 5) -> list[str]:
        """
        Discovers subreddits based on keywords using PRAW's search.

        Args:
            keywords: A list of keywords to search for.
            search_limit_per_keyword: Max number of subreddits to find per keyword.

        Returns:
            A list of unique subreddit display names.
        """
        discovered_subreddits = set() # Use a set to automatically handle duplicates

        if not keywords:
            print("No keywords provided for subreddit discovery. Returning empty list.")
            return []

        print(f"Discovering subreddits for keywords: {keywords}")
        for keyword in keywords:
            try:
                print(f"Searching for subreddits related to '{keyword}'...")
                # PRAW's subreddits.search() returns a generator of Subreddit objects
                search_results = self.reddit.subreddits.search(keyword, limit=search_limit_per_keyword)

                count = 0
                for subreddit in search_results:
                    # We are interested in the display name (e.g., 'learnpython')
                    discovered_subreddits.add(subreddit.display_name)
                    count += 1
                print(f"Found {count} subreddits for keyword '{keyword}'.")

            except Exception as e:
                print(f"Error during subreddit discovery for keyword '{keyword}': {e}")
                # Continue to the next keyword even if one fails
                continue

        if not discovered_subreddits:
            print("No subreddits found for the given keywords. Consider broader terms or check Reddit status.")
            # Optionally, return a default list or raise an error
            # For now, returning an empty list if nothing is found.
            # return ['learnpython', 'datascience'] # Example default

        print(f"Discovered subreddits: {list(discovered_subreddits)}")
        return list(discovered_subreddits)

    def fetch_posts_and_comments(self, subreddits: list[str], post_limit: int = 100, comment_limit_per_post: int = 20, min_upvotes_post: int = 3):
        """
        Fetches posts from specified subreddits and their comments.

        Args:
            subreddits: A list of subreddit names.
            post_limit: Maximum number of posts to fetch per subreddit.
            comment_limit_per_post: Maximum number of comments to fetch per post.
                                    Set to None to fetch all top-level comments (be cautious).
            min_upvotes_post: Minimum upvotes for a post to be included.

        Returns:
            A list of dictionaries, where each dictionary represents a post or a comment.
        """
        all_data = []
        processed_post_ids = set()

        if not subreddits:
            print("No subreddits provided to fetch_posts_and_comments. Using discovered/default subreddits.")
            # Example: use a keyword to discover some subreddits
            subreddits = self._discover_subreddits(keywords=["technology", "programming"])
                                                # ^^^ Example keywords, can be passed from outside

        for sub_name in subreddits:
            try:
                print(f"Fetching posts from r/{sub_name}...")
                subreddit = self.reddit.subreddit(sub_name)

                # Fetching hot posts, can be changed to new, top, etc.
                for post in subreddit.hot(limit=post_limit):
                    if post.id in processed_post_ids:
                        continue # Skip if post already processed (e.g., crossposts)

                    if post.score >= min_upvotes_post:
                        post_data = {
                            'item_id': f"post_{post.id}",
                            'parent_id': None, # Posts don't have a parent in this context
                            'type': 'post',
                            'subreddit': sub_name,
                            'title': post.title,
                            'content': post.selftext,
                            'upvotes': post.score,
                            'url': f"https://www.reddit.com{post.permalink}",
                            'created_utc': datetime.fromtimestamp(post.created_utc, timezone.utc).isoformat()
                        }
                        all_data.append(post_data)
                        processed_post_ids.add(post.id)

                        # Fetch comments for this post
                        print(f"Fetching comments for post: {post.title[:50]}...")
                        # Efficiently load comments:
                        # replace_more(limit=0) fetches all top-level comments by removing "MoreComments" objects.
                        # limit=None in replace_more would attempt to fetch *all* comments recursively, which can be very slow.
                        # For fetching only top-level comments, limit=0 is appropriate.
                        # If you need deeper comment threads, you might need a recursive approach or adjust the limit.
                        post.comments.replace_more(limit=0) 

                        comment_count = 0
                        # post.comments.list() gives a flat list of all loaded comments (after replace_more)
                        for comment in post.comments.list(): 
                            if comment_limit_per_post is not None and comment_count >= comment_limit_per_post:
                                break # Reached comment limit for this post

                            comment_data = {
                                'item_id': f"comment_{comment.id}",
                                'parent_id': f"post_{post.id}",
                                'type': 'comment',
                                'subreddit': sub_name,
                                'title': None, # Comments don't have titles
                                'content': comment.body,
                                'upvotes': comment.score,
                                'url': f"https://www.reddit.com{comment.permalink}",
                                'created_utc': datetime.fromtimestamp(comment.created_utc, timezone.utc).isoformat()
                            }
                            all_data.append(comment_data)
                            comment_count += 1
            except Exception as e:
                print(f"Error fetching data from r/{sub_name}: {e}")
                # Continue to the next subreddit
                continue

        print(f"Fetched a total of {len(all_data)} items (posts and comments).")
        return all_data


    def save_to_csv(self, data: list[dict], filename_prefix: str = "reddit_data"):
        """
        Saves the scraped data to a CSV file in the data/scraped_data/ directory.

        Args:
            data: A list of dictionaries (output from fetch_posts_and_comments).
            filename_prefix: Prefix for the CSV filename. Timestamp will be appended.
        """
        if not data:
            print("No data to save.")
            return

        df = pd.DataFrame(data)

        # Define the directory and ensure it exists
        output_dir = "data/scraped_data"
        os.makedirs(output_dir, exist_ok=True)

        # Create a unique filename with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"Data successfully saved to {filepath}")
        except Exception as e:
            print(f"Error saving data to CSV: {e}")


def main():
    """Main function to run the scraper"""
    try:
        scraper = RedditScraper()
        print("RedditScraper initialized successfully.")

        # Test subreddit discovery
        search_keywords = ["SaaS", "microservices", "indiehackers"]
        print(f"\nAttempting to discover subreddits with keywords: {search_keywords}...")
        discovered_subreddits = scraper._discover_subreddits(
            keywords=search_keywords,
            search_limit_per_keyword=3
        )

        # Define subreddits to scrape
        if discovered_subreddits:
            target_subreddits = discovered_subreddits
        else:
            print("\nNo subreddits discovered, using default list for scraping.")
            target_subreddits = ['learnpython', 'SideProject']

        if not target_subreddits:
            print("\nNo target subreddits to scrape. Exiting.")
            return

        print(f"\nStarting to fetch posts and comments for subreddits: {target_subreddits}...")
        scraped_data = scraper.fetch_posts_and_comments(
            subreddits=target_subreddits,
            post_limit=5,
            comment_limit_per_post=3,
            min_upvotes_post=1
        )

        if scraped_data:
            print(f"\nFetched {len(scraped_data)} items. Saving to CSV...")
            scraper.save_to_csv(scraped_data, filename_prefix="reddit_discovered_scrape")
        else:
            print("\nNo data was fetched. CSV will not be created.")

    except Exception as e:
        print(f"An error occurred during the scraping process: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
