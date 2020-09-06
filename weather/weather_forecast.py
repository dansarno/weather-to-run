import os
import credentials as cred
import requests
import json


def fetch_hourly_forecast(isLocal, location=(51.5074, 0.1278)):
    if not isLocal:
        api_key = os.getenv("API_KEY")
    else:
        api_key = cred.API_KEY

    lat, lon = location
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,daily&appid={api_key}"
    response = requests.get(url)

    return response.json()


print(fetch_hourly_forecast(True))
