from config import TweetConfig
import yaml
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


def get_tweet_templates(yaml_filename="tweet_content.yaml"):
    """Read the tweet content yaml file and return a dictionary of template sentences to be formed into tweets"""
    with open(yaml_filename, 'r', encoding="utf8") as f:
        templates_dict = yaml.load(f, Loader=yaml.FullLoader)
    return templates_dict


def compose_tweet(selections, tone, templates_dict, config=TweetConfig):
    """Forms a full tweet given segment preferences and an overall tone of the tweet.

    Full tweets are comprised of an intro, a weather sentence and an outro. The intros and outros have a less
    than 100% chance of being included in the tweet (determined by tweet_TweetConfig). The tweet components are randomly
    selected from the tweet content yaml file give a tone

    Args:
        selections (list): A list of the names of the segments of the day (in preference order)
        tone (str): Equivalent to alert level of the weather for the day (green, amber, red)
        templates_dict (dict): A dictionary of template sentences
        config (class): Class containing probably constants for intros and outros

    Returns:
        Full tweet string
    """
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


if __name__ == "__main__":
    level = "Green"
    results = ["afternoon", "evening", "morning"]

    templates = get_tweet_templates()

    for _ in range(100):
        a_tweet = compose_tweet(results, level, templates)
        print(a_tweet)
