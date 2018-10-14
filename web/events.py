from init_app import db, socketio

from flask import request
from flask_login import login_required

from models import User

from handlers import bet, configuration, errors
from utilities import steamid_to_name, valid_identifier

import json

config = configuration.get('roulette')

@socketio.on('client_connected')
def client_message(json):
    socketio.emit('new_client', broadcast=True)

@socketio.on('update_user')
def update_user_event(data):
    if 'identifier' in data:
        user_identifier = data['identifier']
    else:
        return

    user_query = db.session.query(User).filter(User.user_identifier == user_identifier)

    if user_query.count():
        user = user_query.one()

        socketio.emit('update_user_response', str(user.balance), room=request.sid)

@socketio.on('client_bet')
@valid_identifier
def client_bet(data):
    bet_amount = float(data['bet_amount'])
    user_identifier = data['user_identifier']
    alternative = data['alternative']

    user = db.session.query(User).filter(User.user_identifier == user_identifier).one()

    if user.balance < bet_amount:
        errors.send_error('Insufficent funds', request.sid)

    elif bet_amount > float(config.max_bet):
        errors.send_error('Max bet is ' + config.max_bet, request.sid)

    elif bet_amount < float(config.min_bet):
        errors.send_error('Min bet is ' + config.min_bet, request.sid)

    else:
        json_resp = {
            'status': 'success',
            'balance': user.balance,
            'bet_amount': bet_amount,
            'alternative': alternative
        }

        socketio.emit('bet_response', json.dumps(json_resp), room=request.sid)

        bet.bet(user_identifier, bet_amount, alternative)   

        new_bet_data = {
            'name': steamid_to_name(user.steamid),
            'amount': bet_amount
        }

        if str(alternative) == str(1):
            new_bet_data['alternative'] = 'red'
        elif str(alternative) == str(2):
            new_bet_data['alternative'] = 'black'
        else:
            new_bet_data['alternative'] = 'green'
        

        socketio.emit('new_bet', json.dumps(new_bet_data), broadcast=True)
    