import config
import tweepy

# Create API object
api = config.create_api(True)

# Create a test tweet
api.update_status("This is a test tweet: is it a good time to run?")
