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


def filter_forecasts(hourly_forecast, daily_forecast, time_windows):
    """ Filters all the hourly and daily forecasts returned from the API call to just those
    in the next day time windows.

    :param hourly_forecast: 48 hour forecast from API call
    :type hourly_forecast: List of dictionaries
    :param daily_forecast: 8 day forecast from API call
    :type daily_forecast: List of dictionaries
    :param time_windows: Start and end times of the running time windows
    :type time_windows: Dictionary
    :return: Morning, midday, evening and next day forecasts
    :rtype: List of dictionaries
    """

    morning_forecast = []
    midday_forecast = []
    evening_forecast = []
    for hour_forecast in hourly_forecast:
        this_datetime = datetime.fromtimestamp(hour_forecast["dt"])
        is_next_day = datetime.now().day + 1 == this_datetime.day
        is_in_morning = time_windows["morning"][0].hour <= this_datetime.hour <= time_windows["morning"][1].hour
        is_in_midday = time_windows["midday"][0].hour <= this_datetime.hour <= time_windows["midday"][1].hour
        is_in_afternoon = time_windows["evening"][0].hour <= this_datetime.hour <= time_windows["evening"][1].hour
        if not is_next_day:
            continue
        if is_in_morning:
            morning_forecast.append(hour_forecast)
        if is_in_midday:
            midday_forecast.append(hour_forecast)
        if is_in_afternoon:
            evening_forecast.append(hour_forecast)

    next_day_forecast = [day_forecast for day_forecast in daily_forecast
                         if datetime.fromtimestamp(day_forecast["dt"]).day == datetime.now().day + 1][0]

    return morning_forecast, midday_forecast, evening_forecast, next_day_forecast


def aggregate_forecast(hourly_forecast):
    pass


hours, days = fetch_forecast(True)
TIME_WINDOWS = {
    "morning": [time(hour=6), time(hour=9)],
    "midday": [time(hour=12), time(hour=14)],
    "evening": [time(hour=17), time(hour=21)]
}

TEMPERATURE_WEIGHTINGS = {

}
