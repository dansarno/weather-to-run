import tweepy
import logging
from config import CredentialsConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def create_api():
    """Creates the Tweepy API object"""
    auth = tweepy.OAuthHandler(CredentialsConfig.TWITTER_CONSUMER_KEY, CredentialsConfig.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(CredentialsConfig.TWITTER_ACCESS_TOKEN, CredentialsConfig.TWITTER_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")

    return api
