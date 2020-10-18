import os
import datetime
import schedule

basedir = os.path.abspath(os.path.dirname(__file__))


class CredentialsConfig:
    # Weather
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    # Geocoder
    GEOCODER_API_KEY = os.getenv("GEOCODER_API_KEY")
    # Twitter
    TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
    TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
    TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_TOKEN_SECRET = os.getenv("TWITTER_TOKEN_SECRET")


class TweetConfig:
    PROB_OF_INTRO = 0.75
    PROB_OF_OUTRO = 0.75
    HASHTAG = "myweather"
    AUTO_REPLY_SCHEDULE = schedule.every(15).seconds
    FOLLOW_BACK_SCHEDULE = schedule.every(10).minutes
    DAILY_TWEET_SCHEDULE = schedule.every().day.at("22:00")
    CONTENT_SOURCE = "database"  # yaml or database
    DB_URI = os.getenv("PG_DB_URI")


class DisplayConfig:
    BACKGROUND = '#222831'
    SEGMENTS = '#30475e'
    TEMP = '#f30a49'
    WIND = '#29c7ac'
    PRECIP = '#46b5d1'
    INFO_FIELD = '#b0c4d9'
    INFO_TEXT = '#7691ad'


class WeatherConfig:
    TIME_WINDOWS = {
        "weekday": {
            "morning": [datetime.time(hour=6), datetime.time(hour=9)],
            "afternoon": [datetime.time(hour=12), datetime.time(hour=14)],
            "evening": [datetime.time(hour=17), datetime.time(hour=21)]
        },
        "weekend": {
            "morning": [datetime.time(hour=6), datetime.time(hour=11)],
            "afternoon": [datetime.time(hour=12), datetime.time(hour=16)],
            "evening": [datetime.time(hour=17), datetime.time(hour=21)]
        }
    }

    WEATHER_PARAMETERS = ["temperature", "wind", "precipitation"]

    # ie equally weighted - CURRENTLY NOT USED!!!!
    WEATHER_WEIGHTINGS = {"temperature": 0.33,
                          "wind": 0.33,
                          "precipitation": 0.33
                          }

    LOCATION = {"London": (51.5074, 0.1278)}

    # My judgement on the best weather conditions to run in (9-best, 0-worst)
    PRECIPITATION_SCORES = {
        # Storms  # Snow    # Rain    # Drizzle # Atmos   # Clouds  # Clear
        "200": 1, "600": 4, "500": 5, "300": 5, "701": 7, "801": 9, "800": 9,
        "201": 1, "601": 3, "501": 4, "301": 5, "711": 3, "802": 8,
        "202": 0, "602": 1, "502": 3, "302": 2, "721": 6, "803": 8,
        "210": 1, "611": 3, "503": 1, "310": 4, "731": 3, "804": 8,
        "211": 1, "612": 4, "504": 0, "311": 3, "741": 7,
        "212": 0, "613": 4, "511": 0, "312": 2, "751": 3,
        "221": 1, "615": 3, "520": 4, "313": 3, "761": 3,
        "230": 1, "616": 2, "521": 3, "314": 2, "762": 0,
        "231": 1, "620": 3, "522": 1, "321": 3, "771": 1,
        "232": 0, "621": 2, "531": 1, "781": 0,
        "622": 1
    }

    ALERT_BANDS = {
        "Green": [6.5, 9.0],
        "Amber": [3.0, 6.4],
        "Red": [0.0, 2.9]
    }
