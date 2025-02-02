import json
import os
import sys
import logging
import argparse
import tempfile
import platform
import psutil
import time
import threading
import requests
import re

from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from flaskwebgui import FlaskUI
from werkzeug.utils import secure_filename

from EDScoutCore.ZmqWrappers import Receiver
from EDScoutCore.EDScout import EDScout
from EDScoutCore import EDSMInterface
from EDScoutWebUI import HudColourAdjuster
from EDScoutWebUI import WindowToggler
from EdScoutConfig import ConfigHandler
from EDScoutWebUI.VersionChecker import check_version


try:
    from EDScoutWebUI import version
    __version__ = version.version
    __release__ = version.release
except ImportError:
    __version__ = "Beta"
    __release__ = "Beta"


# Indicate to EDSM which version of the scout is making requests.
EDSMInterface.set_current_version(__version__)

# Load settings from the config file
config = ConfigHandler.Config()

# Make any overrides from commandline params the user may have specified.
parser = argparse.ArgumentParser(description='Elite Dangerous Scout.')
parser.add_argument('-port', action="store", dest="port", type=int, default=int(config.get_option('port')))
parser.add_argument('-host', action="store", dest="host", type=str, default=config.get_option('host'))
parser.add_argument('-log_level', action="store", dest="log_level", type=int, default=config.get_option('log_level'))
parser.add_argument('-no_app', action="store_false", dest="run_as_app")
parser.add_argument('-force_polling', action="store_true", dest="force_polling")
parser.add_argument('-disable_nav_route', action="store_true", dest="disable_nav_route")
args = parser.parse_args()

# This looks a bit backwards but these options are designed to disable settings.
# So if they're true, we should check the default from the config.
if args.run_as_app is True:
    args.run_as_app = (config.get_option('no_app').lower() == 'false')
if args.force_polling is False:
    args.force_polling = (config.get_option('force_polling').lower() == 'true')
if args.disable_nav_route is False:
    args.disable_nav_route = (config.get_option('disable_nav_route').lower() == 'true')

# Check if this has been packaged up for distribution
is_deployed = hasattr(sys, '_MEIPASS')


def configure_logger(logger_to_configure, log_path, log_level_override=None):

    if log_level_override is not None:
        log_level = log_level_override
    elif args.log_level != logging.INFO:
        log_level = args.log_level
    elif is_deployed:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    logger_to_configure.setLevel(log_level)

    # Logging to file
    fh = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03dZ - %(name)s-%(module)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%dT%H:%M:%S')
    logging.Formatter.converter = time.gmtime
    fh.setFormatter(formatter)
    logger_to_configure.addHandler(fh)

    # More detailed logging to console if not deployed
    if not is_deployed:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger_to_configure.addHandler(ch)


def version_check(current_version):
    version_check_response = check_version()
    if version_check_response:
        socketio.emit('version', version_check_response)


# Work out where to stick the logs and make sure it exists
osname = platform.system()
if osname == 'Windows':
    logging_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'EDScout', 'Logs')
elif osname == 'Linux':
    logging_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'EDScout', 'logs')
else:
    raise Exception(f"EDScout does not support {osname}")
if not os.path.isdir(logging_dir):
    Path(logging_dir).mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
logging_path = os.path.join(logging_dir, f"EDScout-{timestamp}.log")

# Configure logging
log = logging.getLogger('EDScoutWebUI')
configure_logger(log, logging_path)
configure_logger(logging.getLogger('EDScoutCore'), logging_path)
configure_logger(logging.getLogger('NavRouteWatcher'), logging_path)
configure_logger(logging.getLogger('JournalInterface'), logging_path)
configure_logger(logging.getLogger('VersionChecker'), logging_path)
configure_logger(logging.getLogger('flaskwebgui'), logging_path, log_level_override=logging.INFO)

# Lets go!
log.info(f"ED Scout {__release__} Starting")

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
else:
    base_dir = os.path.dirname(__file__)

# Setup the app
static_path = os.path.join(base_dir, 'static')
app = Flask(__name__,
            static_folder=static_path,
            template_folder=os.path.join(base_dir, 'templates'))
app.config['SECRET_KEY'] = 'justasecretkeythatishouldputhere'
if not is_deployed:
    log.info("Disabling caching")
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Stop caching to changes to content files happens right away during debug
    # app.debug = True

# Configure socketIO and the WebUI we use to encapsulate the window
socketio = SocketIO(app)
if args.run_as_app:
    ui = FlaskUI(app=app, socketio=socketio, port=args.port, server="flask_socketio")
else:
    ui = None

# Make the global thread used to forward data.
thread = None
zmq_port_test = None

temp_dir = tempfile.TemporaryDirectory()


def receive_and_forward(scout):
    """
    Waits for messages sent over the ZMQ link and emits each one via the socketIO link.
    Runs until the thread it runs on is killed.
    """

    log.info("Background thread launched and awaiting data..")
    r = Receiver(port=scout.port)
    scout.trigger_current_journal_check()

    while True:
        message = r.receive().decode('ascii')
        try:
            log.debug("Received:   '" + message + "'")
            content = dict(data=json.loads(message))
            log.debug("Forwarding: '" + str(content) + "'")
            socketio.emit('log', content)
        except Exception as pass_on_failure:
            log.exception(pass_on_failure)


@app.route('/')
def index():
    return render_template('index.html',
                           version=__version__,
                           timestamp=str(datetime.now(datetime.UTC)),
                           disable_nav_route=args.disable_nav_route)


@app.route('/css-overrides/<path:filename>')
def css_override_route(filename):
    safe_filename = secure_filename(filename)
    log.debug(f"Looking for: {safe_filename} in {temp_dir.name}")
    return send_from_directory(temp_dir.name, safe_filename, conditional=True)


@socketio.on('connect')
def on_connect():
    log.debug("Client connected.")

    # Launch the version check. Note that we only do this after the client has connected to avoid them missing this.
    version_thread = socketio.start_background_task(version_check, __version__)

    global thread
    if thread is None:
        global scout
        thread = socketio.start_background_task(receive_and_forward, scout)


def remap_css_to_match_hud():
    # Try to load the users gfx changes if they exist
    if os.path.exists(HudColourAdjuster.default_config_file):
        log.info(f"Looking for HUD overrides in {HudColourAdjuster.default_config_file}")

        original_css_path = os.path.join(static_path, "style.css")
        try:
            colour_matrix = HudColourAdjuster.get_matrix_values(HudColourAdjuster.default_config_file)
        except Exception as e:
            log.error("Failed to interpret HUD overrides; Please check your file is of the format described in https://arkku.com/elite/hud_editor/")
            log.exception(e)
            colour_matrix = None
        else:
            if colour_matrix:
                remapped_css_file = "css-overrides.css"
                remapped_css_file_path = os.path.join(temp_dir.name, remapped_css_file)

                HudColourAdjuster.remap_style_file(original_css_path, colour_matrix, remapped_css_file_path)
                log.info("Successfully remapped styles to match Elite HUD")
            else:
                log.info(f"No HUD overrides detected in ({HudColourAdjuster.default_config_file})")
    else:
        log.info(f"No HUD overrides file detected ({HudColourAdjuster.default_config_file})")


if __name__ == '__main__':
    try:
        # If the user has altered the colour settings for their hud, attempt to do the same in the scout by adjusting
        # any colours in the .css
        remap_css_to_match_hud()

        # Launch the background interfaces
        if args.force_polling:
            log.info("Polling enabled")

        record_output = not is_deployed
        scout = EDScout(force_polling=args.force_polling, record_output=record_output)

        # Enable toggling
        toggler = WindowToggler.ScoutToggler()
        # Enable transparency adjustment
        window_title = "ED Scout " + __version__
        trans = WindowToggler.TransparencySetter(window_title)

        # Launch the web server either directly or as an app
        if ui:
            ui.run()
        else:
            socketio.run(app)
    except Exception as e:
        log.exception(e)
        raise
