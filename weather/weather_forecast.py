import os
import credentials as cred
import requests
from datetime import datetime
import json


def fetch_forecast(isLocal, location=(51.5074, 0.1278)):
    if not isLocal:
        api_key = os.getenv("API_KEY")
    else:
        api_key = cred.API_KEY

    lat, lon = location
    url = (f"https://api.openweathermap.org/data/2.5/onecall?"
           f"lat={lat}&lon={lon}"
           f"&exclude=current"
           f"&&units=metric"
           f"&appid={api_key}")

    response = requests.get(url)
    full_response_dict = response.json()
    hourly_forecast = full_response_dict["hourly"]
    daily_forecast = full_response_dict["daily"]

    return hourly_forecast, daily_forecast


def aggregate_forecast_in_windows(hourly_forecast, time_windows):
    for hour_forecast in hourly_forecast:
        is_next_day = datetime.fromtimestamp(hour_forecast["dt"]).day == datetime.now().day + 1
        is_in_morning = False
        is_in_midday = False
        is_in_afternoon = False
        if not is_next_day:
            continue
        if is_in_morning:
            pass
        if is_in_midday:
            pass
        if is_in_afternoon:
            pass
    return None


hours, days = fetch_forecast(True)
