from threading import Thread
import logging
import os
from time import sleep

logger = logging.getLogger('EDScoutCore')


class FileSystemUpdatePrompter:

    def __init__(self, path_to_query):
        self.path_to_query = path_to_query

        t = Thread(target=self.file_check)
        t.daemon = True
        t.start()

        self.file_size = None

    def file_check(self):
        while True:
            new_size = os.stat(self.path_to_query).st_size

            if self.file_size is None:
                logger.debug(f"File size check: {new_size}")
            elif new_size != self.file_size:
                logger.debug(f"File size check: {new_size} (+{new_size-self.file_size})")

            self.file_size = new_size

            sleep(0.1)

    def set_watch_file(self, path_to_query):
        self.path_to_query = path_to_query
