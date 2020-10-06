import logging
import schedule
import datetime
import tweepy
import bot_state
from weather import day_weather
from weather import forecast
from bots import tweet_composer
from bots import config
from bots import auto_reply_bot

logging.getLogger('schedule').propagate = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def rankings_interpreter(rankings):
    """Simple ranking interpreter that returns the best ranked day segments"""
    all_segements = []
    best_segments = []
    is_first = True
    for level, segs in rankings.items():
        if segs:
            for seg in segs:
                all_segements.append(seg.name)
            if is_first:
                best_segments = [seg.name for seg in segs]
                is_first = False
    return best_segments, all_segements


# TODO - make debug an environment variable
def daily_tweet(api_obj, method, debug=False):
    """Automatically updates the bot's tweet status with the next day's run weather and dashboard image.

    Creates a default instance of the Day class (location=London, day=tomorrow) and generates tweet text and a
    dashboard image based off the forecast for that Day. That content is then posted to the bot's twitter timeline.

    Args:
        api_obj (Tweepy API object): An instance of the Tweepy API class.
        debug (bool): By default (False) the post is sent to Twitter. If True, the post is not sent and the dashboard
            image is shown on screen.
    """
    date_of_next_day = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow = day_weather.Day(date_of_next_day)
    tomorrow.score_forecast()
    if method == "old":
        tomorrow.rank_segments()
    elif method == "new":
        tomorrow.rank_segments_2()
    else:
        print(f"Method of {method} is not recognised.")
    choices, order = rankings_interpreter(tomorrow.rankings)
    tone = tomorrow.alert_level

    fname = f"dashboards/dashboard_{tomorrow.date.strftime('%d-%m-%y')}.jpg"
    forecast.plot_scores(tomorrow, order, to_show=debug, filename=fname)

    tweet_templates = tweet_composer.get_tweet_templates("bots/tweet_content.yaml")
    tweet_text = tweet_composer.compose_tweet(choices, tone, tweet_templates)

    if not debug:
        # Upload media
        media = api_obj.media_upload(fname)  # Note: there is a 5MB upload limit
        # Tweet the run weather forecast and dashboard image
        api_obj.update_status(status=tweet_text, media_ids=[media.media_id])

        logger.info("Daily tweet posted")
    else:
        print(tweet_text)


def reply_to_mentions(bot, api_obj, hashtag_str):
    """Automatically replies to users with their run weather forecast and dashboard images.

    Makes an API call to retrieve the bot's mentions timeline for any new mentions. If new mentions are detected, they
    are inspected to see if they contain the trigger hashtag. If found, the tweet text is parsed for city names. If a
    city name is found, the bot account replies to the user with the run weather forecast and dashboard image for
    that city. If no city name is found, the bot account replies to the user to inform them as such.

    Args:
        bot (object): Twitter account object, storing the state of the profile
        api_obj (Tweepy API object): An instance of the Tweepy API class.
        hashtag_str (str): The hashtag string used to trigger an auto-reply response from the bot.
    """
    logger.info("Retrieving mentions...")

    # Get the most recent mention tweet id stored in the profile state
    new_since_id = bot.last_mention_id

    logger.info(f"Latest mention ID: {new_since_id}")

    for tweet in tweepy.Cursor(api_obj.mentions_timeline, since_id=new_since_id).items():
        # Update new_since_id if newer tweets are in the mentions timeline
        new_since_id = max(tweet.id, new_since_id)

        if tweet.in_reply_to_status_id is not None:
            continue

        if any(hashtag_str == hashtag["text"] for hashtag in tweet.entities["hashtags"]):
            logger.info(f"Answering {tweet.user.name}")

            loc, offset_sec = auto_reply_bot.text_to_location(tweet.text)
            if loc:
                reply_text, dashboard_file = tweet_your_weather(loc, offset_sec)

                # Upload media
                media = api_obj.media_upload(dashboard_file)

                # Reply to user with their run weather forecast and dashboard image
                api_obj.update_status(
                    status=f"@{tweet.author.screen_name} {reply_text}",
                    in_reply_to_status_id=tweet.id,
                    auto_populate_reply_metadata=True,
                    media_ids=[media.media_id]
                )
            else:
                reply_text = "sorry, I couldn't find your location. Want to give it another try?"

                # Reply to user without forecast
                api_obj.update_status(
                    status=f"@{tweet.author.screen_name} {reply_text}",
                    in_reply_to_status_id=tweet.id,
                    auto_populate_reply_metadata=True
                )

    # Update the most recent mention tweet id in the profile state
    bot.last_mention_id = new_since_id


def tweet_your_weather(location, offset):
    """Generates tweet text and a dashboard image given a user specified location.

    Args:
        location (dict): A single element dictionary with the city name as the key and lat and long tuple as the value.
        offset (int): Number of seconds from UTC

    Returns:
        Tweet text string and the filename string indicating the location of the saved dashboard image
    """
    hour_delta = offset / 60 / 60
    their_next_day = datetime.datetime.now() + datetime.timedelta(days=1) + datetime.timedelta(hours=hour_delta)
    their_next_date = their_next_day.date()
    your_tomorrow = day_weather.Day(their_next_date, location=location)
    your_tomorrow.score_forecast()
    your_tomorrow.rank_segments()
    choices, order = rankings_interpreter(your_tomorrow.rankings)
    tone = your_tomorrow.alert_level

    dashboard_filename_prefix = "_".join(list(location.keys())[0].lower().split())
    fname = f"dashboards/replies/{dashboard_filename_prefix}_dashboard" \
            f"_{your_tomorrow.date.strftime('%d-%m-%y')}.jpg"
    forecast.plot_scores(your_tomorrow, order, to_show=False, filename=fname)

    tweet_templates = tweet_composer.get_tweet_templates("bots/tweet_content.yaml")
    tweet_text = tweet_composer.compose_tweet(choices, tone, tweet_templates)

    return tweet_text, fname


if __name__ == "__main__":

    tag = "myweather"  # trigger hashtag

    # Create API object
    api = config.create_api()
    # Create Profile object
    bot_account = bot_state.TwitterProfile(api)

    # daily_tweet(api, "new", debug=True)
    schedule.every(15).seconds.do(reply_to_mentions, bot_account, api, tag)
    schedule.every().day.at("22:00").do(daily_tweet, api, "new")

    while True:
        schedule.run_pending()
