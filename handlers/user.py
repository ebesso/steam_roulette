from init_app import db

from models import User

import string, random

def update_user_identifier(steamid):
    current_user = db.session.query(User).filter(User.steamid == steamid).one()

    current_user.user_identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

    db.session.commit()

def validate_user_identifer(identifier):
    if db.session.query(User).filter(User.user_identifier == identifier).count():
        return True
    else:
        return False