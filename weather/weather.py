from datetime import date, time, datetime


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


class Hour(TimePeriod):
    def __init__(self):
        super().__init__()
