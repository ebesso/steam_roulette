from flask import Flask

from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from flask_login import LoginManager

import os

socketio = SocketIO()
db = SQLAlchemy()
oid = OpenID()
login_manager = LoginManager()

def create_app(debug_mode):
    
    app = Flask(__name__)

    app.secret_key = '123abc'
    app.debug = debug_mode
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

    from web import web as web_bp

    app.register_blueprint(web_bp)

    socketio.init_app(app)
    db.init_app(app)
    oid.init_app(app)
    login_manager.init_app(app)

    return app
