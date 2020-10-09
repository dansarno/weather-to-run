import logging
import tweepy

logging.getLogger('schedule').propagate = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def follow_back(api_obj, bot):
    """Follow back new users that follow the account"""
    logger.info(f"Checking for new followers")
    current_followers = bot.followers
    for follower in tweepy.Cursor(api_obj.followers).items():
        if follower not in current_followers:
            logger.info(f"Now following {follower.name}")
            follower.follow()
            bot.followers.append(follower)
