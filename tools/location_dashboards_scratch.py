from bots import auto_reply_bot

text = "Belfast"
loc, offset_sec = auto_reply_bot.text_to_location(text)
if loc:
    reply_text, dashboard_file = auto_reply_bot.tweet_your_weather(loc, offset_sec)
    print(reply_text)
else:
    print("Cannot find this location")


