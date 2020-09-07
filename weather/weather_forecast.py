import os
import credentials as cred
import requests
from datetime import datetime, time
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


def group_forecasts_in_windows(hourly_forecast, time_windows):
    morning_forecast = []
    midday_forecast = []
    afternoon_forecast = []
    for hour_forecast in hourly_forecast:
        this_datetime = datetime.fromtimestamp(hour_forecast["dt"])
        is_next_day = datetime.now().day + 1 == this_datetime.day
        is_in_morning = time_windows["morning"][0].hour <= this_datetime.hour <= time_windows["morning"][1].hour
        is_in_midday = time_windows["midday"][0].hour <= this_datetime.hour <= time_windows["midday"][1].hour
        is_in_afternoon = time_windows["afternoon"][0].hour <= this_datetime.hour <= time_windows["afternoon"][1].hour
        if not is_next_day:
            continue
        if is_in_morning:
            morning_forecast.append(hour_forecast)
        if is_in_midday:
            midday_forecast.append(hour_forecast)
        if is_in_afternoon:
            afternoon_forecast.append(hour_forecast)
    return morning_forecast, midday_forecast, afternoon_forecast


def aggregate_forecast(hourly_forecast):
    pass


hours, days = fetch_forecast(True)
windows_dict = {
    "morning": [time(hour=6), time(hour=9)],
    "midday": [time(hour=12), time(hour=14)],
    "afternoon": [time(hour=17), time(hour=21)]
    }
