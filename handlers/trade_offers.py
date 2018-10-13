from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from models import Trade_offer, Trade_offer_types, User

from handlers import configuration

from vgo import vgo_actions

from utilities import get_vgo_trade_offer_value

import requests, os

key_config = configuration.get('keys')

Session = scoped_session(sessionmaker(create_engine(os.environ['DATABASE_URL'])))

def check_trade_offers():
    db = Session()

    for deposit in db.query(Trade_offer).all():

        if deposit.vgo_offer == True:
            state = int(requests.get('https://api-trade.opskins.com/ITrade/GetOffer/v1/?key={0}&offer_id={1}'.format(key_config.vgo_key, deposit.offer_id)).json()['response']['offer']['state'])

            if state == 7 or state == 8 or state == 6 or state == 5 :

                if deposit.trade_type == Trade_offer_types.withdraw:
                    vgo_actions.trade_offer_declined(deposit.offer_id, db)

                db.query(Trade_offer).filter(Trade_offer.offer_id == deposit.offer_id).delete()
                db.commit()
            
            elif state == 3:
                vgo_actions.trade_offer_accepted(deposit.offer_id, deposit.trade_type, db)