import weather.weather as weather
import time

while True:
    tomorrow = weather.Day()
    tomorrow.add_forecast(location)
    time.sleep(24*60*60)
