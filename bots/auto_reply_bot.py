from opencage.geocoder import OpenCageGeocode
import os
from geotext import GeoText


def create_geocoder_obj():
    geocoder_api_key = os.getenv("GEOCODER_API_KEY")
    return OpenCageGeocode(geocoder_api_key)


def text_to_location(tweet_text):
    geo = create_geocoder_obj()

    city_list = GeoText(tweet_text).cities
    if city_list:
        city_str = city_list[0]
        result = geo.geocode(city_str, no_annotations=1)
        return {city_str: (result[0]["geometry"]["lat"], result[0]["geometry"]["lng"])}
    else:
        return None


if __name__ == "__main__":

    test_str = "fgdjk jkfgdjdh jfsklj fsfs Cork"
    ans = text_to_location(test_str)
    print(ans)
