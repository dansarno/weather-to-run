import logging
import datetime
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
    choices, order = tomorrow.rankings_interpreter()
    tone = tomorrow.alert_level

    fname = f"dashboards/dashboard_{tomorrow.date.strftime('%d-%m-%y')}.jpg"
    forecast.plot_scores(tomorrow, order, to_show=debug, filename=fname)

    tweet_text = tweet_composer.compose_tweet(choices, tone)

    if not debug:
        # Upload media
        media = api_obj.media_upload(fname)  # Note: there is a 5MB upload limit
        # Tweet the run weather forecast and dashboard image
        api_obj.update_status(status=tweet_text, media_ids=[media.media_id])

        logger.info("Daily tweet posted")
    else:
        print(tweet_text)
