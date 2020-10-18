from config import TweetConfig
import yaml
from bots.tweetdb import TweetDB, Intro, Forecast, Outro
import random
import re


def add_selections_to_tweet(tweet_text, selections):
    """Replace placeholder characters with correct words given a selections list.

    Args:
        tweet_text (str): A tweet template sentence from tweet_content.yaml
        selections (list): A list of the names of the segments of the day (in preference order)

    Returns:
        text_with_selection: A grammatically correct sentence with the selections substituted in

    """
    text_with_selection = tweet_text
    for selection in selections:
        text_with_selection = re.sub("NOUN", selection, text_with_selection, count=1)

    if selections[0] == "afternoon" or selections[0] == "evening":
        text_with_selection = re.sub("A\(N\)", "an", text_with_selection)
    else:
        text_with_selection = re.sub("A\(N\)", "a", text_with_selection)
    return text_with_selection


def get_tweet_templates(yaml_filename="../data/tweet_content.yaml"):
    """Read the tweet content yaml file and return a dictionary of template sentences to be formed into tweets"""
    with open(yaml_filename, 'r', encoding="utf8") as f:
        templates_dict = yaml.load(f, Loader=yaml.FullLoader)
    return templates_dict


def compose_tweet(selections, tone, config=TweetConfig):
    """Forms a full tweet given segment preferences and an overall tone of the tweet.

    Full tweets are comprised of an intro, a weather sentence and an outro. The intros and outros have a less
    than 100% chance of being included in the tweet (determined by tweet_TweetConfig). The tweet components are randomly
    selected from the tweet content yaml file give a tone

    Args:
        selections (list): A list of the names of the segments of the day (in preference order)
        tone (str): Equivalent to alert level of the weather for the day (green, amber, red)
        config (class): Class containing probably constants for intros and outros

    Returns:
        Full tweet string
    """

    if config.CONTENT_SOURCE == "yaml":
        templates_dict = get_tweet_templates()
        intro_text = random.choice(templates_dict['Intro'][tone])
        selection_text = random.choice(templates_dict[f'Selection text {len(selections)}'][tone])
        outro_text = random.choice(templates_dict['Outro'][tone])
        selection_text = add_selections_to_tweet(selection_text, selections)

        tweet_composition = []
        if random.random() < config.PROB_OF_INTRO:
            tweet_composition.append(intro_text)
        tweet_composition.append(selection_text)
        if random.random() < config.PROB_OF_OUTRO:
            tweet_composition.append(outro_text)

        return " ".join(tweet_composition)

    elif config.CONTENT_SOURCE == "database":
        db = TweetDB(config.DB_URI)

        intro = db.choose_from_unused(Intro, tone.lower())
        forecast = db.choose_from_unused(Forecast, tone.lower(), len(selections))
        outro = db.choose_from_unused(Outro, tone.lower())

        # Add selections fot text
        forecast_text = add_selections_to_tweet(forecast.sentence, selections)

        tweet_composition = []
        if random.random() < config.PROB_OF_INTRO:
            tweet_composition.append(intro.sentence)
        tweet_composition.append(forecast_text)
        if random.random() < config.PROB_OF_OUTRO:
            tweet_composition.append(outro.sentence)

        tweet_text = " ".join(tweet_composition)
        db.add_tweet(intro, forecast, outro, tweet_text)

        return tweet_text

    else:
        raise ValueError


if __name__ == "__main__":
    level = "Green"
    results = ["afternoon", "evening", "morning"]

    templates = get_tweet_templates()

    for _ in range(100):
        a_tweet = compose_tweet(results, level, templates)
        print(a_tweet)
