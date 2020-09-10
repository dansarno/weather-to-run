import weather_config
import datetime


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


class Day(TimePeriod):
    def __init__(self, date=datetime.date.today() + datetime.timedelta(days=1), segments=weather_config.TIME_WINDOWS):
        super().__init__()
        self.sunrise = 0
        self.sunset = 0
        self.date = date
        self.segments = [DaySegment(name, times[0], times[1]) for name, times in segments.items()]
        self.best_segments = {"Green": [], "Amber": [], "Red": []}

    def __str__(self):
        return f"Day with date {self.date.strftime('%d/%m/%y')} and {len(self.segments)} segments: " \
               f"{', '.join([segment.name.title() for segment in self.segments])}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.date.strftime('%d/%m/%y')}, " \
               f"({', '.join([segment.name.title() for segment in self.segments])}))"


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
        return f"{self.__class__.__name__}({self.name.title()} ({self.start_time} - {self.end_time}))"


class Hour(TimePeriod):
    def __init__(self, hr):
        super().__init__()
        self.hr = hr

