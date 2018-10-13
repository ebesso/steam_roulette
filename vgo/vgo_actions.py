from init_app import db

from handlers import configuration, errors
from utilities import parse_vgo_inventory, validate_user_balance, get_vgo_trade_offer_value

from models import Empty, Trade_offer, Trade_offer_types, Sent_trade_offer, User

from flask import render_template

import requests, pyotp

keys_config = configuration.get('keys')
trade_offer_config = configuration.get('trade_offers')

def get_vgo_inventory(steamid):
    inventory_url = 'https://api-trade.opskins.com/ITrade/GetUserInventoryFromSteamId/v1/?key={0}&steam_id={1}&app_id=1'

    response = requests.get(inventory_url.format(keys_config.vgo_key, steamid))

    print('Getting user inventory with ' + response.url)

    if response.status_code == 200:
        print('Successful request')
        return parse_vgo_inventory(response.json())
    else:
        print('Failed request ' + str(response.status_code) + ' for user ' + steamid)
        return []    

def send_trade_offer(steamid, items, offer_type):
    auth_code = pyotp.TOTP(keys_config.opskins_secret).now()

    print('Auth code. ' + str(auth_code))
    print('Items to trade ' + str(items))

    offer_data = {
        'key': keys_config.vgo_key,
        'twofactor_code': auth_code,
        'steam_id': steamid
    }

    if offer_type == Trade_offer_types.deposit:
        print('Offer type is deposit')

        offer_data['items_to_receive'] = ','.join(map(str, items))
    
    else:
        if validate_user_balance(get_vgo_trade_offer_value(items, True), steamid) == False:
            return errors.route_error('Insufficent funds')

        print('Offer type is withdraw')

        offer_data['items_to_send'] = ','.join(map(str, items))

    response = requests.post('https://api-trade.opskins.com/ITrade/SendOfferToSteamId/v1/', data=offer_data)

    if response.status_code == 200:

        if offer_type == Trade_offer_types.withdraw:

            print('Withdraw sent')

            user = db.session.query(User).filter(User.steamid == steamid).one()
            user.balance -= get_vgo_trade_offer_value(items, True)
            db.session.commit()

        offer = Trade_offer(
            offer_type,
            steamid,
            response.json()['response']['offer']['id'],
            True
        )

        db.session.add(offer)
        db.session.commit()

        print('Offer sent to client')

        return Sent_trade_offer.success

    else:
        return errors.route_error('Opskins request failed')
    
def trade_offer_declined(offer_id, db):

    response = requests.get('https://api-trade.opskins.com/ITrade/GetOffer/v1/?key={0}&offer_id={1}'.format(keys_config.vgo_key, offer_id)).json()

    items = []

    for item in response['response']['offer']['sender']['items']:
        items.append(item['id'])
    
    value = get_vgo_trade_offer_value(items, True)

    user = db.query(User).filter(User.steamid == response['response']['offer']['recipient']['steam_id']).one()
    user.balance += value

    db.commit()

def trade_offer_accepted(offer_id, offer_type, db):
    
    offer_response = requests.get('https://api-trade.opskins.com/ITrade/GetOffer/v1/?key={0}&offer_id={1}'.format(keys_config.vgo_key, offer_id)).json()

    offer_value = 0

    for item in offer_response['response']['offer']['recipient']['items']:
        offer_value += int(item['suggested_price_floor'])
    
    user = db.query(User).filter(User.steamid == offer_response['response']['offer']['recipient']['steam_id']).one()
    
    if offer_type == Trade_offer_types.deposit:
        print('Addded balance for deposit')
        user.balance += ((offer_value / 100) * float(trade_offer_config.user_percentage))

    db.commit()

    db.query(Trade_offer).filter(Trade_offer.offer_id == offer_id).delete()
    db.commit()

    print('Added funds to user')