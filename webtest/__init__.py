from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
import os

socketio = SocketIO()

def createApp(debug=False):
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = os.urandom(24)

    from .main import main as m
    app.register_blueprint(m)
    socketio.init_app(app)
    return app

