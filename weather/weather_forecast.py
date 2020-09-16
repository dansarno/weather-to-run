import weather_config
import os
import credentials as cred
import numpy as np
import requests
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
import json
from scipy.interpolate import interp1d
import scipy.ndimage


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
    :return: Morning, afternoon, evening and next day forecasts
    :rtype: List of dictionaries
    """

    windowed_forecasts = {window_name: [] for window_name in time_windows.keys()}
    for hour_forecast in hourly_forecast:
        this_datetime = datetime.datetime.fromtimestamp(hour_forecast["dt"])
        is_next_day = datetime.datetime.now().day + 1 == this_datetime.day
        if not is_next_day:
            continue

        # Check if this hour is within any of the time windows
        for window_name, window_times in time_windows.items():
            is_in_window = window_times[0].hour <= this_datetime.hour <= window_times[1].hour
            if is_in_window:
                windowed_forecasts[window_name].append(hour_forecast)

    # TODO datetime.now() may be problematic for the deployed app
    tomorrows_summary = [day_forecast for day_forecast in daily_forecast
                         if datetime.datetime.fromtimestamp(day_forecast["dt"]).day == datetime.datetime.now().day + 1][0]

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
        all_scores.append(temp_c_to_score(hour_forecast["feels_like"]))
    if "wind" in what_to_score:
        all_scores.append(wind_speed_to_score(hour_forecast["wind_speed"]))
    if "precipitation" in what_to_score:
        all_scores.append(weather_config.PRECIPITATION_SCORES[str(int(hour_forecast["weather"][0]["id"]))])
    return all_scores


def wind_speed_to_score(wind_speed):
    # Empirical score (9-best, 0-worst) based off the Beaufort scale
    score = 10 - ((wind_speed ** (7 / 6)) / 6)
    return round(min(max(score, 0), 9), 1)


def temp_c_to_score(temp_c):
    # Empirical score (9-best, 0-worst)
    score = (-0.023 * (temp_c - 20) ** 2) + 9
    return round(min(max(score, 0), 9), 1)


def _plot_scores(hourly_forecast, what_to_score, time_windows):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    all_scores = [score_forecast(hour_forecast, what_to_score) for hour_forecast in hourly_forecast
                  if datetime.datetime.fromtimestamp(hour_forecast["dt"]).date() == tomorrow]
    temp, wind, precip = list(zip(*all_scores))
    forecast_times = [datetime.datetime.fromtimestamp(hour["dt"]) for hour in hourly_forecast
                      if datetime.datetime.fromtimestamp(hour["dt"]).date() == tomorrow]
    times = [int(time.strftime("%H")) for time in forecast_times]

    f_t = interp1d(times, temp, kind='linear')
    f_w = interp1d(times, wind, kind='linear')
    f_p = interp1d(times, precip, kind='linear')

    x_smooth = np.linspace(min(times), max(times), 200)

    fig = plt.figure(figsize=(5.5, 2.5))
    ax = fig.add_subplot(111)

    for window_name, window_times in time_windows.items():
        rect_width = max(window_times).hour - min(window_times).hour
        x = min(window_times).hour
        rect = patches.Rectangle((x, 1), rect_width, 9, edgecolor='none', facecolor='gray', alpha=200)
        ax.add_patch(rect)

        ax.text(((max(window_times).hour + min(window_times).hour) / 2) - 0.2,
                1.7,
                window_name.upper(),
                color='white',
                rotation=90,
                fontsize=15,
                fontweight='bold',
                zorder=1
                )

    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_t(x_smooth), 3) + 1, color='red')
    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_w(x_smooth), 3) + 1, color='blue')
    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_p(x_smooth), 3) + 1)
    ax.set_ylabel("SCORE")
    # ax.xaxis.set_tick_params(rotation=90)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_ylim([1, 10.5])
    ax.set_xlim([3.7, 22.5])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
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


if __name__ == "__main__":
    outcome = when_to_run(weather_config.TIME_WINDOWS)
    print(outcome.title())
