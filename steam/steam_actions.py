from handlers import configuration

import utilities

import requests

def get_user_steam_inventory(user_id):
    inventory_url = 'http://steamcommunity.com/inventory/{0}/{1}/2?l=english&count=500'

    inventory_data = requests.get(inventory_url.format(user_id, configuration.get('website').appid)).json()
    inventory_assets = utilities.parse_steam_inventory(inventory_data)

    return inventory_assets





    
    
