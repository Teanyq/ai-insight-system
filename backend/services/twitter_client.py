import os
import logging
import tweepy

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self):
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        self.client = None
        self.is_configured = False

        if all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            try:
                self.client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_secret
                )
                self.is_configured = True
                logger.info("Twitter client successfully configured.")
            except Exception as e:
                logger.error(f"Failed to configure Twitter client: {e}")
        else:
            logger.warning("Twitter API keys are missing. Auto-posting is disabled.")

    def post_tweet(self, text: str) -> bool:
        """
        Post a tweet to X (Twitter).
        Returns True if successful, False otherwise.
        """
        if not self.is_configured or not self.client:
            logger.warning("Cannot post tweet: Twitter client is not configured.")
            return False
            
        try:
            logger.info("Attempting to post tweet to X...")
            response = self.client.create_tweet(text=text)
            logger.info(f"Successfully posted tweet. Tweet ID: {response.data['id']}")
            return True
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return False

twitter_client = TwitterClient()
