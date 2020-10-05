# Weather Twitter Bot For London Runners

Twitter account: [@weather_to_run](https://twitter.com/weather_to_run)

Using data from OpenWeather, this simple Twitter bot scores the next day's weather forecast (based 
on a judgement of the best conditions for running) and informs the bot's Twitter followers what time 
of the day is best to go out.

The format of these tweets are: text status with the best time of the day for running along with a 
"dashboard" image with additional information of the next day's weather.

#### Example Tweet

Status Update:

"I got morning, afternoon and evening. In that order."

Media:

![Example of a weather dashboard](readme_images/dashboard_23-09-20.jpg)

## Automation
The following is a description of the automated processes performed by the Twitter bot.

### Daily Tweet
Tweets when it thinks the best time to run is tomorrow. These tweets are scheduled for at 10pm London time 
and follow the format outlined above.

### Auto-Reply

Automatically replies to Twitter users that @ mentions the account to discover what the bot thinks the best
time to run in their location is. The replies must follow these formatting rules (outlined in the bot's bio):
- Be an @ mention to the [@weather_to_run](https://twitter.com/weather_to_run) account
- Use the hashtag #myweather
- Contain their location information as the english name and spelling of the nearest major city. The city name can be
anywhere in the body of the tweet text. For example "[@weather_to_run](https://twitter.com/weather_to_run) #myweather
can you tell me the weather in the great city of Manchester? Thanksss" will pick out the city name Manchester.
    
An example reply and response by the Twitter bot would be:

Reply: "[@weather_to_run](https://twitter.com/weather_to_run) #myweather Houston"

Bot response: "\[Incoming Alert\] The morning is best for a run, that's my best guess... I say go for it"

![Examples of auto-reply dashboard](readme_images/auto_reply_demo.gif)

### Follow Back
_Not yet implemented_

Automatically follows anyone who follows the [@weather_to_run](https://twitter.com/weather_to_run) account.

## Behind the Scenes

### Day Weather Object

Encapsulation of OpenWeatherMap's One Call API response, adding a model layer and other convenient functionality 
on top of it. 

The One Call API response returns weather data for a given geographic location. The main information used in this model
are the:
- Hourly forecast for 48 hours
- Daily forecast for 7 days

The call provides data for a number of weather parameters - for more information, see
[Open Call API documentation](https://openweathermap.org/api/one-call-api). However, only weather parameters that are
most useful to assess the best running conditions are incorporated into the model. These are:
- Temperature
- Feels like temperature
- Wind speed
- Weather condition code
- Precipitation probability
- Precipitation volume

Encapsulation of the API response allows for more convenient handling of hours and days, as well as the addition of
any arbitrary period of the time (morning, afternoon and evening) with the same interface, attributes and methods.

A TimeElement is the "base" class. Any portion of time is a form of TimeElement and has all of the weather parameters
outlined above, along with their associated scores. Since an hour is considered the smallest unit of time
in this model, it directly inherits from TimeElement and is described in the concrete class Hour.

In order to provide a common interface, the class TimePeriod outlines spans of time like days and segments of the day.
The TimePeriod class inherits from TimeElement and is composed of a number of Hour objects. 
This class also has methods for aggregation the weather conditions and scores over its time period.
Concrete classes for DaySegment and Day inherit from TimePeriod and add the final level of specificity for attributes 
and methods of those periods of time. For example, the Day class uniquely has the attributes sunset and sunrise
time.

### Tweet Generator

### Heroku Deployment