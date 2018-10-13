from . import web

from flask_login import login_user
from flask import redirect, make_response

from handlers import user

from models import User, User_auth

from init_app import login_manager, db, oid

@web.errorhandler(401)
def page_not_found(e):
    return redirect('/login')

@login_manager.user_loader
def load_user(user_id):
    if user_id != 'None':
        real_user = db.session.query(User).filter(User.steamid == user_id).one()
        auth_user = User_auth(real_user.steamid)
        auth_user.user_identifier = real_user.user_identifier

        return auth_user

@oid.after_login
def login_handling(steam_response):
    steamid = steam_response.identity_url.split('/')[5]

    if db.session.query(User).filter(User.steamid == steamid).count():
        login_user(User_auth(steamid))

    else:
        new_user = User(steamid)

        db.session.add(new_user)
        db.session.commit()

        login_user(User_auth(steamid))

    user.update_user_identifier(steamid)

    response = make_response(redirect('/'))

    response.set_cookie('user_identifier', db.session.query(User).filter(User.steamid == steamid).one().user_identifier)

    return response
