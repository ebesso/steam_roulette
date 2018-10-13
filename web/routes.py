from . import web
from init_app import oid, db

from flask import render_template, redirect, request

from flask_login import logout_user, login_required, current_user

from handlers import configuration, errors

from models import Sent_trade_offer, Trade_offer_types, User

from steam.steam_actions import get_user_steam_inventory 
from vgo import vgo_actions

import requests

@web.route('/')
def index():

    balance = ''

    if current_user.is_authenticated:
        balance = db.session.query(User).filter(User.steamid == current_user.id).one().balance

    return render_template('home.html', template_data=configuration.get('website'), balance=balance)

@web.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/')

@web.route('/login', methods=['GET'])
@oid.loginhandler
def open_id_login():
    return oid.try_login('http://steamcommunity.com/openid')

@web.route('/deposit', methods=['GET', 'POST'])
@web.route('/withdraw', methods=['GET', 'POST'])
@login_required 
def deposit():
    rule = request.url_rule

    if request.method == 'GET':
        
        if configuration.get('trade_offers').steam_skins == '1':
            if 'deposit' in rule.rule:
                inventory = get_user_steam_inventory(current_user.id)
            else:
                inventory = get_user_steam_inventory(configuration.get('keys').steam_id)
        else:
            if 'deposit' in rule.rule:
                print('Getting user inventory')

                action = 'deposit'
                inventory = vgo_actions.get_vgo_inventory(current_user.id)
            else:
                print('Getting bot inventory')

                action = 'withdraw'
                inventory = vgo_actions.get_vgo_inventory(configuration.get('keys').steam_id)
        
        if inventory == []:
            return errors.route_error('Failed to get your inventory\nBecause you have no items or you have no trade.opskins account')

        return render_template('trade_offer.html', inventory_data=inventory, template_data=configuration.get('website'), action=action, balance=db.session.query(User).filter(User.steamid == current_user.id).one().balance)
    
    else:

        if configuration.get('trade_offers').vgo_skins == '1':

            if 'deposit' in rule.rule:
                print('User Depositing')

                inventory = vgo_actions.get_vgo_inventory(current_user.id)
                trade_offer_type = Trade_offer_types.deposit
            else:
                print('User Withdrawing')
                
                inventory = vgo_actions.get_vgo_inventory(configuration.get('keys').steam_id)
                trade_offer_type = Trade_offer_types.withdraw

            items = []

            for item in inventory:
                if str(item.assetid) in request.form:
                    items.append(item.assetid)

            offer_response = vgo_actions.send_trade_offer(current_user.id, items, trade_offer_type)

            if offer_response == Sent_trade_offer.success:
                return redirect('/')
            else:
                return offer_response

        
