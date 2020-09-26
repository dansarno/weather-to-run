import time
import os
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
    # Simple ranking interpreter that returns the best ranked day segments
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
        media = api_obj.media_upload(fname)  # 5MB limit
        # Create a test tweet
        api_obj.update_status(status=tweet_text, media_ids=[media.media_id])

        logger.info("Daily tweet posted")


def reply_to_mentions(api_obj, hashtag_str, initial_since_id):
    logger.info("Retrieving mentions...")

    # Get the last tweet id that is stored
    with open("bots/last_checked_tweet_id.txt", "r") as f:
        since_id_from_file = int(f.read())

    # Use whichever is newest: from file or from initial check
    new_since_id = max(since_id_from_file, initial_since_id)

    for tweet in tweepy.Cursor(api_obj.mentions_timeline, since_id=new_since_id).items():
        # Update new_since_id if newer tweets are in the mentions timeline
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue

        if any(hashtag_str == hashtag["text"] for hashtag in tweet.entities["hashtags"]):
            logger.info(f"Answering {tweet.user.name}")

            loc = auto_reply_bot.text_to_coords(tweet.text)
            reply_text, dashboard_file = tweet_your_weather(loc)

            # Upload media
            media = api_obj.media_upload(dashboard_file)

            api_obj.update_status(
                status=f"@{tweet.author.screen_name} {reply_text}",
                in_reply_to_status_id=tweet.id,
                auto_populate_reply_metadata=True,
                media_ids=[media.media_id]
            )

    # Set the last mention tweet id
    with open("bots/last_checked_tweet_id.txt", "w") as f:
        f.write(str(new_since_id))


def tweet_your_weather(location):
    your_tomorrow = day_weather.Day(location=location)
    your_tomorrow.score_forecast()
    your_tomorrow.rank_segments()
    choices, order = rankings_interpreter(your_tomorrow.rankings)
    tone = your_tomorrow.alert_level

    fname = f"dashboards/replies/{list(location.keys())[0].lower()}_dashboard" \
            f"_{your_tomorrow.date.strftime('%d-%m-%y')}.jpg"
    forecast.plot_scores(your_tomorrow, order, to_show=False, filename=fname)

    tweet_templates = tweet_composer.get_tweet_templates("bots/tweet_content.yaml")
    tweet_text = tweet_composer.compose_tweet(choices, tone, tweet_templates)

    return tweet_text, fname


if __name__ == "__main__":

    tag = "myweather"

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
