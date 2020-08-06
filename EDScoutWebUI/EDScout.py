import json
import os
import sys

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flaskwebgui import FlaskUI #get the FlaskUI class

from NavRouteForwarder import Receiver
from EDScout import EDScout

# Fudge where the templates are located so they're still found after packaging
# See https://stackoverflow.com/questions/32149892/flask-application-built-using-pyinstaller-not-rendering-index-html
base_dir = '.'
if hasattr(sys, '_MEIPASS'):
    base_dir = os.path.join(sys._MEIPASS)

# Setup the app
app = Flask(__name__,
        static_folder=os.path.join(base_dir, 'static'),
        template_folder=os.path.join(base_dir, 'templates'))
app.config['SECRET_KEY'] = 'justasecretkeythatishouldputhere'

# Configure socketIO and the WebUI we use to encapsulate the window
socketio = SocketIO(app)
ui = FlaskUI(app, socketio=socketio)

# Make the global thread used to forward data.
thread = None


def receive_and_forward():
    welcome_message = "Waiting for nav data.."
    print(welcome_message)
    #socketio.emit('log', dict(data=welcome_message), broadcast=True)
    r = Receiver()

    while True:
        message = r.receive().decode('ascii')
        print("Forwarding '"+message+"'")
        content = dict(data=json.loads(message))
        print("Forwarding " + str(content))
        socketio.emit('log', content, broadcast=True)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def on_connect():
    print("Client connected.")
    #emit('log', dict(data='Connected'), broadcast=True)

    global thread
    if thread is None:
        thread = socketio.start_background_task(target=receive_and_forward)


if __name__ == '__main__':
    scout = EDScout()
    ui.run()
