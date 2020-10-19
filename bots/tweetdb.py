import random
import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Text, Boolean, Integer, VARCHAR, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import TweetConfig
from urllib.parse import urlparse

base = declarative_base()


class Tweet(base):
    __tablename__ = 'tweets'
    tweets_id = Column(Integer, primary_key=True)
    date_posted = Column(DateTime)
    intros_id = Column(Integer, ForeignKey('intros.intros_id'))
    forecasts_id = Column(Integer, ForeignKey('forecasts.forecasts_id'))
    outros_id = Column(Integer, ForeignKey('outros.outros_id'))
    sentence = Column(Text)

    def __init__(self, date_posted, intros_id, forecasts_id, outros_id, sentence):
        self.date_posted = date_posted
        self.intros_id = intros_id
        self.forecasts_id = forecasts_id
        self.outros_id = outros_id
        self.sentence = sentence

    def __repr__(self):
        return f'<Tweet: "{self.sentence}">'


class Content:
    sentence = Column(Text, nullable=False)
    tone = Column(VARCHAR(20), nullable=False)
    used = Column(Boolean, nullable=False, default=False)
    uses = Column(Integer, nullable=False, default=0)
    deleted = Column(Boolean, nullable=False, default=False)

    def __init__(self, sentence, tone, used, uses):
        self.sentence = sentence
        self.tone = tone
        self.used = used
        self.uses = uses
        self.deleted = False


class Intro(Content, base):
    __tablename__ = 'intros'
    intros_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f'<Intro: "{self.sentence}">'


class Forecast(Content, base):
    __tablename__ = 'forecasts'
    forecasts_id = Column(Integer, primary_key=True)
    n_selections = Column(Integer, nullable=False)

    def __init__(self, sentence, tone, used, uses, n_selections):
        super().__init__(sentence, tone, used, uses)
        self.n_selections = n_selections

    def __repr__(self):
        return f'<Forecast: "{self.sentence}">'


class Outro(Content, base):
    __tablename__ = 'outros'
    outros_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f'<Outro: "{self.sentence}">'


class TweetDB:
    def __init__(self, db_uri=TweetConfig.DB_URI):
        self.engine = None
        self.session = None
        self.uri = db_uri

        self.connect()

    def __repr__(self):
        url_components = urlparse(self.uri)
        dbname = url_components.path[1:]
        return f'<db: "{dbname}">'

    def connect(self):
        self.engine = create_engine(self.uri)
        Session = sessionmaker(self.engine)
        self.session = Session()

    def add_sentence(self, table, new_sentence, tone, n_selections=0):
        print(f'Adding "{new_sentence}"...')
        if n_selections:
            new_record = table(sentence=new_sentence, tone=tone, used=False, uses=0, n_selections=n_selections)
        else:
            new_record = table(sentence=new_sentence, tone=tone, used=False, uses=0)
        self.session.add(new_record)
        self.session.commit()

    def edit_sentence(self, table, record_id, new_sentence):
        record_to_edit = self.session.query(table).get(record_id)
        if record_to_edit:
            record_to_edit.sentence = new_sentence
            self.session.commit()
            print("Successful edit")
        else:
            raise ValueError

    def remove_sentence(self, table, record_id):
        record_to_delete = self.session.query(table).get(record_id)
        if record_to_delete:
            record_to_delete.deleted = True
            self.session.commit()
            print("Successful deletion")
        else:
            raise ValueError

    def choose_from_unused(self, table, tone, n_selections=0):
        if n_selections:
            unused_records = self.session.query(table).filter(table.used==False,
                                                              table.deleted==False,
                                                              table.tone==tone,
                                                              table.n_selections==n_selections).all()
        else:
            unused_records = self.session.query(table).filter(table.used==False,
                                                              table.deleted==False,
                                                              table.tone==tone).all()

        if unused_records:
            random_record = random.choice(unused_records)
            random_record.used = True
            random_record.uses += 1
            self.session.commit()

        else:
            if n_selections:
                q = self.session.query(table).filter(table.tone == tone,
                                                     table.deleted == False,
                                                     table.n_selections==n_selections)
            else:
                q = self.session.query(table).filter(table.tone == tone, table.deleted==False)
            # Reset "used" column, i.e. set all to False
            q.update({table.used: False})
            records = q.all()
            random_record = random.choice(records)
            random_record.used = True
            random_record.uses += 1
            self.session.commit()

        return random_record

    def add_tweet(self, intro, forecast, outro, tweet, date=datetime.datetime.now()):
        new_tweet = Tweet(date, intro.intros_id, forecast.forecasts_id, outro.outros_id, tweet)
        self.session.add(new_tweet)
        self.session.commit()

    def form_tweet(self, tone, n_selections):
        intro = self.choose_from_unused(Intro, tone)
        forecast = self.choose_from_unused(Forecast, tone, n_selections)
        outro = self.choose_from_unused(Outro, tone)

        tweet = f"{intro.sentence} {forecast.sentence} {outro.sentence}"
        print(tweet)
        new_tweet = Tweet(datetime.datetime.now(), intro.intros_id, forecast.forecasts_id, outro.outros_id, tweet)
        self.session.add(new_tweet)
        self.session.commit()

    def _print_sentences(self, table):
        records = self.session.query(table)
        for record in records:
            print(record.sentence)

    def _reset_table(self, table):
        self.session.query(table).update({table.uses: 0, table.used: False})
        self.session.commit()

    def _clear_table(self, table):
        all_records = self.session.query(table).all()
        for record in all_records:
            self.session.delete(record)
        self.session.commit()
