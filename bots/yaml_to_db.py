from bots import tweetdb
from bots import tweet_composer


def add_phrases(db_obj, yaml_dict, table, tone, n_selections=0):
    if table == tweetdb.Intro:
        sentences = yaml_dict["Intro"][tone.title()]
    elif table == tweetdb.Outro:
        sentences = yaml_dict["Outro"][tone.title()]
    elif table == tweetdb.Forecast:
        sentences = yaml_dict[f"Selection text {n_selections}"][tone.title()]
    else:
        raise ValueError

    for sentence in sentences:
        db_obj.add_sentence(table, sentence, tone, n_selections)


db = tweetdb.TweetDB()
content_dict = tweet_composer.get_tweet_templates()
add_phrases(db, content_dict, tweetdb.Forecast, "red", 3)
