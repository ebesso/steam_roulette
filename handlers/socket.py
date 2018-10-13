from main import socketio

@socketio.on('message')
def client_message(message):
    print(message)