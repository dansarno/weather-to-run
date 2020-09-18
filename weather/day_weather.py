from weather import weather_config as config
from weather import weather_forecast as fcast
import datetime


TOMORROW = datetime.date.today() + datetime.timedelta(days=1)
is_Local = True


class TimeElement:
    def __init__(self):
        self.temp_c = 0
        self.temp_score = 0
        self.wind_mps = 0
        self.wind_score = 0
        self.precipitation_type = ""
        self.precipitation_score = 0


class TimePeriod(TimeElement):
    def __init__(self):
        super().__init__()
        self.hours = []
        self.alert_level = ""

    def average_score(self):
        if self.hours:
            all_temp_scores = [hour.temp_score for hour in self.hours]
            all_wind_scores = [hour.wind_score for hour in self.hours]
            all_precip_scores = [hour.precipitation_score for hour in self.hours]

            self.temp_score = round(sum(all_temp_scores) / len(all_temp_scores), 2)
            self.wind_score = round(sum(all_wind_scores) / len(all_wind_scores), 2)
            self.precipitation_score = all_precip_scores[len(all_precip_scores) // 2]  # this may need changing!

    def judge_score(self, bands=config.ALERT_BANDS):
        worst_alert_level = ""
        worst_score = min([self.temp_score, self.wind_score, self.precipitation_score])
        for alert_name, band_limits in bands.items():
            if band_limits[0] <= round(worst_score, 1) <= band_limits[1]:
                worst_alert_level = alert_name
        self.alert_level = worst_alert_level
        return worst_score


class Day(TimePeriod):
    def __init__(self, date=TOMORROW, segments=config.TIME_WINDOWS):
        super().__init__()
        self.sunrise = 0
        self.sunset = 0
        self.date = date
        self.location = config.LOCATION
        self.segments = [DaySegment(name, times[0], times[1]) for name, times in segments.items()]
        self.rankings = {"Green": [], "Amber": [], "Red": []}

        self.add_forecast()

    def __str__(self):
        return f"Day with date {self.date.strftime('%d/%m/%y')} and {len(self.segments)} segments: " \
               f"{', '.join([segment.name.title() for segment in self.segments])}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.date.strftime('%d/%m/%y')}, " \
               f"({', '.join([segment.name.title() for segment in self.segments])}))"

    def add_forecast(self):
        hourly_forecasts, daily_forecasts = fcast.fetch_forecast(is_Local, location=self.location["London"])
        day_temps = []
        for hour_forecast in hourly_forecasts:
            is_this_day = self.date == datetime.datetime.fromtimestamp(hour_forecast["dt"]).date()
            if not is_this_day:
                continue
            this_hour = Hour(datetime.datetime.fromtimestamp(hour_forecast["dt"]).hour)
            this_hour.temp_c = hour_forecast["feels_like"]
            this_hour.wind_mps = hour_forecast["wind_speed"]
            this_hour.precipitation_type = str(int(hour_forecast["weather"][0]["id"]))
            self.hours.append(this_hour)
            day_temps.append(hour_forecast["feels_like"])

        self._filter_forecast()

        for day_forecast in daily_forecasts:
            is_this_day = self.date == datetime.datetime.fromtimestamp(day_forecast["dt"]).date()
            if not is_this_day:
                continue
            self.sunrise = datetime.datetime.fromtimestamp(day_forecast["sunrise"]).time()
            self.sunset = datetime.datetime.fromtimestamp(day_forecast["sunset"]).time()
            self.temp_c = round(sum(day_temps) / len(day_temps), 2)  # Using average daily temperature for now
            self.wind_mps = day_forecast["wind_speed"]
            self.precipitation_type = str(int(day_forecast["weather"][0]["id"]))

    def score_forecast(self, precip_scores_dict=config.PRECIPITATION_SCORES):
        for hour in self.hours:
            hour.temp_score = fcast.temp_c_to_score(hour.temp_c)
            hour.wind_score = fcast.wind_speed_to_score(hour.wind_mps)
            hour.precipitation_score = precip_scores_dict[hour.precipitation_type]

        for segment in self.segments:
            segment.average_score()

        self.average_score()
        self.judge_score()

    def rank_segments(self, segments_to_rank=None):
        # By default use all segments in the day if not specified otherwise
        if not segments_to_rank:
            segments_to_rank = self.segments

        seg_and_worst_score = []
        for segment in segments_to_rank:
            # Out of temp, wind, precip... which is the worst and whats its score
            worst_score = segment.judge_score()
            seg_and_worst_score.append([segment, worst_score])
        # Sort segments by worst score
        ordered_seg_and_worst_score = sorted(seg_and_worst_score, reverse=True, key=lambda x: x[1])

        self.rankings = {"Green": [], "Amber": [], "Red": []}  # reset rankings
        for segment, worst_score in ordered_seg_and_worst_score:
            for name, segment_list in self.rankings.items():
                if not segment.alert_level.lower() == name.lower():
                    continue
                segment_list.append(segment)

    def weather_at_time(self, time):
        pass

    def _filter_forecast(self):
        for hour in self.hours:
            # Check if this hour is within any of the time segments
            for segment in self.segments:
                is_in_window = segment.start_time.hour <= hour.hr <= segment.end_time.hour
                if is_in_window:
                    segment.hours.append(hour)

        # Update segment attributes after segments have hours
        for segment in self.segments:
            segment.average_weather()


class DaySegment(TimePeriod):
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

    def average_weather(self):
        all_temp_c = [hour.temp_c for hour in self.hours]
        all_wind_mps = [hour.wind_mps for hour in self.hours]
        all_precip_types = [hour.precipitation_type for hour in self.hours]

        self.temp_c = round(sum(all_temp_c) / len(all_temp_c), 2)
        self.wind_mps = round(sum(all_wind_mps) / len(all_wind_mps), 2)
        self.precipitation_type = all_precip_types[len(all_precip_types) // 2]  # this may need changing!


class Hour(TimeElement):
    def __init__(self, hr):
        super().__init__()
        self.hr = hr

    def __str__(self):
        return f"Hour object at {self.hr:02}:00"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.hr:02})"
