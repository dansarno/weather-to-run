import weather_config as config
import weather_forecast as fcast
import datetime


TOMORROW = datetime.date.today() + datetime.timedelta(days=1)
is_Local = True


class TimePeriod:
    def __init__(self):
        self.temp_c = 0
        self.temp_score = 0
        self.wind_mps = 0
        self.wind_score = 0
        self.precipitation_type = 0
        self.precipitation_score = 0


class Day(TimePeriod):
    def __init__(self, date=TOMORROW, segments=config.TIME_WINDOWS):
        super().__init__()
        self.sunrise = 0
        self.sunset = 0
        self.date = date
        self.location = config.LOCATION
        self.hours = []
        self.segments = [DaySegment(name, times[0], times[1]) for name, times in segments.items()]
        self.rankings = {"Green": [], "Amber": [], "Red": []}

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

    def _filter_forecast(self):
        for hour in self.hours:
            # Check if this hour is within any of the time segments
            for segment in self.segments:
                is_in_window = segment.start_time.hour <= hour.hr <= segment.end_time.hour
                if is_in_window:
                    segment.hours.append(hour)

    def weather_at_time(self, time):
        pass


class DaySegment(TimePeriod):
    def __init__(self, name, start_time, end_time):
        super().__init__()
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.duration = abs(end_time.hour - start_time.hour)
        self.hours = []

    def __str__(self):
        return f"DaySegment object called {self.name.title()} ({self.start_time} to {self.end_time})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name.title()} ({self.start_time} - {self.end_time}))"


class Hour(TimePeriod):
    def __init__(self, hr):
        super().__init__()
        self.hr = hr
