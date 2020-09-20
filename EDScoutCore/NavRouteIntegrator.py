import logging
import json
import os
from pathlib import Path
from .SavedGamesLocator import get_saved_games_path

logger = logging.getLogger('EDScoutCore')


class NavRouteIntegrator:

    def __init__(self, nav_route_file=None):
        self.last_nav_route = None

        if not nav_route_file:
            home = str(Path.home())
            self.nav_route_file = os.path.join(get_saved_games_path(), "NavRoute.json")
        else:
            self.nav_route_file = nav_route_file

    def process_new_journal_entries(self, entries):
        adjusted_new_entries = []
        for entry in entries:
            if entry["event"] == "NavRoute":
                nav_route = self._read_and_process_new_nav_route()
                if nav_route:
                    adjusted_new_entries.append(nav_route)
                else:
                    logger.debug("Skipping nav event; Route is not new")

            else:
                adjusted_new_entries.append(entry)
        return adjusted_new_entries

    def _is_new_nav_route(self, route):
        if len(route) == 0:
            self.last_nav_route = None
            return True  # Empty route so no harm in sending that up in case it got cleared.

        first_system = route[0]['SystemAddress']
        last_system = route[-1]['SystemAddress']
        is_new_route = (self.last_nav_route is None) or \
                       (self.last_nav_route[0] != first_system) or \
                       (self.last_nav_route[1] != last_system)
        self.last_nav_route = (first_system, last_system)
        return is_new_route

    def _read_and_process_new_nav_route(self):

        nav_route_event = self._extract_nav_route_from_file()
        nav_route = nav_route_event["Route"]
        if not self._is_new_nav_route(nav_route):
            nav_route_event = None
        return nav_route_event

    def _extract_nav_route_from_file(self):
        with open(self.nav_route_file, 'r') as read_file:
            content = read_file.read()
            if len(content) == 0:
                return {}

            nav_route = json.loads(content)

            return nav_route
