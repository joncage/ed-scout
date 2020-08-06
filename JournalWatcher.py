import json
import time
import os

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class JournalWatcher:

    def _extract_nav_route_from_file(journal_file: str):

        # Check the file size
        fsize = os.stat(journal_file).st_size

        with open(journal_file, 'r') as read_file:
            content = read_file.read()
            if len(content) is 0:
                return {}

            nav_route = json.loads(content)

            return nav_route['Route']

    class _EntriesChangeHandler(PatternMatchingEventHandler):

        def __init__(self):
            super(JournalWatcher._EntriesChangeHandler, self).__init__(
                patterns=['journal*.log'],
                ignore_patterns=[],
                ignore_directories=True)

            self.on_new_route = None

        def set_callback(self, on_new_route):
            self.on_new_route = on_new_route

        def on_modified(self, event):
            nav_route_file = str(event.src_path)
            new_route = NavRouteWatcher._extract_nav_route_from_file(nav_route_file)
            if new_route:
                self.on_new_route(new_route)


    def __init__(self):
        home = str(Path.home())
        path = home+"\\Saved Games\\Frontier Developments\\Elite Dangerous"
        self.event_handler = NavRouteWatcher._NewRouteHandler()

        self.observer = Observer()
        self.observer.schedule(self.event_handler, path, recursive=False)
        self.observer.start()

    def set_callback(self, on_new_route):
        self.event_handler.set_callback(on_new_route)

    def stop(self):
        self.observer.stop()
        self.observer.join()


if __name__ == '__main__':

    def ReportRoute(new_route):
        print('New route detected:'+str(new_route))

    navWatcher = NavRouteWatcher()
    navWatcher.set_callback(ReportRoute)

    print('running')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('done')

    navWatcher.stop()
