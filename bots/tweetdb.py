import os
import random
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Text, Boolean, Integer, VARCHAR, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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


class Content:
    sentence = Column(Text)
    tone = Column(VARCHAR(20))
    used = Column(Boolean)
    uses = Column(Integer)

    def __init__(self, sentence, tone, used, uses):
        self.sentence = sentence
        self.tone = tone
        self.used = used
        self.uses = uses


class Intro(base, Content):
    __tablename__ = 'intros'
    intros_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f'<Intro: "{self.sentence}">'


class Forecast(base, Content):
    __tablename__ = 'forecasts'
    forecasts_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f'<Forecast: "{self.sentence}">'


class Outro(base, Content):
    __tablename__ = 'outros'
    outros_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f'<Outro: "{self.sentence}">'


class TweetData:
    def __init__(self):
        self.engine = None
        self.session = None

        self.connect()

    def connect(self):
        self.engine = create_engine(os.getenv("PG_DB_URI"))
        Session = sessionmaker(self.engine)
        self.session = Session()

    def add_sentence(self, table, new_sentence, tone):
        new_record = table(sentence=new_sentence, tone=tone, used=False, uses=0)
        self.session.add(new_record)
        self.session.commit()

    def edit_sentence(self, table, old_sentence, new_sentence):
        pass

    def remove_sentence(self, table, sentence):
        pass

    def choose_from_unused(self, table, tone):
        unused_records = self.session.query(table).filter(table.used==False, table.tone==tone).all()

        if unused_records:
            random_record = random.choice(unused_records)
            random_record.used = True
            random_record.uses += 1
            self.session.commit()
            print(random_record.sentence)
            # return random_record.sentence

        # If there are no unused sentences, reset and repeat...
        else:
            # Reset "used" column, i.e. set all to False
            self.session.query(table).update({table.used: False})
            self.session.commit()
            # Recall method
            self.choose_from_unused(table, tone)

    def _print_sentences(self, table):
        records = self.session.query(table)
        for record in records:
            print(record.sentence)
