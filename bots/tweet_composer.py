import bots.tweet_config as config
import yaml
import numpy as np
import random
import re


def _add_selections_to_tweet(tweet_text, selections):
    text_with_selection = tweet_text
    for selection in selections:
        text_with_selection = re.sub("NOUN", selection, text_with_selection, count=1)

    if selections[0] == "afternoon" or selections[0] == "evening":
        text_with_selection_and_indef = re.sub("A\(N\)", "an", text_with_selection)
    else:
        text_with_selection_and_indef = re.sub("A\(N\)", "a", text_with_selection)
    return text_with_selection_and_indef


def get_tweet_templates(yaml_filename="tweet_content.yaml"):
    with open(yaml_filename, 'r', encoding="utf8") as f:
        templates_dict = yaml.load(f)
    return templates_dict


def compose_tweet(selections, tone, templates_dict, config=config):
    intro_text = random.choice(templates_dict['Intro'][tone])
    selection_text = random.choice(templates_dict[f'Selection text {len(selections)}'][tone])
    outro_text = random.choice(templates_dict['Outro'][tone])

    selection_text = _add_selections_to_tweet(selection_text, selections)

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
        a_tweet = compose_tweet(results, level, templates, config)
        print(a_tweet)
