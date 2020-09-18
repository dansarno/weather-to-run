import weather.day_weather as weather
import time
import bots.tweet_composer as composer


def rankings_interpreter(rankings):
    # Simple ranking interpreter that returns the best ranked day segments
    segments = []
    alert_level = ""
    for level, segs in rankings.items():
        if segs:
            segments = [seg.name for seg in segs]
            alert_level = level
    return segments, alert_level


# while True:
tomorrow = weather.Day()
tomorrow.score_forecast()
tomorrow.rank_segments()
choices, tone = rankings_interpreter(tomorrow.rankings)

tweet_templates = composer.get_tweet_templates("bots/tweet_content.yaml")
tweet_text = composer.compose_tweet(choices, tone, tweet_templates)
print(tweet_text)

# time.sleep(24*60*60)
