import numpy as np
import requests
from config import DisplayConfig
from config import CredentialsConfig
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.interpolate import interp1d
import scipy.ndimage
import matplotlib.image as mpimg


def fetch_forecast(location):
    """Makes API call to OpenWeatherMap to get the weather forecast for a specific location.

    Args:
        location (dict): City name (key) and a tuple of the decimal geographic coordinates (value)

    Returns:
        hourly_forecast: Dictionary of the 48 hour weather data API response
        daily_forecast: Dictionary of the 7 day weather data API response
        timezone_offset: Shift in seconds from UTC of this location

    """

    api_key = CredentialsConfig.OPENWEATHER_API_KEY

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


def _generate_forecast_lines(day_obj):
    all_scores = [(hour.temp_score, hour.wind_score, hour.precipitation_score) for hour in day_obj.hours]
    temp, wind, precip = list(zip(*all_scores))
    times = [hour.hr for hour in day_obj.hours]

    f_t = interp1d(times, temp, kind='linear')
    f_w = interp1d(times, wind, kind='linear')
    f_p = interp1d(times, precip, kind='linear')

    time_smooth = np.linspace(min(times), max(times), 200)
    temp_smooth = scipy.ndimage.gaussian_filter(f_t(time_smooth), 3)
    wind_smooth = scipy.ndimage.gaussian_filter(f_w(time_smooth), 3)
    precip_smooth = scipy.ndimage.gaussian_filter(f_p(time_smooth), 3)
    return time_smooth, temp_smooth, wind_smooth, precip_smooth


def _add_dashboard_text_to_figure(fig_handle, day_obj, preferences):
    fig_handle.text(0.045, 0.9, "Weather to run or bot".upper(), color='white', fontsize=18, fontweight='bold')
    fig_handle.text(0.52, 0.9, f"{day_obj.date:%d.%m.%y}", color='white', fontsize=18, fontweight='ultralight')

    fig_handle.text(0.05, 0.8, "LOCATION:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    fig_handle.text(0.17, 0.8, f"{list(day_obj.location.keys())[0].upper()}", color=DisplayConfig.INFO_TEXT, fontsize=12)
    fig_handle.text(0.05, 0.75, "SUNRISE:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    fig_handle.text(0.17, 0.75, f"{day_obj.sunrise:%H:%M}", color=DisplayConfig.INFO_TEXT, fontsize=12)
    fig_handle.text(0.05, 0.7, "SUNSET:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    fig_handle.text(0.17, 0.7, f"{day_obj.sunset:%H:%M}", color=DisplayConfig.INFO_TEXT, fontsize=12)
    fig_handle.text(0.35, 0.8, "BEST OPTION:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    fig_handle.text(0.55, 0.8, f"{preferences[0].upper()}", color=DisplayConfig.INFO_TEXT, fontsize=12)
    fig_handle.text(0.35, 0.75, "BACKUP OPTION:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    fig_handle.text(0.55, 0.75, f"{preferences[1].upper()}", color=DisplayConfig.INFO_TEXT, fontsize=12)
    fig_handle.text(0.35, 0.7, "FINAL OPTION:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    fig_handle.text(0.55, 0.7, f"{preferences[2].upper()}", color=DisplayConfig.INFO_TEXT, fontsize=12)


def _configure_main_dashboard_plot(ax_handle):
    ax_handle.set_facecolor(DisplayConfig.BACKGROUND)
    ax_handle.xaxis.set_major_locator(MultipleLocator(1))
    ax_handle.yaxis.set_major_locator(MultipleLocator(1))
    ax_handle.set_ylim([1, 10.5])
    ax_handle.set_xlim([4.7, 23.5])
    ax_handle.tick_params(axis='x', colors='white')
    ax_handle.tick_params(axis='y', colors='white')
    ax_handle.spines['top'].set_visible(False)
    ax_handle.spines['right'].set_visible(False)
    ax_handle.spines['left'].set_visible(False)
    ax_handle.spines['bottom'].set_color('white')
    ax_handle.set_ylabel("BOT RATING", color='white', fontweight="light")


def _add_maxed(fig_handle, pos, asset_file):
    ax_max = fig_handle.add_axes(pos)
    im_max = mpimg.imread(asset_file)
    ax_max.imshow(im_max)
    ax_max.xaxis.set_visible(False)
    ax_max.yaxis.set_visible(False)
    ax_max.set_facecolor(DisplayConfig.BACKGROUND)
    ax_max.spines['right'].set_visible(False)
    ax_max.spines['left'].set_visible(False)
    ax_max.spines['bottom'].set_visible(False)
    ax_max.spines['top'].set_visible(False)


def _plot_dial(fig_handle, ax_handle, val, max_val, maxed_pos, maxed_asset, icon_asset, dial_colour):
    ccw = False
    if 0 < val <= max_val:
        groups = [val / max_val, 1 - val / max_val]
    elif val == 0:
        groups = [0.01, 0.99]
    elif val >= max_val:
        groups = [max_val, 0]
        _add_maxed(fig_handle, maxed_pos, maxed_asset)
    else:  # only valid for temperature where a negative value is possible
        groups = [abs(val) / max_val, 1 - abs(val) / max_val]
        ccw = True
    ax_handle.pie(groups, colors=[dial_colour, DisplayConfig.SEGMENTS], startangle=90, counterclock=ccw)
    my_circle = plt.Circle((0, 0), 0.7, color=DisplayConfig.BACKGROUND)
    ax_handle.add_artist(my_circle)
    im_icon = mpimg.imread(icon_asset)
    icon = OffsetImage(im_icon, zoom=0.18)
    ab_icon = AnnotationBbox(icon, (0, 0), frameon=False)
    ax_handle.add_artist(ab_icon)


def _add_dial_text(ax_handle, morn_param, aft_param, eve_param, unit):
    ax_handle.text(1.3, 0.4, "M:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    ax_handle.text(1.8, 0.4, f"{morn_param:.1f}{unit}", color=DisplayConfig.INFO_TEXT, fontsize=12)
    ax_handle.text(1.3, -0.2, "A:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    ax_handle.text(1.8, -0.2, f"{aft_param:.1f}{unit}", color=DisplayConfig.INFO_TEXT, fontsize=12)
    ax_handle.text(1.3, -0.8, "E:", color=DisplayConfig.INFO_FIELD, fontsize=12)
    ax_handle.text(1.8, -0.8, f"{eve_param:.1f}{unit}", color=DisplayConfig.INFO_TEXT, fontsize=12)


def plot_scores(day, rankings, to_show, filename):
    """Generate dashboard plot for a given day and save to disk or show to user.

    Args:
        day (): DayWeather object to be plotted
        rankings (list): List of Segment objects at those levels in preference order
        to_show (bool): True - plt.show() is called, False - it isn't and the plot is cleared
        filename (str): File path (relative to the project directory) where the plot is to be saved

    """

    time, temp, wind, precip = _generate_forecast_lines(day)

    # Create the figure
    fig = plt.figure("Weather Dashboard", figsize=(8, 4.5))  # 16 x 9 aspect ratio for twitter
    gs = fig.add_gridspec(nrows=3, ncols=4, left=0.08, bottom=0.12, top=0.95)
    gs.update(wspace=-0.1)
    fig.patch.set_facecolor(DisplayConfig.BACKGROUND)

    _add_dashboard_text_to_figure(fig, day, rankings)

    # MAIN DASHBOARD PLOT
    ax = fig.add_subplot(gs[-2:, :-1])
    for name, seg in day.segments.items():
        rect_width = seg.duration + 0.9
        x = seg.start_time.hour
        rect = patches.Rectangle((x, 1), rect_width, 9, edgecolor='none', facecolor=DisplayConfig.SEGMENTS)
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

    _configure_main_dashboard_plot(ax)

    ax.plot(time, temp + 1, color=DisplayConfig.TEMP, linewidth=4.0, zorder=5)
    ax.plot(time, wind + 1, color=DisplayConfig.WIND, linewidth=4.0, zorder=5)
    ax.plot(time, precip + 1, color=DisplayConfig.PRECIP, linewidth=4.0, zorder=5)

    # DASHBOARD DIALS
    # Temperature Dial
    ax_temp = fig.add_subplot(gs[0, -1])
    max_temp = 40  # degrees C
    _plot_dial(fig, ax_temp, day.temp_c, max_temp, [0.77, 0.925, 0.04, 0.04],
               'assets/maxed_temp.png', 'assets/therm.png', DisplayConfig.TEMP)
    _add_dial_text(ax_temp, day.segments['morning'].temp_c, day.segments['afternoon'].temp_c,
                   day.segments['evening'].temp_c, "°C")

    # Wind Speed Dial
    ax_wind = fig.add_subplot(gs[1, -1])
    max_wind = 30  # mps
    _plot_dial(fig, ax_wind, day.wind_mps, max_wind, [0.77, 0.634, 0.04, 0.04],
               'assets/maxed_wind.png', 'assets/wind.png', DisplayConfig.WIND)
    _add_dial_text(ax_wind, day.segments['morning'].wind_mps, day.segments['afternoon'].wind_mps,
                   day.segments['evening'].wind_mps, "m/s")

    # Precipitation Volume Dial
    ax_precip = fig.add_subplot(gs[2, -1])
    max_precip = 20  # mm
    _plot_dial(fig, ax_precip, day.precipitation_mm, max_precip, [0.77, 0.34, 0.04, 0.04],
               'assets/maxed_precip.png', 'assets/drop.png', DisplayConfig.PRECIP)
    _add_dial_text(ax_precip, day.segments['morning'].precipitation_mm, day.segments['afternoon'].precipitation_mm,
                   day.segments['evening'].precipitation_mm, "mm")

    if filename:
        fig.savefig(filename)

    if to_show:
        plt.show()
    else:
        plt.close()
