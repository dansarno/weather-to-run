import logging
import schedule
import datetime
import tweepy
from bots import bot_state
from weather import day_weather
from weather import forecast
from bots import tweet_composer
from bots import config
from bots import auto_reply_bot
from bots import daily_tweet_bot
from bots import followback_bot

logging.getLogger('schedule').propagate = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


if __name__ == "__main__":

    tag = "myweather"  # trigger hashtag

    # Create API object
    api = config.create_api()
    # Create Profile object
    bot_account = bot_state.TwitterProfile(api)

    # daily_tweet_bot.daily_tweet(api, "new", debug=True)
    # schedule.every(15).seconds.do(auto_reply_bot.reply_to_mentions, bot_account, api, tag)
    schedule.every(15).seconds.do(auto_reply_bot.reply_to_mentions, bot_account, api, tag)
    # schedule.every(10).minutes.do(followback_bot.follow_back, api, bot_account)
    # schedule.every().day.at("22:00").do(daily_tweet_bot.daily_tweet, api, "new")
    while True:
        schedule.run_pending()
