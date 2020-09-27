import logging
import schedule
import tweepy
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


def daily_tweet(api_obj, debug=False):
    """Automatically updates the bot's tweet status with the next day's run weather and dashboard image.

    Creates a default instance of the Day class (location=London, day=tomorrow) and generates tweet text and a
    dashboard image based off the forecast for that Day. That content is then posted to the bot's twitter timeline.

    Args:
        api_obj (Tweepy API object): An instance of the Tweepy API class.
        debug (bool): By default (False) the post is sent to Twitter. If True, the post is not sent and the dashboard
            image is shown on screen.
    """
    tomorrow = day_weather.Day()
    tomorrow.score_forecast()
    tomorrow.rank_segments()
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


def reply_to_mentions(api_obj, hashtag_str, initial_since_id):
    """Automatically replies to users with their run weather forecast and dashboard images.

    Makes an API call to retrieve the bot's mentions timeline for any new mentions. If new mentions are detected, they
    are inspected to see if they contain the trigger hashtag. If found, the tweet text is parsed for city names. If a
    city name is found, the bot account replies to the user with the run weather forecast and dashboard image for
    that city. If no city name is found, the bot account replies to the user to inform them as such.

    Args:
        api_obj (Tweepy API object): An instance of the Tweepy API class.
        hashtag_str (str): The hashtag string used to trigger an auto-reply response from the bot.
        initial_since_id (int): The latest mention tweet id. This id is used to limit the mentions timeline search
            to those already handled by this function.
    """
    logger.info("Retrieving mentions...")

    # Get the tweet id of the last mention to be handled by this function (cached in a txt file)
    with open("bots/last_checked_tweet_id.txt", "r") as f:
        since_id_from_file = int(f.read())

    # Use whichever is "newest": from cache or from initial check on start-up
    new_since_id = max(since_id_from_file, initial_since_id)

    for tweet in tweepy.Cursor(api_obj.mentions_timeline, since_id=new_since_id).items():
        # Update new_since_id if newer tweets are in the mentions timeline
        new_since_id = max(tweet.id, new_since_id)

        if tweet.in_reply_to_status_id is not None:
            continue

        if any(hashtag_str == hashtag["text"] for hashtag in tweet.entities["hashtags"]):
            logger.info(f"Answering {tweet.user.name}")

            loc = auto_reply_bot.text_to_location(tweet.text)
            if loc:
                reply_text, dashboard_file = tweet_your_weather(loc)

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

    # Cache the last mention tweet id
    with open("bots/last_checked_tweet_id.txt", "w") as f:
        f.write(str(new_since_id))


def tweet_your_weather(location):
    """Generates tweet text and a dashboard image given a user specified location.

    Args:
        location (dict): A single element dictionary with the city name as the key and lat and long tuple as the value.

    Returns:
        Tweet text string and the filename string indicating the location of the saved dashboard image
    """
    your_tomorrow = day_weather.Day(location=location)
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
    # Get latest mention tweet_id
    last_tweet_id = list(tweepy.Cursor(api.mentions_timeline).items(1))[0].id

    # daily_tweet(api, debug=True)
    schedule.every(15).seconds.do(reply_to_mentions, api, tag, last_tweet_id)
    schedule.every().day.at("22:00").do(daily_tweet, api)

    while True:
        schedule.run_pending()

    # test_loc = {"Houston": (29.760427, -95.369804)}
    # # test_loc = {"Tokyo": (35.689487, 139.691711)}
    # tweet_your_weather(test_loc)
