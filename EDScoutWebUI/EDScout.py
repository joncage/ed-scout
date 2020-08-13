import json
import os
import sys
import logging
import argparse

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flaskwebgui import FlaskUI

from EDScoutCore.NavRouteForwarder import Receiver
from EDScoutCore.EDScout import EDScout

__version__ = "1.1.0"


parser = argparse.ArgumentParser(description='Elite Dangerous Scout.')
parser.add_argument('-port', action="store", dest="port", type=int, default=5000)
parser.add_argument('-host', action="store", dest="host", type=str, default="127.0.0.1")

args = parser.parse_args()

# Check if this has been packaged up for distribution
is_deployed = hasattr(sys, '_MEIPASS')

# Work out where to stick the logs and make sure it exists
logging_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'EDScout')
if not os.path.isdir(logging_dir):
    os.mkdir(logging_dir)
logging_path = os.path.join(logging_dir, 'EDScout.log')

# Configure logging
log = logging.getLogger("EDScoutLogger")
log.setLevel(logging.DEBUG)

# Logging to file
fh = logging.FileHandler(logging_path)
if is_deployed:
    log_level = logging.INFO
else:
    log_level = logging.DEBUG
fh.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
log.addHandler(fh)

# More detailed logging to console if not deployed
if not is_deployed:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

# Lets go!
log.info("ED Scout Started")

# Fudge where the templates are located so they're still found after packaging
# See https://stackoverflow.com/questions/32149892/flask-application-built-using-pyinstaller-not-rendering-index-html
base_dir = '.'
if is_deployed:
    base_dir = os.path.join(sys._MEIPASS)

# Setup the app
app = Flask(__name__,
        static_folder=os.path.join(base_dir, 'static'),
        template_folder=os.path.join(base_dir, 'templates'))
app.config['SECRET_KEY'] = 'justasecretkeythatishouldputhere'

# Configure socketIO and the WebUI we use to encapsulate the window
socketio = SocketIO(app)
ui = FlaskUI(app, socketio=socketio, host=args.host, port=args.port)

# Make the global thread used to forward data.
thread = None
zmq_port_test = None


def receive_and_forward():
    """
    Waits for messages sent over the ZMQ link and emits each one via the socketIO link.
    Runs until the thread it runs on is killed.
    """

    log.info("Background thread launched and awaiting data..")
    global zmq_port_test
    r = Receiver(port=zmq_port_test)

    while True:
        message = r.receive().decode('ascii')
        try:
            log.debug("Received:   '" + message + "'")
            content = dict(data=json.loads(message))
            log.debug("Forwarding: '" + str(content) + "'")
            socketio.emit('log', content, broadcast=True)
        except Exception as pass_on_failure:
            log.exception(pass_on_failure)


@app.route('/')
def index():
    return render_template('index.html', version=__version__)


@socketio.on('connect')
def on_connect():
    log.debug("Client connected.")

    global thread
    if thread is None:
        thread = socketio.start_background_task(target=receive_and_forward)


if __name__ == '__main__':
    try:
        scout = EDScout()
        zmq_port_test = scout.port
        ui.run()
        socketio.run(app)
    except Exception as e:
        log.exception(e)
        raise

