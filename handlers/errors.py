from init_app import socketio

from flask import render_template

import json

def send_error(message, sid):
    socketio.emit('error', message, room=sid)

def route_error(message):
    return render_template('error.html', error=message)
