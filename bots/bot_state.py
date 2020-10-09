import tweepy


class TwitterProfile:
    """A class representing the state of a twitter profile.

    Attributes:
        followers (list): List of followers
        last_mention_id (int): The most recent tweet id in the mentions timeline of the account

    """
    def __init__(self, api):
        self.followers = list(tweepy.Cursor(api.followers).items())
        self.last_mention_id = list(tweepy.Cursor(api.mentions_timeline).items(1))[0].id
