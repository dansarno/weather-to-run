import datetime

TIME_WINDOWS = {
    "morning": [datetime.time(hour=6), datetime.time(hour=9)],
    "afternoon": [datetime.time(hour=12), datetime.time(hour=14)],
    "evening": [datetime.time(hour=17), datetime.time(hour=21)]
}

WEATHER_PARAMETERS = ["temperature", "wind", "precipitation"]

# ie equally weighted - CURRENTLY NOT USED!!!!
WEATHER_WEIGHTINGS = {"temperature": 0.33,
                      "wind": 0.33,
                      "precipitation": 0.33
                      }

LOCATION = {"London": (51.5074, 0.1278)}  # Needs to be generalised in the future

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
