from init_app import db

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models import User, Bet, Roulette, Rig
import os, random

from handlers import configuration

Session = scoped_session(sessionmaker(bind=create_engine(os.environ['DATABASE_URL'])))

def bet(user_identifier, bet_amount, alternative):

    user = db.session.query(User).filter(User.user_identifier == user_identifier).one()
    user.balance -= bet_amount
    db.session.commit()

    roulette_round = db.session.query(Roulette).filter(Roulette.id == 1).one().current_round

    user_bet = Bet(bet_amount, user.steamid, alternative, roulette_round)

    db.session.add(user_bet)
    db.session.commit()

def finish_round(winning_alternative):
    db = Session()
    config = configuration.get('roulette')


    for user_bet in db.query(Bet).filter(Bet.roulette_round == db.query(Roulette).filter(Roulette.id == 1).one().current_round):
        user = db.query(User).filter(User.steamid == user_bet.steamid).one()

        if user_bet.alternative == winning_alternative:
            if winning_alternative == 1 or winning_alternative == 2:
                user.balance += user_bet.amount * float(config.red_black_payout)
                db.commit()

            else:
                user.balance += user_bet.amount * float(config.green_payout)
                db.commit()

        print('user_bet: ' + str(user_bet.alternative))

    print('Winning Alternative: ' + str(winning_alternative))

    roulette = db.query(Roulette).filter(Roulette.id == 1).one()
    roulette.current_round += 1
    db.commit()
            

def lottery():
    db = Session()

    winning_number = random.randint(0, 14)
    
    if db.query(Rig).filter(Rig.roulette_round == db.query(Roulette).filter(Roulette.id == 1).one().current_round).count():
        print('Round rigged')
        return db.query(Rig).filter(Rig.roulette_round == db.query(Roulette).filter(Roulette.id == 1).one().current_round).one().winning_alternative

    if winning_number in range(1, 8):
        return 1
    if winning_number in range(8, 15):
        return 2
    if winning_number == 0:
        return 3



