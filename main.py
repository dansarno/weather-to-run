import weather.weather as weather
import weather.weather_config as config
import time

location = config.LOCATION

while True:
    tomorrow = weather.Day()
    tomorrow.score_forecast()
    tomorrow.rank_segments()

    time.sleep(24*60*60)
