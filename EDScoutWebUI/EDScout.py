import json
import os
import sys
import logging
import argparse
import tempfile
import psutil
from datetime import datetime

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from flaskwebgui import FlaskUI
from werkzeug.utils import secure_filename

from EDScoutCore.ZmqWrappers import Receiver
from EDScoutCore.EDScout import EDScout
from EDScoutWebUI import HudColourAdjuster

__version__ = "1.2.1"

parser = argparse.ArgumentParser(description='Elite Dangerous Scout.')
parser.add_argument('-port', action="store", dest="port", type=int, default=5000)
parser.add_argument('-host', action="store", dest="host", type=str, default="127.0.0.1")
parser.add_argument('-noapp', action="store_false", dest="run_as_app")
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
log.info("ED Scout Starting")

# Kill off any previous scouts; There can be only one (due to interactions with flaskwebgui)!
PROCNAME = "EDScout.exe"
log.debug(f"Current process: {os.getpid()}")
current_pid = os.getpid()
matching_processes = []
for proc in psutil.process_iter():
    # check whether the process name matches
    try:
        if (proc.name() == PROCNAME) and (proc.pid != current_pid):
            log.info(f"Found existing Scout instance PID:{proc.pid}, killing off before continuing")
            proc.kill()
    except psutil.AccessDenied:
        pass

# Fudge where the templates are located so they're still found after packaging
# See https://stackoverflow.com/questions/32149892/flask-application-built-using-pyinstaller-not-rendering-index-html
base_dir = '.'
if is_deployed:
    base_dir = os.path.join(sys._MEIPASS)



# Setup the app
static_path = os.path.join(base_dir, 'static')
app = Flask(__name__,
            static_folder=static_path,
            template_folder=os.path.join(base_dir, 'templates'))
app.config['SECRET_KEY'] = 'justasecretkeythatishouldputhere'

# Configure socketIO and the WebUI we use to encapsulate the window
socketio = SocketIO(app)
if args.run_as_app:
    ui = FlaskUI(app, socketio=socketio, host=args.host, port=args.port)

# Make the global thread used to forward data.
thread = None
zmq_port_test = None

temp_dir = tempfile.TemporaryDirectory()

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
    return render_template('index.html', version=__version__, timestamp=str(datetime.utcnow()))

@app.route('/css-overrides/<path:filename>')
def css_override_route(filename):
    safe_filename = secure_filename(filename)
    log.debug(f"Looking for: {safe_filename} in {temp_dir.name}")
    return send_from_directory(temp_dir.name, safe_filename, conditional=True)

@socketio.on('connect')
def on_connect():
    log.debug("Client connected.")

    global thread
    if thread is None:
        thread = socketio.start_background_task(target=receive_and_forward)


if __name__ == '__main__':
    try:

        # Try to load the users gfx changes if they exist
        if os.path.exists(HudColourAdjuster.default_config_file):
            log.info(f"Looking for HUD overrides in {HudColourAdjuster.default_config_file}")

            original_css_path = os.path.join(static_path, "style.css")
            colour_matrix = HudColourAdjuster.get_matrix_values(HudColourAdjuster.default_config_file)
            if colour_matrix:
                remapped_css_file = "css-overrides.css"
                remapped_css_file_path = os.path.join(temp_dir.name,remapped_css_file)

                HudColourAdjuster.remap_style_file(original_css_path, colour_matrix, remapped_css_file_path)
            else:
                log.info(f"No HUD overrides detected in ({HudColourAdjuster.default_config_file})")
        else:
            log.info(f"No HUD overrides file detected ({HudColourAdjuster.default_config_file})")

        # Launch the background interfaces
        scout = EDScout()
        zmq_port_test = scout.port

        # Launch the web server either directly or as an app
        if args.run_as_app:
            ui.run()
        else:
            socketio.run(app)
    except Exception as e:
        log.exception(e)
        raise
