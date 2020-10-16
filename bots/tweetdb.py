import os
import random
from sqlalchemy import create_engine
from sqlalchemy import Column, Text, Boolean, Integer, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, synonym

base = declarative_base()


class Intro(base):
    __tablename__ = 'intros'

    intros_id = Column(Integer, primary_key=True)
    primary_id = synonym("intros_id")
    sentence = Column(Text)
    tone = Column(VARCHAR(20))
    used = Column(Boolean)
    uses = Column(Integer)


class Forecast(base):
    __tablename__ = 'forecasts'

    forecasts_id = Column(Integer, primary_key=True)
    primary_id = synonym("forecasts_id")
    sentence = Column(Text)
    tone = Column(VARCHAR(20))
    used = Column(Boolean)
    uses = Column(Integer)


class Outro(base):
    __tablename__ = 'outros'

    outros_id = Column(Integer, primary_key=True)
    primary_id = synonym("outros_id")
    sentence = Column(Text)
    tone = Column(VARCHAR(20))
    used = Column(Boolean)
    uses = Column(Integer)


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

    def choose_from_unused(self, table):
        all_unused_records = [record for record in self.session.query(table).filter_by(used=False)]

        # If there are some unused sentences...
        if all_unused_records:
            random_record = random.choice(all_unused_records)
            random_record.used = True
            random_record.uses += 1
            self.session.commit()
            print(random_record.sentence)
            # return random_record.sentence

        # If there are no unused sentences, reset and repeat...
        else:
            # Reset "used" column
            for record in self.session.query(table):
                record.used = False
            self.session.commit()
            # Recall method
            self.choose_from_unused(table)

    def _print_sentences(self, table):
        records = self.session.query(table)
        for record in records:
            print(record.sentence)
