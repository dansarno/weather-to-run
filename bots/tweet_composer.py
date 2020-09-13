import yaml
import numpy as np
import random

with open('tweet_content.yaml', 'r', encoding="utf8") as f:
    doc = yaml.load(f)

tone = "Green"
weathers = 2
prob_of_no_intro = 0.3
prob_of_no_outro = 0.25

for _ in range(100):
    start = random.choice(doc['Intro'][tone])
    middle = random.choice(doc[f'Weather text {weathers}'][tone])
    end = random.choice(doc['Outro'][tone])

    tweet_construction = []
    if random.random() > prob_of_no_intro:
        tweet_construction.append(start)
    tweet_construction.append(middle)
    if random.random() > prob_of_no_outro:
        tweet_construction.append(end)

    tweet = " ".join(tweet_construction)
    print(tweet)
