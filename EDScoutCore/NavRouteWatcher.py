import json
import time
import os

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class NavRouteWatcher:

    def __init__(self):
        home = str(Path.home())
        self.path = home+"\\Saved Games\\Frontier Developments\\Elite Dangerous"
        self.event_handler = NavRouteWatcher._NewRouteHandler()

        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=False)
        self.observer.start()

    def initiate_manually_triggered_event(self):
        nav_route_file = os.path.join(self.path, "NavRoute.json")
        self.event_handler.process_nav_file(nav_route_file)

    class _NewRouteHandler(PatternMatchingEventHandler):

        def __init__(self):
            super(NavRouteWatcher._NewRouteHandler, self).__init__(
                patterns=['*NavRoute.json'],
                ignore_patterns=[],
                ignore_directories=True)

            self.on_new_route = None

        def set_callback(self, on_new_route):
            self.on_new_route = on_new_route

        def on_modified(self, event):
            self.process_nav_file(str(event.src_path))

        def process_nav_file(self, nav_file):
            nav_route_file = nav_file
            new_route = NavRouteWatcher._extract_nav_route_from_file(nav_route_file)
            if new_route:
                self.on_new_route(new_route)

    @staticmethod
    def _extract_nav_route_from_file(nav_route_file: str):
        with open(nav_route_file, 'r') as read_file:
            content = read_file.read()
            if len(content) is 0:
                return {}

            nav_route = json.loads(content)

            return nav_route['Route']

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
    navWatcher.initiate_manually_triggered_event() # Populate the current route on startup

    print('running')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('done')

    navWatcher.stop()
