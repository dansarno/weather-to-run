import credentials as cred
import requests
import json

api_key = cred.API_KEY
# Lat and long of London
lat = 51.5074
lon = 0.1278

url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,daily&appid={api_key}"
response = requests.get(url)

x = response.json()

print(x)
