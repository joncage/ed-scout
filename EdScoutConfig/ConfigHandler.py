import configparser
import os
import logging
from pathlib import Path


class Config:

    DefaultPath = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'EDScout')

    def __init__(self, config_dir=DefaultPath):
        self.config = configparser.ConfigParser()

        self.config_dir = config_dir
        if not os.path.isdir(self.config_dir):
            Path(self.config_dir).mkdir(parents=True, exist_ok=True)

        self.set_defaults()

        self.config_path = os.path.join(self.config_dir, 'EdScout.ini')
        if os.path.isfile(self.config_path):
            self.config.read(self.config_path)
        # Always write the file so that any new config options get added to it.
        with open(self.config_path, "w") as f:
            self.config.write(f) #

    def set_defaults(self):
        self.config['General'] = {
            'port': '5000',
            'host': '127.0.0.1',
            'no_app': 'False',
            'log_level': str(logging.INFO),
            'force_polling': 'False',
            'show_nav_route': 'True'
        }

    def get_option(self, option_name):
        return self.config['General'][option_name]
