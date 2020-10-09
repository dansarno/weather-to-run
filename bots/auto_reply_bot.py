from opencage.geocoder import OpenCageGeocode
import logging
import os
import datetime
import tweepy
from geotext import GeoText
from weather import forecast
from weather import day_weather
from bots import tweet_composer


logging.getLogger('schedule').propagate = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)


def create_geocoder_obj():
    """Reads authentication credentials from environment variables and creates the geocoder API object"""
    geocoder_api_key = os.getenv("GEOCODER_API_KEY")
    return OpenCageGeocode(geocoder_api_key)


def text_to_location(tweet_text):
    """Generates a location dictionary (city name and coordinates) given a sentence string.

    Uses geotext package to search a string for recognised city names contained within it. Then uses the opencage
    package to retrieve the latitude and longitude coordinates of the given city and forms a dictionary of the city
    name (key) and a tuple of the coordinates (value)

    Args:
        tweet_text (str): Sentence string

    Returns:
        Location dict or None: If a recognised city is in the tweet_text, a location is returned. Else, return None
        Offset: Number of seconds from UTC
    """
    geo = create_geocoder_obj()

    city_list = GeoText(tweet_text).cities
    if city_list:
        city_str = city_list[0]
        result = geo.geocode(city_str)
        offset = result[0]["annotations"]["timezone"]["offset_sec"]
        return {city_str: (result[0]["geometry"]["lat"], result[0]["geometry"]["lng"])}, offset
    else:
        return None


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

    logger.debug(f"Latest mention ID: {new_since_id}")

    for tweet in tweepy.Cursor(api_obj.mentions_timeline, since_id=new_since_id).items():
        # Update new_since_id if newer tweets are in the mentions timeline
        new_since_id = max(tweet.id, new_since_id)

        if tweet.in_reply_to_status_id is not None:
            continue

        if any(hashtag_str == hashtag["text"] for hashtag in tweet.entities["hashtags"]):
            logger.info(f"Replying to {tweet.user.name}")

            loc, offset_sec = text_to_location(tweet.text)
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
    choices, order = your_tomorrow.rankings_interpreter()
    tone = your_tomorrow.alert_level

    dashboard_filename_prefix = "_".join(list(location.keys())[0].lower().split())
    fname = f"dashboards/replies/{dashboard_filename_prefix}_dashboard" \
            f"_{your_tomorrow.date.strftime('%d-%m-%y')}.jpg"
    forecast.plot_scores(your_tomorrow, order, to_show=False, filename=fname)

    tweet_templates = tweet_composer.get_tweet_templates("bots/tweet_content.yaml")
    tweet_text = tweet_composer.compose_tweet(choices, tone, tweet_templates)

    return tweet_text, fname
