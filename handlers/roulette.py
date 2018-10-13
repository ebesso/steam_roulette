from init_app import socketio, db

from sqlalchemy import create_engine

from handlers import bet, configuration

from models import Base, Roulette

import os

timer = 0

config = configuration.get('roulette')

def time_roulettes():
    global timer  
    timer += 1

    if timer < int(config.interval):
        socketio.emit('update_time', str(int(config.interval) - timer), broadcast=True)

    if timer == int(config.interval):
        winning_alternative = bet.lottery()
        socketio.emit('run_script', str(winning_alternative), broadcast=True)
        bet.finish_round(winning_alternative)

    if timer == int(config.interval) + 3:
        timer = 0

def init_roulette():
    Base.metadata.create_all(create_engine(os.environ['DATABASE_URL']))
    db.session.commit()    

    if db.session.query(Roulette).filter(Roulette.id == 1).count() == False:
        roulette = Roulette()
        roulette.current_round = 1

        db.session.add(roulette)
        db.session.commit()
