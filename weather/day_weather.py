from weather import config
from weather import forecast
import datetime

is_Local = True


class TimeElement:
    """A base class representing any length of time (hour, segment, day) for which there can be weather properties.

    Attributes:
        temp_c (float): Temperature in degrees Celsius
        feels_like (float): "Feels like" temperature in degree Celsius
        temp_score (float): Temperature score, with 9 being the best conditions and 0 being the worst
        wind_mps (float): Wind speed in metres per second
        wind_score (float): Wind score, with 9 being the best conditions and 0 being the worst
        precipitation_type (str): Precipitation code from OpenWeatherMap
            see https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
        precipitation_score (float): Precipitation score, with 9 being the best conditions and 0 being the worst
        precipitation_prob (float): Probability of precipitation (0 to 1)
        precipitation_mm (float): Volume of precipitation in millimetres

    """
    def __init__(self):
        self.temp_c = 0
        self.feels_like = 0
        self.temp_score = 0
        self.wind_mps = 0
        self.wind_score = 0
        self.precipitation_type = ""
        self.precipitation_score = 0
        self.precipitation_prob = 0
        self.precipitation_mm = 0


class TimePeriod(TimeElement):
    """A class representing any generic length of time (segment, day) consisting of a number of hours.

    Attributes:
        hours (list): A list of the Hour objects belonging to the TimePeriod
        alert_level (str): Overall alert level of the weather for this TimePeriod (green, amber, red)

    """
    def __init__(self):
        super().__init__()
        self.hours = []
        self.alert_level = ""

    def aggregate_score(self, method="min"):
        """Averages or takes the minimum score of the hours in the TimePeriod for each weather parameters
         and sets those score attributes.

        Args:
            method (str): The method of score aggregation, either "min" or "average"

        """
        if self.hours:
            all_temp_scores = [hour.temp_score for hour in self.hours]
            all_wind_scores = [hour.wind_score for hour in self.hours]
            all_precip_scores = [hour.precipitation_score for hour in self.hours]

            if method.lower() == "min":
                self.temp_score = round(min(all_temp_scores), 2)
                self.wind_score = round(min(all_wind_scores), 2)
                self.precipitation_score = round(min(all_precip_scores), 2)
            elif method.lower() == "average":
                self.temp_score = round(sum(all_temp_scores) / len(all_temp_scores), 2)
                self.wind_score = round(sum(all_wind_scores) / len(all_wind_scores), 2)
                self.precipitation_score = all_precip_scores[len(all_precip_scores) // 2]
            else:
                print(f'Aggregate score method "{method}" not recognised')  # Need to raise an error here instead

    def judge_score(self, bands=config.ALERT_BANDS):
        """Sets the alert level attribute for this TimePeriod based off the worst score of any of the weather params.

        Args:
            bands (dict): The upper and lower score bands of the alert levels (green, amber, red)
        """
        worst_alert_level = ""
        worst_score = self.calc_worst_score()
        for alert_name, band_limits in bands.items():
            if band_limits[0] <= round(worst_score, 1) <= band_limits[1]:
                worst_alert_level = alert_name
        self.alert_level = worst_alert_level

    def calc_worst_score(self):
        """Calculate what, of all of the weather parameters, is the worst score."""
        return min([self.temp_score, self.wind_score, self.precipitation_score])


class Day(TimePeriod):
    """A class representing a 24 hour period.

    Attributes:
        sunrise (int): Sunrise time, Unix, UTC
        sunset (int): Sunset time, Unix, UTC
        date (object): datetime.day object
        location (dict): City name (key) and a tuple of the decimal geographic coordinates (value)
        rankings (dict): Alert levels (keys) and a list of Segment objects at those levels in preference order (values)
        segments (dict): Segment names (keys) and the Segment objects (values)

    """
    def __init__(self, date, segments=config.TIME_WINDOWS, location=config.LOCATION):
        super().__init__()
        self.sunrise = 0
        self.sunset = 0
        self.date = date
        self.location = location
        self.rankings = {"Green": [], "Amber": [], "Red": []}
        if date.isoweekday() in {6, 7}:  # i.e. is it the weekend?
            day_type = "weekend"
        else:
            day_type = "weekday"
        self.segments = {name: DaySegment(name, times[0], times[1]) for name, times in segments[day_type].items()}

        # Add forecast after attribute construction
        self.add_forecast()

    def __str__(self):
        return f"Day with date {self.date.strftime('%d/%m/%y')} and {len(self.segments)} segments: " \
               f"{', '.join([name.title() for name, segment in self.segments.items()])}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.date.strftime('%d/%m/%y')}, " \
               f"({', '.join([name.title() for name, segment in self.segments.items()])}))"

    def add_forecast(self):
        """Fetches the weather forecast and adds the weather parameters to the class attributes.

        Adds weather data to every time period level within a day (hour, segment, day). The data used is the 48 hour
        forecast, for an hour by hour breakdown, and the 7 day forecast, for a whole day summary along with other
        parameters like sunrise and sunset times. This information is filtered for the day and for the segment periods
        specified in the object instance.

        """
        # Fetch forecast using One Call API from OpenWeatherMap
        hourly_forecasts, daily_forecasts, timezone_offset = forecast.fetch_forecast(location=self.location)

        day_temps = []
        day_feels = []
        # Hour level
        for hour_forecast in hourly_forecasts:
            is_this_day = self.date == datetime.datetime.utcfromtimestamp(hour_forecast["dt"] + timezone_offset).date()
            if not is_this_day:
                continue
            this_hour = Hour(datetime.datetime.utcfromtimestamp(hour_forecast["dt"] + timezone_offset).hour)
            this_hour.temp_c = hour_forecast["temp"]
            this_hour.feels_like = hour_forecast["feels_like"]  # Using "feels like" temp makes sense for scoring
            this_hour.wind_mps = hour_forecast["wind_speed"]
            this_hour.precipitation_type = str(int(hour_forecast["weather"][0]["id"]))
            this_hour.precipitation_prob = hour_forecast["pop"]
            if "rain" in hour_forecast.keys():
                this_hour.precipitation_mm = hour_forecast["rain"]["1h"]
            self.hours.append(this_hour)  # add this hour to the day's hours list
            day_temps.append(hour_forecast["temp"])
            day_feels.append(hour_forecast["feels_like"])

        # Segment level
        self._segment_forecast()

        # Day level
        for day_forecast in daily_forecasts:
            is_this_day = self.date == datetime.datetime.utcfromtimestamp(day_forecast["dt"] + timezone_offset).date()
            if not is_this_day:
                continue
            self.sunrise = datetime.datetime.utcfromtimestamp(day_forecast["sunrise"] + timezone_offset).time()
            self.sunset = datetime.datetime.utcfromtimestamp(day_forecast["sunset"] + timezone_offset).time()
            self.temp_c = round(sum(day_temps) / len(day_temps), 2)  # Using average daily temperature for now
            self.feels_like = round(sum(day_feels) / len(day_feels), 2)  # Using average daily temperature for now
            self.wind_mps = day_forecast["wind_speed"]
            self.precipitation_type = str(int(day_forecast["weather"][0]["id"]))
            self.precipitation_prob = day_forecast["pop"]
            if "rain" in day_forecast.keys():
                self.precipitation_mm = day_forecast["rain"]

    def score_forecast(self, precip_scores_dict=config.PRECIPITATION_SCORES):
        """Maps weather conditions to scores for every hour in the day and aggregates scores over time periods.

        Mapping for temperature and wind speed to scores are continuous functions whereas the precipitation score is
        a discrete mapping from weather condition ids to scores using precip_scores_dict. Note: the temperature to
        score conversion uses the "feels like" temperature as its input and not the "true" temperature.

        Args:
            precip_scores_dict (dict): Dictionary mapping weather condition ids to a score for each (0 to 9)

        """
        # Hour level
        for hour in self.hours:
            hour.temp_score = forecast.temp_to_score(hour.feels_like)  # Using feels_like to score makes sense to me!
            hour.wind_score = forecast.wind_speed_to_score(hour.wind_mps)
            hour.precipitation_score = precip_scores_dict[hour.precipitation_type]

        # Segment level
        for seg_name, segment in self.segments.items():
            segment.aggregate_score(method="min")  # the worst weather in that given time period
            segment.judge_score()

        # Day level
        self.aggregate_score(method="min")  # not obvious if the alert level should judged off the worst or av score
        self.judge_score()

    def rank_segments(self, segments_to_rank=None):
        """Sorts segments in preference order and bins them in the "rankings" structure with the appropriate alert level

        For each segment to rank, this method orders the segments by best score, with the worst score in each used to
        summarise the whole segment. The segments are added into the ranking structure at the appropriate alert levels
        in this order to maintain information on the segment preference order.

        Args:
            segments_to_rank (list): List of segment to rank. This can be a subset of the segment in the day for example

        """
        # By default use all segments in the day if not specified otherwise
        if not segments_to_rank:
            segments_to_rank = list(self.segments.values())

        seg_and_worst_score = []
        for segment in segments_to_rank:
            # Out of temp, wind, precip... which is the worst and whats its score
            worst_score = segment.calc_worst_score()
            seg_and_worst_score.append([segment, worst_score])
        # Sort segments by worst score (descending)
        ordered_seg_and_worst_score = sorted(seg_and_worst_score, reverse=True, key=lambda x: x[1])

        self.rankings = {"Green": [], "Amber": [], "Red": []}  # reset rankings
        for segment, worst_score in ordered_seg_and_worst_score:
            for name, segment_list in self.rankings.items():
                if not segment.alert_level.lower() == name.lower():
                    continue
                segment_list.append(segment)

    def _segment_forecast(self):
        """Adds hours to the segments given their time windows and aggregates the weather over those time periods"""
        for hour in self.hours:
            # Check if this hour is within any of the time segments
            for seg_name, segment in self.segments.items():
                is_in_window = segment.start_time.hour <= hour.hr <= segment.end_time.hour
                if is_in_window:
                    segment.hours.append(hour)

        # Update segment attributes after segments have hours
        for seg_name, segment in self.segments.items():
            segment.aggregate_weather()


class DaySegment(TimePeriod):
    """A class representing a period/segment of the day e.g. morning

    Attributes:
        name (str): The name given to the period/segment of the day e.g. morning
        start_time (object): datetime.time object representing the start time of the DaySegment
        end_time (object): datetime.time object representing the end time of the DaySegment
        duration (int): number of whole hours in the DaySegment

    """
    def __init__(self, name, start_time, end_time):
        super().__init__()
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = abs(end_time.hour - start_time.hour)

    def __str__(self):
        return f"DaySegment object called {self.name.title()} ({self.start_time} to {self.end_time})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name.title()}({self.start_time} - {self.end_time}))"

    def aggregate_weather(self):
        """Averages, takes median or sums the weather params in the DaySegment and sets those DaySegment attributes.

        Averages temperature, "feels like" temperature, wind speed and precipitation probability. Takes the median
        weather condition as a summary of the weather during the segment. And sums the total precipitation volume
        over the segment.

        """
        all_temp_c = [hour.temp_c for hour in self.hours]
        all_feels_like = [hour.feels_like for hour in self.hours]
        all_wind_mps = [hour.wind_mps for hour in self.hours]
        all_precip_types = [hour.precipitation_type for hour in self.hours]
        all_precip_probs = [hour.precipitation_prob for hour in self.hours]
        all_precip_mm = [hour.precipitation_mm for hour in self.hours]

        self.temp_c = round(sum(all_temp_c) / len(all_temp_c), 2)
        self.feels_like = round(sum(all_feels_like) / len(all_feels_like), 2)
        self.wind_mps = round(sum(all_wind_mps) / len(all_wind_mps), 2)
        self.precipitation_type = all_precip_types[len(all_precip_types) // 2]  # this may need changing!
        self.precipitation_prob = round(sum(all_precip_probs) / len(all_precip_probs), 2)  # this may need changing!
        self.precipitation_mm = round(sum(all_precip_mm), 2)  # this may need changing!


class Hour(TimeElement):
    """A class representing the smallest element of time in this model.

    Attributes:
        hr (int): Hour of the day (0 to 23)
    """
    def __init__(self, hr):
        super().__init__()
        self.hr = hr

    def __str__(self):
        return f"Hour object at {self.hr:02}:00"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.hr:02})"
