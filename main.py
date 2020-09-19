import time
from weather import day_weather
from weather import forecast
from bots import tweet_composer


def rankings_interpreter(rankings):
    # Simple ranking interpreter that returns the best ranked day segments
    segments = []
    alert_level = ""
    for level, segs in rankings.items():
        if segs:
            segments = [seg.name for seg in segs]
            alert_level = level
    return segments, alert_level


def produce_dashboard_image(day, to_show=False):
    fig_handle = forecast.plot_scores(day, to_show)
    fig_handle.savefig(f"dashboards/dashboard_{day.date.strftime('%d-%m-%y')}.jpg")


# while True:
tomorrow = day_weather.Day()
tomorrow.score_forecast()
tomorrow.rank_segments()
choices, tone = rankings_interpreter(tomorrow.rankings)
produce_dashboard_image(tomorrow)

tweet_templates = tweet_composer.get_tweet_templates("bots/tweet_content.yaml")
tweet_text = tweet_composer.compose_tweet(choices, tone, tweet_templates)
print(tweet_text)

# time.sleep(24*60*60)
