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
        if is_next_day:
            is_in_morning = time_windows["morning"][0].hour <= this_datetime.hour <= time_windows["morning"][1].hour
            is_in_midday = time_windows["midday"][0].hour <= this_datetime.hour <= time_windows["midday"][1].hour
            is_in_afternoon = time_windows["evening"][0].hour <= this_datetime.hour <= time_windows["evening"][1].hour
            if is_in_morning:
                morning_forecast.append(hour_forecast)
            if is_in_midday:
                midday_forecast.append(hour_forecast)
            if is_in_afternoon:
                evening_forecast.append(hour_forecast)

    # TODO datetime.now() may be problematic for the deployed app
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

# My judgement on the best temperatures to run in
TEMP_C_SCORES = {
    -1: 2, -2: 2, -3: 1, -4: 1, -5: 1, -6: 1, -7: 1, -8: 1, -9: 1,
    0:  3,  1: 3,  2: 4,  3: 4,  4: 4,  5: 5,  6: 5,  7: 5,  8: 5,  9: 5,
    10: 6, 11: 6, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 8, 18: 9, 19: 9,
    20: 9, 21: 9, 22: 9, 23: 8, 24: 8, 25: 8, 26: 7, 27: 7, 28: 7, 29: 6,
    30: 6, 31: 5, 32: 4, 33: 3, 34: 2, 35: 1, 36: 1, 37: 1, 38: 1, 39: 1
}

CONDITIONS_SCORES = {
    # Storms    # Snow    # Rain      # Drizzle     # Atmos     # Clouds    # Clear
    "200": 2,   "600": 4,   "500": 5,   "300": 5,   "701": 7,   "801": 9,   "800": 9,
    "201": 2,   "601": 3,   "501": 4,   "301": 5,   "711": 3,   "802": 8,
    "202": 1,   "602": 1,   "502": 3,   "302": 2,   "721": 6,   "803": 8,
    "210": 1,   "611": 3,   "503": 2,   "310": 4,   "731": 3,   "804": 8,
    "211": 1,   "612": 4,   "504": 1,   "311": 3,   "741": 7,
    "212": 1,   "613": 4,   "511": 1,   "312": 2,   "751": 3,
    "221": 1,   "615": 3,   "520": 4,   "313": 3,   "761": 3,
    "230": 1,   "616": 2,   "521": 3,   "314": 2,   "762": 1,
    "231": 1,   "620": 3,   "522": 1,   "321": 3,   "771": 1,
    "232": 1,   "621": 2,   "531": 1,               "781": 1,
                "622": 1
}
