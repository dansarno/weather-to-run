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
Tweets when it thinks the best time to run is tomorrow. These tweets are scheduled for at 8pm London time 
and follow the format outlined above.

### Auto-Reply

Automatically replies to Twitter users that @ mentions the account to discover what the bot thinks the best
time to run in their location is. The replies must follow these formatting rules (outlined in the bot's bio):
- Be an @ mention to the [@weather_to_run](https://twitter.com/weather_to_run) account
- Use the hashtag #myweather
- Contain their location information, either as...
    - The english name and spelling of the nearest major city
    - Or, latitude and logitude coordinates (_not yet implemented_)
    
An example reply and response by the Twitter bot would be:

Reply: "@weather_to_run #myweather Houston"

Bot response: "\[Incoming Alert\] The morning is best for a run, that's my best guess... I say go for it"

![Examples of auto-reply dashboard](readme_images/auto_reply_demo.gif)

### Follow Back
_Not yet implemented_

Automatically follows anyone who follows the [@weather_to_run](https://twitter.com/weather_to_run) account.

## Behind the Scenes

### Day Weather Object

Encapsulation of OpenWeatherMap's One Call API response, adding a model layer and other convenient functionality 
on top of it.

### Tweet Generator

### Heroku Deployment