import config

# Create API object
api = config.create_api(True)

# Create a test tweet
api.update_status("The curse of the third tweet!")
