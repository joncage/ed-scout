from threading import Timer
import logging
import os

logger = logging.getLogger('EDScoutCore')


class FileSystemUpdatePrompter:

    def __init__(self, path_to_query):
        self.path_to_query = path_to_query
        self.t = Timer(0.1, self.hello)
        self.file_size = None

        self.hello()

    def hello(self):
        new_size = os.stat(self.path_to_query).st_size

        if self.file_size is None:
            logger.debug(f"File size check: {new_size}")
        elif new_size != self.file_size:
            logger.debug(f"File size check: {new_size} (+{new_size-self.file_size})")

        self.file_size = new_size
        self.t = Timer(0.1, self.hello)
        self.t.start()

