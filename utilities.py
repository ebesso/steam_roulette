from init_app import db, socketio

from models import Empty, Steam_item, User

from handlers import configuration
from handlers import user as user_handler

from functools import wraps

from flask import redirect, request

import json, requests, os

key_config = configuration.get('keys')
website_config = configuration.get('website')

summaries_url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={0}&steamids={1}'
market_url = 'http://steamcommunity.com/market/priceoverview/?appid={0}&currency=1&market_hash_name={1}'

def steamid_to_name(steamid):
    steam_data = requests.get(summaries_url.format(key_config.steam_api_key, steamid)).json()

    return steam_data['response']['players'][0]['personaname']

def parse_steam_inventory(inventory_data):

    asset_dict = {}
    inventory_assets = []
    full_assets = []

    for asset in inventory_data['assets']:
        asset_dict[asset['classid']] = asset['assetid']

    for description in inventory_data['descriptions']:
        if description['tradable'] == 1:
            inventory_asset = Empty()

            inventory_asset.name = description['market_hash_name']
            inventory_asset.icon_url = 'http://cdn.steamcommunity.com/economy/image/' + description['icon_url']
            inventory_asset.assetid = asset_dict[description['classid']]
            
            if db.session.query(Steam_item).filter(Steam_item.market_hash_name == inventory_asset.name).count():
                print('Using old data')

                inventory_asset.price = db.session.query(Steam_item).filter(Steam_item.market_hash_name == inventory_asset.name).one().price
                inventory_assets.append(inventory_asset)

            else:
                print('Using new data')

                price_data = requests.get(market_url.format(website_config.appid, inventory_asset.name)).json()

                if price_data['success'] == True:
                    price = price_data['lowest_price']

                    steam_item = Steam_item(inventory_asset.name, float(price.replace('$', '')))
                    db.session.add(steam_item)
                    db.session.commit()

                    inventory_asset.price = price.replace('$', '')

                    inventory_assets.append(inventory_asset)

    return inventory_assets

def update_item_prices():

    for item in db.session.query(Steam_item).all():
        price_data = requests.get(market_url.format(website_config.appid, item.market_hash_name)).json()

        if price_data['success'] == True:
            price = price_data['lowest_price']

            item.price = float(price.replace('$', ''))
            db.session.commit()

def parse_vgo_inventory(data):
    inventory = []

    if data['response']['user_data']['steam_id'] == key_config.steam_id:
        bot_inventory = True
    else:
        bot_inventory = False
    
    trade_offer_config = configuration.get('trade_offers')

    for item in data['response']['items']:
        parsed_item = Empty()

        parsed_item.name = item['name']
        parsed_item.assetid = item['id']
        parsed_item.icon_url = item['image']['300px']
        parsed_item.price = item['suggested_price_floor'] / 100

        if bot_inventory:
            parsed_item.price = parsed_item.price * float(trade_offer_config.bot_percentage)
        else:
            parsed_item.price = parsed_item.price * float(trade_offer_config.user_percentage)

        inventory.append(parsed_item)
    
    return inventory

        
def validate_user_balance(amount, steamid):
    user = db.session.query(User).filter(User.steamid == steamid).one()

    if user.balance >= float(amount):
        return True
    else:
        return False

def get_vgo_trade_offer_value(items, bot_inventory):
    items_string = ','.join(map(str, items))

    response = requests.get('https://api-trade.opskins.com/IItem/GetItemsById/v1/?key={0}&item_id={1}'.format(configuration.get('keys').vgo_key, items_string)).json()

    value = 0

    for item in response['response']['items']:
        item_price = item['suggested_price_floor']

        item_price = item_price / 100

        if bot_inventory:
            item_price = item_price * float(configuration.get('trade_offers').bot_percentage)
        else:
            item_price = item_price * float(configuration.get('trade_offers').user_percentage)

        value += item_price
    
    return value

def valid_identifier(func):
    @wraps(func)
    def validate(data):
        if 'user_identifier' not in data:
            socketio.emit('login_required', room=request.sid)
            return

        if db.session.query(User).filter(User.user_identifier == data['user_identifier']).count():
            return func(data)
        else:
            socketio.emit('login_required', room=request.sid)            
    
    return validate

