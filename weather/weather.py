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


class Hour(TimePeriod):
    def __init__(self, hr):
        super().__init__()
        self.hr = hr


TIME_WINDOWS = {
    "morning": [datetime.time(hour=6), datetime.time(hour=9)],
    "midday": [datetime.time(hour=12), datetime.time(hour=14)],
    "evening": [datetime.time(hour=17), datetime.time(hour=21)]
}


morning = DaySegment("morning", datetime.time(), datetime.time())

segments = []
for window_name, window_times in TIME_WINDOWS.items():
    start, end = window_times
    segments.append(DaySegment(window_name, start, end))
