import weather_config


class TimePeriod:
    def __init__(self):
        self.temp_c = 0
        self.temp_score = 0
        self.wind_mps = 0
        self.wind_score = 0
        self.precipitation_type = 0
        self.precipitation_volume = 0
        self.precipitation_score = 0
        self.weather_icon = ""


class WholeDay(TimePeriod):
    def __init__(self, date):
        super().__init__()
        self.date = date
        self.sunrise = 0
        self.sunset = 0


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
        return f"{self.__class__.__name__}({self.name.title()},({self.start_time} - {self.end_time}))"


class Hour(TimePeriod):
    def __init__(self, hr):
        super().__init__()
        self.hr = hr


segments = []
for window_name, window_times in weather_config.TIME_WINDOWS.items():
    start, end = window_times
    segments.append(DaySegment(window_name, start, end))
