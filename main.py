import weather.weather as weather
import time
import bots.tweet_composer as composer


def rankings_interpreter(rankings):
    pass
    # return tone, selections

# while True:
tomorrow = weather.Day()
tomorrow.score_forecast()
tomorrow.rank_segments()

templates = composer.get_tweet_templates("bots/tweet_content.yaml")
composer.compose_tweet(tomorrow.rankings["Green"][0], templates)

# time.sleep(24*60*60)
