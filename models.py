from sqlalchemy import String, Date, Float, Column, Integer, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
import datetime, random, string, enum

Base = declarative_base()

class Trade_offer_types(enum.Enum):
    deposit = 1
    withdraw = 2

class Sent_trade_offer(enum.Enum):
    success = 1
    fail = 2

class Rig(Base):
    __tablename__ = 'rigs'

    id = Column('id', Integer, primary_key=True)

    roulette_round = Column('tournament_round', Integer, unique=True, nullable=False)
    winning_alternative = Column('winning_alternative', Integer, nullable=False)

    def __init__(self, roulette_round, winning_alternative):
        self.roulette_round = roulette_round
        self.winning_alternative = winning_alternative


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True)

    steamid = Column('steamid', String, unique=True)
    balance = Column('balance', Float, nullable=False)
    register_date = Column('register_date', Date, nullable=False)

    trade_link = Column('trade_link', String)

    user_identifier = Column('user_identifier', String)

    def __init__(self, steamid):
        self.steamid = steamid
        self.balance = 0
        self.trade_link = None
        self.register_date = datetime.datetime.today().date()
        self.user_identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

class Bet(Base):
    __tablename__ = 'bets'

    id = Column('id', Integer, primary_key=True)

    amount = Column('amount', Float, nullable=False)
    steamid = Column('steamid', String, nullable=False)
    roulette_round = Column('roulette_round', Integer, nullable=False)
    alternative = Column('alternative', Integer, nullable=False)
    date = Column('date', Date, nullable=False)

    def __init__(self, amount, steamid, alternative, roulette_round):
        self.alternative = alternative
        self.amount = amount
        self.steamid = steamid
        self.roulette_round = roulette_round
        self.date = datetime.datetime.now().date()

class Roulette(Base):
    __tablename__ = 'roulette'

    id = Column('id', Integer, primary_key=True)

    current_round = Column('current_round', Integer)

class Steam_item(Base):
    __tablename__ = 'items'

    id = Column('id', Integer, primary_key=True)

    market_hash_name = Column('market_hash_name', String, unique=True)
    price = Column('price', Float, nullable=False)

    def __init__(self, market_hash_name, price):
        self.market_hash_name = market_hash_name
        self.price = price

class Trade_offer(Base):
    __tablename__ = 'trade_offers'

    id = Column('id', Integer, primary_key=True)

    trade_type = Column('trade_type', Enum(Trade_offer_types))
    steamid = Column('steamid', String)

    offer_id = Column('offerid', String, unique=True)

    time_created = Column('time_created', Date)

    vgo_offer = Column('vgo_offer', Boolean)

    def __init__(self, trade_type, steamid, offer_id, vgo_offer):
        self.trade_type = trade_type
        self.steamid = steamid
        self.offer_id = offer_id
        self.time_created = datetime.datetime.today().date()
        self.vgo_offer = vgo_offer


class Empty(object):
    def __getattr__(self, prop):
        return self.__dict__[prop]
    def __setattr__(self, prop, val):
        self.__dict__[prop] = val

class User_auth(UserMixin, object):
    def __setattr__(self, prop, val):
        self.__dict__[prop] = val
    def __init__(self, steamid):
        self.id = steamid
