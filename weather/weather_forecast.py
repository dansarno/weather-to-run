import os
import credentials as cred
import requests
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
    minutely_forecast = full_response_dict["minutely"]
    hourly_forecast = full_response_dict["hourly"]
    daily_forecast = full_response_dict["daily"]

    return minutely_forecast, hourly_forecast, daily_forecast


def parse_hourly_forecast(hourly_forecast):
    pass


minutes, hours, days = fetch_forecast(True)
