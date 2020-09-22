import os
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.interpolate import interp1d
import scipy.ndimage
import matplotlib.image as mpimg
from weather import dashboard_colours as colours


def fetch_forecast(location):

    api_key = os.getenv("OPENWEATHER_API_KEY")

    lat, lon = list(location.values())[0]
    url = (f"https://api.openweathermap.org/data/2.5/onecall?"
           f"lat={lat}&lon={lon}"
           f"&exclude=current"
           f"&units=metric"
           f"&appid={api_key}")

    response = requests.get(url)
    full_response_dict = response.json()
    timezone_offset = full_response_dict["timezone_offset"]
    hourly_forecast = full_response_dict["hourly"]
    daily_forecast = full_response_dict["daily"]

    return hourly_forecast, daily_forecast, timezone_offset


def wind_speed_to_score(wind_speed):
    # Empirical score (9-best, 0-worst) based off the Beaufort scale
    score = 10 - ((wind_speed ** (7 / 6)) / 6)
    return round(min(max(score, 0), 9), 1)


def temp_c_to_score(temp_c):
    # Empirical score (9-best, 0-worst)
    score = (-0.023 * (temp_c - 20) ** 2) + 9
    return round(min(max(score, 0), 9), 1)


def plot_scores(day, rankings, to_show, filename):

    # TODO: This plotting protocol needs porting over to main where it can be integrated with true weather data
    # TODO: Also need to sort out how to gradient the segment patches so they fade out towards the top

    all_scores = [(hour.temp_score, hour.wind_score, hour.precipitation_score) for hour in day.hours]
    temp, wind, precip = list(zip(*all_scores))
    times = [hour.hr for hour in day.hours]

    f_t = interp1d(times, temp, kind='linear')
    f_w = interp1d(times, wind, kind='linear')
    f_p = interp1d(times, precip, kind='linear')

    x_smooth = np.linspace(min(times), max(times), 200)

    fig = plt.figure("Weather Dashboard", figsize=(8, 4.5))  # 16 x 9 aspect ratio for twitter
    gs = fig.add_gridspec(nrows=3, ncols=4, left=0.08, bottom=0.12, top=0.95)
    gs.update(wspace=-0.1)
    fig.patch.set_facecolor(colours.background)
    ax = fig.add_subplot(gs[-2:, :-1])

    fig.text(0.045, 0.9, "Weather to run or bot".upper(), color='white', fontsize=18, fontweight='bold')

    fig.text(0.05, 0.8, "LOCATION:", color=colours.info_field, fontsize=12)
    fig.text(0.17, 0.8, f"{list(day.location.keys())[0].upper()}", color=colours.info_text, fontsize=12)
    fig.text(0.05, 0.75, "SUNRISE:", color=colours.info_field, fontsize=12)
    fig.text(0.17, 0.75, f"{day.sunrise:%H:%M}", color=colours.info_text, fontsize=12)
    fig.text(0.05, 0.7, "SUNSET:", color=colours.info_field, fontsize=12)
    fig.text(0.17, 0.7, f"{day.sunset:%H:%M}", color=colours.info_text, fontsize=12)
    fig.text(0.35, 0.8, "BEST OPTION:", color=colours.info_field, fontsize=12)
    fig.text(0.55, 0.8, f"{rankings[0].upper()}", color=colours.info_text, fontsize=12)
    fig.text(0.35, 0.75, "BACKUP OPTION:", color=colours.info_field, fontsize=12)
    fig.text(0.55, 0.75, f"{rankings[1].upper()}", color=colours.info_text, fontsize=12)
    fig.text(0.35, 0.7, "FINAL OPTION:", color=colours.info_field, fontsize=12)
    fig.text(0.55, 0.7, f"{rankings[2].upper()}", color=colours.info_text, fontsize=12)

    fig.text(0.52, 0.9, f"{day.date:%d.%m.%y}", color='white', fontsize=18, fontweight='ultralight')

    for name, seg in day.segments.items():
        rect_width = seg.duration + 0.9
        x = seg.start_time.hour
        rect = patches.Rectangle((x, 1), rect_width, 9, edgecolor='none', facecolor=colours.segments)
        ax.add_patch(rect)

        ax.text(((seg.end_time.hour + seg.start_time.hour) / 2) + 0.2,
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
    ax.set_ylabel("BOT RATING", color='white', fontweight="light")

    ax2 = fig.add_subplot(gs[0, -1])
    max_temp = 40  # C
    ccw = False
    if 0 < day.temp_c <= max_temp:
        groups = [day.temp_c / max_temp, 1 - day.temp_c / max_temp]
    elif day.temp_c == 0:
        groups = [0.01, 0.99]
    elif day.temp_c >= max_temp:
        groups = [max_temp, 0]
        ax_max = fig.add_axes([0.77, 0.925, 0.04, 0.04])
        im_max = mpimg.imread('assets/maxed_temp.png')
        ax_max.imshow(im_max)
        ax_max.xaxis.set_visible(False)
        ax_max.yaxis.set_visible(False)
        ax_max.set_facecolor(colours.background)
        ax_max.spines['right'].set_visible(False)
        ax_max.spines['left'].set_visible(False)
        ax_max.spines['bottom'].set_visible(False)
        ax_max.spines['top'].set_visible(False)
    else:
        groups = [abs(day.temp_c) / max_temp, 1 - abs(day.temp_c) / max_temp]
        ccw = True
    ax2.pie(groups, colors=[colours.temp, colours.segments], startangle=90, counterclock=ccw)
    my_circle = plt.Circle((0, 0), 0.7, color=colours.background)
    ax2.add_artist(my_circle)
    ax2.text(1.3, 0.4, "M:", color=colours.info_field, fontsize=12)
    ax2.text(1.8, 0.4, f"{day.segments['morning'].temp_c:.1f}°C", color=colours.info_text, fontsize=12)
    ax2.text(1.3, -0.2, "A:", color=colours.info_field, fontsize=12)
    ax2.text(1.8, -0.2, f"{day.segments['afternoon'].temp_c:.1f}°C", color=colours.info_text, fontsize=12)
    ax2.text(1.3, -0.8, "E:", color=colours.info_field, fontsize=12)
    ax2.text(1.8, -0.8, f"{day.segments['evening'].temp_c:.1f}°C", color=colours.info_text, fontsize=12)

    im_therm = mpimg.imread('assets/therm.png')
    therm = OffsetImage(im_therm, zoom=0.18)
    ab_therm = AnnotationBbox(therm, (0, 0), frameon=False)
    ax2.add_artist(ab_therm)

    ax3 = fig.add_subplot(gs[1, -1])
    max_wind = 30  # mps
    if 0 < day.wind_mps <= max_wind:
        groups = [day.wind_mps / max_wind, 1 - day.wind_mps / max_wind]
    elif day.wind_mps > max_wind:
        groups = [max_wind, 0]
        ax_max = fig.add_axes([0.77, 0.634, 0.04, 0.04])
        im_max = mpimg.imread('assets/maxed_wind.png')
        ax_max.imshow(im_max)
        ax_max.xaxis.set_visible(False)
        ax_max.yaxis.set_visible(False)
        ax_max.set_facecolor(colours.background)
        ax_max.spines['right'].set_visible(False)
        ax_max.spines['left'].set_visible(False)
        ax_max.spines['bottom'].set_visible(False)
        ax_max.spines['top'].set_visible(False)
    else:
        groups = [0.01, 0.99]
    ax3.pie(groups, colors=[colours.wind, colours.segments], startangle=90, counterclock=False)
    my_circle = plt.Circle((0, 0), 0.7, color=colours.background)
    ax3.add_artist(my_circle)
    ax3.text(1.3, 0.4, "M:", color=colours.info_field, fontsize=12)
    ax3.text(1.8, 0.4, f"{day.segments['morning'].wind_mps:.1f}m/s", color=colours.info_text, fontsize=12)
    ax3.text(1.3, -0.2, "A:", color=colours.info_field, fontsize=12)
    ax3.text(1.8, -0.2, f"{day.segments['afternoon'].wind_mps:.1f}m/s", color=colours.info_text, fontsize=12)
    ax3.text(1.3, -0.8, "E:", color=colours.info_field, fontsize=12)
    ax3.text(1.8, -0.8, f"{day.segments['evening'].wind_mps:.1f}m/s", color=colours.info_text, fontsize=12)

    im_wind = mpimg.imread('assets/wind.png')
    wind = OffsetImage(im_wind, zoom=0.18)
    ab_wind = AnnotationBbox(wind, (0, 0), frameon=False)
    ax3.add_artist(ab_wind)

    ax4 = fig.add_subplot(gs[2, -1])
    max_precip = 20  # mm
    if 0 < day.precipitation_mm <= max_precip:
        groups = [day.precipitation_mm / max_precip, 1 - day.precipitation_mm / max_precip]
    elif day.precipitation_mm > max_precip:
        groups = [max_precip, 0]
        ax_max = fig.add_axes([0.77, 0.34, 0.04, 0.04])
        im_max = mpimg.imread('assets/maxed_precip.png')
        ax_max.imshow(im_max)
        ax_max.xaxis.set_visible(False)
        ax_max.yaxis.set_visible(False)
        ax_max.set_facecolor(colours.background)
        ax_max.spines['right'].set_visible(False)
        ax_max.spines['left'].set_visible(False)
        ax_max.spines['bottom'].set_visible(False)
        ax_max.spines['top'].set_visible(False)
    else:
        groups = [0.01, 0.99]
    ax4.pie(groups, colors=[colours.precip, colours.segments], startangle=90, counterclock=False)
    my_circle = plt.Circle((0, 0), 0.7, color=colours.background)
    ax4.add_artist(my_circle)
    ax4.text(1.3, 0.4, "M:", color=colours.info_field, fontsize=12)
    ax4.text(1.8, 0.4, f"{day.segments['morning'].precipitation_mm:.1f}mm", color=colours.info_text, fontsize=12)
    ax4.text(1.3, -0.2, "A:", color=colours.info_field, fontsize=12)
    ax4.text(1.8, -0.2, f"{day.segments['afternoon'].precipitation_mm:.1f}mm", color=colours.info_text, fontsize=12)
    ax4.text(1.3, -0.8, "E:", color=colours.info_field, fontsize=12)
    ax4.text(1.8, -0.8, f"{day.segments['evening'].precipitation_mm:.1f}mm", color=colours.info_text, fontsize=12)

    im_drop = mpimg.imread('assets/drop.png')
    drop = OffsetImage(im_drop, zoom=0.17)
    ab_drop = AnnotationBbox(drop, (0, 0), frameon=False)
    ax4.add_artist(ab_drop)

    # im_bot = mpimg.imread('assets/my_bot.png')
    # bot = OffsetImage(im_bot, zoom=0.1)
    # ab_bot = AnnotationBbox(bot, (-1.25, -0.28), frameon=False)
    # ax4.add_artist(ab_bot)

    if to_show:
        plt.show()

    if filename:
        fig.savefig(filename)


if __name__ == "__main__":
    pass
