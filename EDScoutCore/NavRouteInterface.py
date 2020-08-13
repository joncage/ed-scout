import json


def extract_nav_route_from_file(nav_route_file: str):
    with open(nav_route_file, 'r') as read_file:
        content = read_file.read()
        if len(content) == 0:
            return {}

        nav_route = json.loads(content)

        return nav_route['Route']
