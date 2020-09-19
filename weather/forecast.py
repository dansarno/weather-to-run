import os
import credentials as cred
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
from scipy.interpolate import interp1d
import scipy.ndimage
import matplotlib.image as mpimg
from weather import dashboard_colours as colours


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


def wind_speed_to_score(wind_speed):
    # Empirical score (9-best, 0-worst) based off the Beaufort scale
    score = 10 - ((wind_speed ** (7 / 6)) / 6)
    return round(min(max(score, 0), 9), 1)


def temp_c_to_score(temp_c):
    # Empirical score (9-best, 0-worst)
    score = (-0.023 * (temp_c - 20) ** 2) + 9
    return round(min(max(score, 0), 9), 1)


def plot_scores(day, to_show):

    # TODO: This plotting protocol needs porting over to main where it can be integrated with true weather data
    # TODO: Also need to sort out how to gradient the segment patches so they fade out towards the top

    all_scores = [(hour.temp_score, hour.wind_score, hour.precipitation_score) for hour in day.hours]
    temp, wind, precip = list(zip(*all_scores))
    times = [hour.hr for hour in day.hours]

    f_t = interp1d(times, temp, kind='linear')
    f_w = interp1d(times, wind, kind='linear')
    f_p = interp1d(times, precip, kind='linear')

    x_smooth = np.linspace(min(times), max(times), 200)

    fig = plt.figure(figsize=(8, 4.5))  # 16 x 9 aspect ratio for twitter
    gs = fig.add_gridspec(nrows=3, ncols=4, left=0.07, bottom=0.12, top=0.95)
    gs.update(wspace=-0.1)
    fig.patch.set_facecolor(colours.background)
    ax = fig.add_subplot(gs[-2:, :-1])

    fig.text(0.05, 0.9, "Weather to run or bot".upper(), color='white', fontsize=20, fontweight='bold')

    fig.text(0.05, 0.8, "LOCATION: LONDON, UK", color=colours.info_text, fontsize=12)
    fig.text(0.05, 0.75, f"SUNRISE: {day.sunrise:%H:%M}", color=colours.info_text, fontsize=12)
    fig.text(0.05, 0.7, f"SUNSET: {day.sunset:%H:%M}", color=colours.info_text, fontsize=12)
    fig.text(0.3, 0.8, "WEEKS TILL SPRING RACES: 26", color=colours.info_text, fontsize=12)
    fig.text(0.3, 0.75, "WEEKS TILL AUTUMN RACES: 3", color=colours.info_text, fontsize=12)
    fig.text(0.3, 0.7, "YEAR PROGRESS: 80%", color=colours.info_text, fontsize=12)

    fig.text(0.6, 0.9, f"{day.date:%d.%m.%y}", color='white', fontsize=16, fontweight='bold')

    for name, seg in day.segments.items():
        rect_width = seg.duration + 0.9
        x = seg.start_time.hour
        rect = patches.Rectangle((x, 1), rect_width, 9, edgecolor='none', facecolor=colours.segments)
        ax.add_patch(rect)

        ax.text(((seg.end_time.hour + seg.start_time.hour) / 2) - 0.2,
                1.7,
                seg.name.upper(),
                color='white',
                rotation=90,
                fontsize=15,
                fontweight='bold',
                zorder=1
                )

    ax.set_facecolor(colours.background)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.set_ylim([1, 10.5])
    ax.set_xlim([4.7, 23.5])
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('white')

    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_t(x_smooth), 3) + 1, color=colours.temp, linewidth=4.0, zorder=5)
    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_w(x_smooth), 3) + 1, color=colours.wind, linewidth=4.0, zorder=5)
    ax.plot(x_smooth, scipy.ndimage.gaussian_filter(f_p(x_smooth), 3) + 1, color=colours.precip, linewidth=4.0, zorder=5)
    ax.set_ylabel("BOT RATING", color='white')

    ax2 = fig.add_subplot(gs[0, -1])
    max_temp = 40  # C
    ccw = False
    if day.temp_c > 0:
        groups = [day.temp_c / max_temp, 1 - day.temp_c / max_temp]
    elif day.temp_c == 0:
        groups = [0.01, 0.99]
    else:
        groups = [abs(day.temp_c) / max_temp, 1 - abs(day.temp_c) / max_temp]
        ccw = True
    ax2.pie(groups, colors=[colours.temp, colours.background], startangle=90, counterclock=ccw)
    my_circle = plt.Circle((0, 0), 0.7, color=colours.background)
    ax2.add_artist(my_circle)
    ax2.text(-0.2, -0.2, "T", color='white', fontsize=17)
    ax2.text(1.3, 0.4, f"M: {day.segments['morning'].temp_c:.1f}C", color=colours.info_text, fontsize=12)
    ax2.text(1.3, -0.2, f"A: {day.segments['afternoon'].temp_c:.1f}C", color=colours.info_text, fontsize=12)
    ax2.text(1.3, -0.8, f"E: {day.segments['evening'].temp_c:.1f}C", color=colours.info_text, fontsize=12)

    ax3 = fig.add_subplot(gs[1, -1])
    max_wind = 30  # mps
    groups = [day.wind_mps / max_wind, 1 - day.wind_mps / max_wind]
    ax3.pie(groups, colors=[colours.wind, colours.background], startangle=90, counterclock=False)
    my_circle = plt.Circle((0, 0), 0.7, color=colours.background)
    ax3.add_artist(my_circle)
    ax3.text(-0.2, -0.2, "W", color='white', fontsize=17)
    ax3.text(1.3, 0.4, f"M: {day.segments['morning'].wind_mps:.1f}mps", color=colours.info_text, fontsize=12)
    ax3.text(1.3, -0.2, f"A: {day.segments['afternoon'].wind_mps:.1f}mps", color=colours.info_text, fontsize=12)
    ax3.text(1.3, -0.8, f"E: {day.segments['evening'].wind_mps:.1f}mps", color=colours.info_text, fontsize=12)

    ax4 = fig.add_subplot(gs[2, -1])
    max_precip = 20  # mm
    if day.precipitation_mm != 0:
        groups = [day.precipitation_mm / max_precip, 1 - day.precipitation_mm / max_precip]
    else:
        groups = [0.01, 0.99]
    ax4.pie(groups, colors=[colours.precip, colours.background], startangle=90, counterclock=False)
    my_circle = plt.Circle((0, 0), 0.7, color=colours.background)
    ax4.add_artist(my_circle)
    ax4.text(-0.2, -0.2, "P", color='white', fontsize=17)
    ax4.text(1.3, 0.4, f"M: {(day.segments['morning'].precipitation_prob * 100):.0f}% "
                       f"{day.segments['morning'].precipitation_mm:.0f}mm", color=colours.info_text, fontsize=12)
    ax4.text(1.3, -0.2, f"A: {(day.segments['afternoon'].precipitation_prob * 100):.0f}% "
                        f"{day.segments['afternoon'].precipitation_mm:.0f}mm", color=colours.info_text, fontsize=12)
    ax4.text(1.3, -0.8, f"E: {(day.segments['evening'].precipitation_prob * 100):.0f}% "
                        f"{day.segments['evening'].precipitation_mm:.0f}mm", color=colours.info_text, fontsize=12)

    ax5 = fig.add_axes([0.59, 0.12, 0.2, 0.2])
    im = mpimg.imread('art/my_bot.png')
    ax5.imshow(im)
    ax5.xaxis.set_visible(False)
    ax5.yaxis.set_visible(False)
    ax5.set_facecolor(colours.background)
    ax5.spines['right'].set_visible(False)
    ax5.spines['left'].set_visible(False)
    ax5.spines['bottom'].set_visible(False)
    ax5.spines['top'].set_visible(False)

    if to_show:
        plt.show()

    return fig


if __name__ == "__main__":
    pass
