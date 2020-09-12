import config

# Create API object
api = config.create_api(True)

# Create a test tweet
api.update_status("Yet another twitter API test")
