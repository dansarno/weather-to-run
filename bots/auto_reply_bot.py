from opencage.geocoder import OpenCageGeocode
import os
from geotext import GeoText


def create_geocoder_obj():
    geocoder_api_key = os.getenv("GEOCODER_API_KEY")
    return OpenCageGeocode(geocoder_api_key)


def text_to_location(tweet_text):
    """Generates a location dictionary (city name and coordinates) given a sentence string.

    Uses geotext package to search a string for recognised city names contained within it. Then uses the opencage
    package to retrieve the latitude and longitude coordinates of the given city and forms a dictionary of the city
    name (key) and a tuple of the coordinates (value)

    Args:
        tweet_text (str): Sentence string

    Returns:
        Location dict or None: If a recognised city is in the tweet_text, a location is returned. Else, return None
    """
    geo = create_geocoder_obj()

    city_list = GeoText(tweet_text).cities
    if city_list:
        city_str = city_list[0]
        result = geo.geocode(city_str, no_annotations=1)
        return {city_str: (result[0]["geometry"]["lat"], result[0]["geometry"]["lng"])}
    else:
        return None
