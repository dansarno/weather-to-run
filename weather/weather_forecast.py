import weather_config
import os
import credentials as cred
import requests
from datetime import datetime, time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
import json


def fetch_forecast(is_local, location=(51.5074, 0.1278)):
    if not is_local:
        api_key = os.getenv("API_KEY")
    else:
        api_key = cred.API_KEY

    lat, lon = location
    url = (f"https://api.openweathermap.org/data/2.5/onecall?"
           f"lat={lat}&lon={lon}"
           f"&exclude=current"
           f"&units=metric"
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

    # morning_forecast = []
    # midday_forecast = []
    # evening_forecast = []
    windowed_forecasts = {window_name: [] for window_name in time_windows.keys()}
    for hour_forecast in hourly_forecast:
        this_datetime = datetime.fromtimestamp(hour_forecast["dt"])
        is_next_day = datetime.now().day + 1 == this_datetime.day
        if not is_next_day:
            continue

        # Check if this hour is within any of the time windows
        for window_name, window_times in time_windows.items():
            is_in_window = window_times[0].hour <= this_datetime.hour <= window_times[1].hour
            if is_in_window:
                windowed_forecasts[window_name].append(hour_forecast)

        # is_in_morning = time_windows["morning"][0].hour <= this_datetime.hour <= time_windows["morning"][1].hour
        # is_in_midday = time_windows["midday"][0].hour <= this_datetime.hour <= time_windows["midday"][1].hour
        # is_in_afternoon = time_windows["evening"][0].hour <= this_datetime.hour <= time_windows["evening"][1].hour
        # if is_in_morning:
        #     morning_forecast.append(hour_forecast)
        # if is_in_midday:
        #     midday_forecast.append(hour_forecast)
        # if is_in_afternoon:
        #     evening_forecast.append(hour_forecast)

    # TODO datetime.now() may be problematic for the deployed app
    tomorrows_summary = [day_forecast for day_forecast in daily_forecast
                         if datetime.fromtimestamp(day_forecast["dt"]).day == datetime.now().day + 1][0]

    return windowed_forecasts, tomorrows_summary


def aggregate_scores(hourly_forecast, what_to_score):
    all_scores = [score_forecast(hour_forecast, what_to_score) for hour_forecast in hourly_forecast]
    lowest_scores_and_reasons = [(min(score), score.index(min(score))) for score in all_scores]
    return lowest_scores_and_reasons


def score_window_and_why(lowest_scores_and_reasons, weather_parameters):
    lowest_score = 10
    worst_parameter = ""
    for score, reason in lowest_scores_and_reasons:
        if score < lowest_score:
            lowest_score = score
            worst_parameter = weather_parameters[reason]
    return lowest_score, worst_parameter


def score_forecast(hour_forecast, what_to_score):
    all_scores = []
    if "temperature" in what_to_score:
        all_scores.append(_temp_c_to_score(hour_forecast["feels_like"]))
    if "wind" in what_to_score:
        all_scores.append(_wind_speed_to_score(hour_forecast["wind_speed"]))
    if "precipitation" in what_to_score:
        all_scores.append(weather_config.PRECIPITATION_SCORES[str(int(hour_forecast["weather"][0]["id"]))])
    return all_scores


def _wind_speed_to_score(wind_speed):
    # Empirical score (9-best, 0-worst) based off the Beaufort scale
    score = 10 - ((wind_speed ** (7 / 6)) / 6)
    return round(min(max(score, 0), 9), 2)


def _temp_c_to_score(temp_c):
    # Empirical score (9-best, 0-worst)
    score = (-0.023 * (temp_c - 20) ** 2) + 9
    return round(min(max(score, 0), 9), 2)


def _plot_scores(hourly_forecast, what_to_score, time_windows):
    all_scores = [score_forecast(hour_forecast, what_to_score) for hour_forecast in hourly_forecast]
    forecast_times = [datetime.fromtimestamp(hour["dt"]).strftime("%d, %H:%M") for hour in hourly_forecast]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for window_name, window_times in time_windows.items():
        rect_width = max(window_times).hour - min(window_times).hour
        x = min(window_times).hour + (24 - datetime.now().hour)
        rect = patches.Rectangle((x, 0), rect_width, 9, edgecolor='none', facecolor='gray', alpha=95)
        ax.add_patch(rect)

    ax.plot(forecast_times, all_scores)
    ax.set_xlabel("Datetime")
    ax.set_ylabel("Score")
    ax.xaxis.set_tick_params(rotation=30)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_ylim([0, 9.5])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.show()


def when_to_run(time_windows, is_local=True, is_debug=True):
    hourly_forecast, daily_forecast = fetch_forecast(is_local)
    if is_debug:
        _plot_scores(hourly_forecast, weather_config.WEATHER_PARAMETERS, time_windows)
    windowed_forecasts, tomorrows_summary = filter_forecasts(hourly_forecast, daily_forecast, time_windows)
    highest_score = -1
    best_time = ""  # likely need changing
    for window_name, forecast in windowed_forecasts.items():
        this_windows_score = score_window_and_why(
            aggregate_scores(forecast, weather_config.WEATHER_PARAMETERS), weather_config.WEATHER_PARAMETERS)[0]
        is_a_better_time = highest_score < this_windows_score
        if is_a_better_time:
            highest_score = this_windows_score
            best_time = window_name
    return best_time


outcome = when_to_run(weather_config.TIME_WINDOWS)
print(outcome.title())
