import yaml
import numpy as np
import random
import re


def add_selections_to_tweet(tweet_text, selections):
    tweet_words = tweet_text.split(" ")
    correct_words = []
    choice = 0
    for word in tweet_words:
        if word == "NOUN":
            correct_words.append(selections[choice])
            if len(selections) > 1:
                choice += 1
        else:
            correct_words.append(word)
    formed_tweet = " ".join(correct_words)
    return formed_tweet


def add_selections_to_tweet2(tweet_text, selections):
    text_with_selection = re.sub("NOUN", selections[0], tweet_text)
    if selections[0] == "afternoon" or selections[0] == "evening":
        text_with_selection_and_indef = re.sub("A\(N\)", "an", text_with_selection)
    else:
        text_with_selection_and_indef = re.sub("A\(N\)", "a", text_with_selection)
    return text_with_selection_and_indef


with open('tweet_content.yaml', 'r', encoding="utf8") as f:
    doc = yaml.load(f)

tone = "Amber"
results = ["afternoon"]
weathers = len(results)
prob_of_no_intro = 0.3
prob_of_no_outro = 0.25

for _ in range(100):
    start = random.choice(doc['Intro'][tone])
    middle = random.choice(doc[f'Weather text {weathers}'][tone])
    end = random.choice(doc['Outro'][tone])

    formed_middle = add_selections_to_tweet2(middle, results)

    tweet_construction = []
    if random.random() > prob_of_no_intro:
        tweet_construction.append(start)
    tweet_construction.append(formed_middle)
    if random.random() > prob_of_no_outro:
        tweet_construction.append(end)

    tweet = " ".join(tweet_construction)
    print(tweet)
