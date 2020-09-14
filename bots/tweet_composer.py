import yaml
import numpy as np
import random
import re


def add_selections_to_tweet(tweet_text, selections):
    text_with_selection = tweet_text
    for selection in selections:
        text_with_selection = re.sub("NOUN", selection, text_with_selection, count=1)

    if selections[0] == "afternoon" or selections[0] == "evening":
        text_with_selection_and_indef = re.sub("A\(N\)", "an", text_with_selection)
    else:
        text_with_selection_and_indef = re.sub("A\(N\)", "a", text_with_selection)
    return text_with_selection_and_indef


with open('tweet_content.yaml', 'r', encoding="utf8") as f:
    doc = yaml.load(f)

tone = "Green"
results = ["afternoon"]
weathers = len(results)
prob_of_no_intro = 0.7
prob_of_no_outro = 0.75

for _ in range(100):
    start = random.choice(doc['Intro'][tone])
    middle = random.choice(doc[f'Weather text {weathers}'][tone])
    end = random.choice(doc['Outro'][tone])

    formed_middle = add_selections_to_tweet(middle, results)

    tweet_construction = []
    if random.random() < prob_of_no_intro:
        tweet_construction.append(start)
    tweet_construction.append(formed_middle)
    if random.random() < prob_of_no_outro:
        tweet_construction.append(end)

    tweet = " ".join(tweet_construction)
    print(tweet)
