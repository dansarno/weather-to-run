import time
from weather import day_weather
from weather import forecast
from bots import tweet_composer
from bots import config


def rankings_interpreter(rankings):
    # Simple ranking interpreter that returns the best ranked day segments
    segments = []
    alert_level = ""
    for level, segs in rankings.items():
        if segs:
            segments = [seg.name for seg in segs]
            alert_level = level
    return segments, alert_level


def produce_dashboard_image(day, filename, to_show=False):
    fig_handle = forecast.plot_scores(day, to_show)
    fig_handle.savefig(filename)


# while True:
tomorrow = day_weather.Day()
tomorrow.score_forecast()
tomorrow.rank_segments()
choices, tone = rankings_interpreter(tomorrow.rankings)

fname = f"dashboards/dashboard_{tomorrow.date.strftime('%d-%m-%y')}.jpg"
produce_dashboard_image(tomorrow, fname, to_show=True)

tweet_templates = tweet_composer.get_tweet_templates("bots/tweet_content.yaml")
tweet_text = tweet_composer.compose_tweet(choices, tone, tweet_templates)
print(tweet_text)

# # Create API object
# api = config.create_api(True)
# # Upload media
# media = api.media_upload(fname)  # 5MB limit
# # Create a test tweet
# api.update_status(status=tweet_text, media_ids=[media.media_id])
