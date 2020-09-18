from weather import config
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
import matplotlib.image as mpimg


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
                         if datetime.datetime.fromtimestamp(day_forecast["dt"]).day == datetime.datetime.now().day + 1][
        0]

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
        all_scores.append(config.PRECIPITATION_SCORES[str(int(hour_forecast["weather"][0]["id"]))])
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

    # TODO: This ploting protol needs porting over to main where it can be integrated with true weather data
    # TODO: Also need to sort out how to gradient the segment patches so they fade out towards the top

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

    fig = plt.figure(figsize=(10, 4.5))
    gs = fig.add_gridspec(nrows=3, ncols=4, left=0.07, bottom=0.12, top=0.95)
    gs.update(wspace=-0.1)
    fig.patch.set_facecolor('#222831')
    ax = fig.add_subplot(gs[-2:, :-1])

    fig.text(0.05, 0.9, "Weather to run or bot".upper(), color='white', fontsize=20, fontweight='bold')

    fig.text(0.05, 0.8, "LOCATION: LONDON, UK", color='#7691ad', fontsize=12)
    fig.text(0.05, 0.75, "SUNRISE: 06:48", color='#7691ad', fontsize=12)
    fig.text(0.05, 0.7, "SUNSET: 19:28", color='#7691ad', fontsize=12)
    fig.text(0.3, 0.8, "WEEKS TILL SPRING RACES: 26", color='#7691ad', fontsize=12)
    fig.text(0.3, 0.75, "WEEKS TILL AUTUMN RACES: 3", color='#7691ad', fontsize=12)
    fig.text(0.3, 0.7, "YEAR PROGRESS: 80%", color='#7691ad', fontsize=12)

    fig.text(0.6, 0.9, tomorrow.strftime("%d.%m.%y"), color='white', fontsize=16, fontweight='bold')

    for window_name, window_times in time_windows.items():
        rect_width = max(window_times).hour - min(window_times).hour
        x = min(window_times).hour
        rect = patches.Rectangle((x, 1), rect_width, 9, edgecolor='none', facecolor='#30475e')
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

    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_t(x_smooth), 3) + 1, color='#46b5d1', linewidth=4.0)
    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_w(x_smooth), 3) + 1, color='#29c7ac', linewidth=4.0)
    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_p(x_smooth), 3) + 1, color='#f30a49', linewidth=4.0)
    ax.set_ylabel("BOT RATING", color='white')

    ax.set_facecolor('#222831')
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_ylim([1, 10.5])
    ax.set_xlim([3.7, 22.5])
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('white')

    ax2 = fig.add_subplot(gs[0, -1])
    groups = [70, 30]
    ax2.pie(groups, colors=['#46b5d1', '#222831'], startangle=90, counterclock=False)
    my_circle = plt.Circle((0, 0), 0.7, color='#222831')
    ax2.add_artist(my_circle)
    ax2.text(-0.2, -0.2, "T", color='white', fontsize=17)
    ax2.text(1.3, 0.4, "M: 14C", color='#7691ad', fontsize=12)
    ax2.text(1.3, -0.2, "A: 24C", color='#7691ad', fontsize=12)
    ax2.text(1.3, -0.8, "E: 22C", color='#7691ad', fontsize=12)

    ax3 = fig.add_subplot(gs[1, -1])
    groups = [40, 60]
    ax3.pie(groups, colors=['#29c7ac', '#222831'], startangle=90, counterclock=False)
    my_circle = plt.Circle((0, 0), 0.7, color='#222831')
    ax3.add_artist(my_circle)
    ax3.text(-0.2, -0.2, "W", color='white', fontsize=17)
    ax3.text(1.3, 0.4, "M: 4 mps", color='#7691ad', fontsize=12)
    ax3.text(1.3, -0.2, "A: 3 mps", color='#7691ad', fontsize=12)
    ax3.text(1.3, -0.8, "E: 6 mps", color='#7691ad', fontsize=12)

    ax4 = fig.add_subplot(gs[2, -1])
    groups = [85, 15]
    ax4.pie(groups, colors=['#f30a49', '#222831'], startangle=90, counterclock=False)
    my_circle = plt.Circle((0, 0), 0.7, color='#222831')
    ax4.add_artist(my_circle)
    ax4.text(-0.2, -0.2, "P", color='white', fontsize=17)
    ax4.text(1.3, 0.4, "M: 12% 0mm", color='#7691ad', fontsize=12)
    ax4.text(1.3, -0.2, "A: 5% 0mm", color='#7691ad', fontsize=12)
    ax4.text(1.3, -0.8, "E: 7% 0mm", color='#7691ad', fontsize=12)

    ax5 = fig.add_axes([0.59, 0.12, 0.2, 0.2])
    # ax5 = fig.add_subplot(gs[0, 2])
    im = mpimg.imread('my_bot.png')
    ax5.imshow(im)
    ax5.xaxis.set_visible(False)
    ax5.yaxis.set_visible(False)
    ax5.set_facecolor('#222831')
    ax5.spines['right'].set_visible(False)
    ax5.spines['left'].set_visible(False)
    ax5.spines['bottom'].set_visible(False)
    ax5.spines['top'].set_visible(False)

    plt.show()


def when_to_run(time_windows, is_local=True, is_debug=True):
    hourly_forecast, daily_forecast = fetch_forecast(is_local)
    if is_debug:
        _plot_scores(hourly_forecast, config.WEATHER_PARAMETERS, time_windows)
    windowed_forecasts, tomorrows_summary = filter_forecasts(hourly_forecast, daily_forecast, time_windows)
    highest_score = -1
    best_time = ""  # likely need changing
    for window_name, forecast in windowed_forecasts.items():
        this_windows_score = score_window_and_why(
            aggregate_scores(forecast, config.WEATHER_PARAMETERS), config.WEATHER_PARAMETERS)[0]
        is_a_better_time = highest_score < this_windows_score
        if is_a_better_time:
            highest_score = this_windows_score
            best_time = window_name
    return best_time


if __name__ == "__main__":
    outcome = when_to_run(config.TIME_WINDOWS)
    print(outcome.title())
