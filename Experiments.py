import json
import time
import logging
import requests

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
from watchdog.events import LoggingEventHandler

def report_route():
    with open('./ExampleData/NavRoute.json', 'r') as read_file:
        content = read_file.read()
        if len(content) is 0:
            return
        #print(content)
        nav_route = json.loads(content)
        print(nav_route)
        print('event: '+nav_route['event'])
        print('Route: ')
        for stop in nav_route['Route']:
            print(stop)
            # {'StarSystem': 'Wregoe JS-K d8-38', 'SystemAddress': 1316231366987, 'StarPos': [380.375, 215.84375, -299.46875], 'StarClass': 'F'}
            # {'StarSystem': 'Wregoe YI-L b36-2', 'SystemAddress': 5073565066553, 'StarPos': [350.125, 199.0625, -272.78125], 'StarClass': 'M'}
            # {'StarSystem': 'Wregoe BS-R c18-9', 'SystemAddress': 2558290727586, 'StarPos': [315.5, 180.5, -256.0], 'StarClass': 'K'}
            # {'StarSystem': 'Wregoe HL-H b38-2', 'SystemAddress': 5072759629129, 'StarPos': [282.90625, 156.15625, -239.3125], 'StarClass': 'M'}
            # {'StarSystem': 'Wregoe OH-F b39-3', 'SystemAddress': 7271514318161, 'StarPos': [263.125, 130.84375, -210.875], 'StarClass': 'M'}
            # {'StarSystem': 'Wregoe XO-B b41-3', 'SystemAddress': 7271245817185, 'StarPos': [244.9375, 113.0, -176.75], 'StarClass': 'M'}
            # {'StarSystem': 'Col 285 Sector KG-K b10-0', 'SystemAddress': 673907615089, 'StarPos': [219.40625, 98.21875, -143.6875], 'StarClass': 'M'}
            # {'StarSystem': 'Col 285 Sector RC-I b11-0', 'SystemAddress': 673639048569, 'StarPos': [201.90625, 72.78125, -111.75], 'StarClass': 'M'}
            # {'StarSystem': 'Col 285 Sector VD-G b12-3', 'SystemAddress': 7270171878785, 'StarPos': [174.96875, 43.90625, -92.0625], 'StarClass': 'M'}
            # {'StarSystem': 'Col 285 Sector EL-C b14-3', 'SystemAddress': 7269903377809, 'StarPos': [153.53125, 19.75, -61.875], 'StarClass': 'M'}
            # {'StarSystem': 'Deciat', 'SystemAddress': 6681123623626, 'StarPos': [122.625, -0.8125, -47.28125], 'StarClass': 'K'}

class FileChangedHandler(PatternMatchingEventHandler):

    def on_modified(self, event):
        #print('Modified: '+str(event))
        report_route()


def watch_for_changes():
    path = '.\\ExampleData'
    event_handler = FileChangedHandler(patterns=['*NavRoute.json'],
        ignore_patterns=[],
        ignore_directories=True)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    #path = sys.argv[1] if len(sys.argv) > 1 else '.'
    #event_handler = LoggingEventHandler()


    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    print('running')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('done')
        observer.stop()
    observer.join()


def getSystemEstimatedValue(systemName):
    requestData = {
        "systemName": systemName
    }

    data = requests.get("https://www.edsm.net/api-system-v1/estimated-value", requestData)

    if data.status_code == 200:
        return data.json()

    else:
        raise ("request returned bad response code %d" % (data.status_code))


def getSystems(systemName, radius):
    requestData = {
        "systemName": systemName,
        "radius": radius
    }

    data = requests.get("https://www.edsm.net/api-v1/sphere-systems", requestData)

    if data.status_code == 200:
        return data.json()

    else:
        raise ("request returned bad response code %d" % (data.status_code))

def searchSystems(systemName, radius):
    for item in getSystems(systemName, radius):
        data = getSystemEstimatedValue(item['name'])
        print(data)

        #for key in data.keys():
        #    print(key + ":" + str(data[key]))

        #print

def lookup_system():
    # {'StarSystem': 'Wregoe JS-K d8-38', 'SystemAddress': 1316231366987, 'StarPos': [380.375, 215.84375, -299.46875], 'StarClass': 'F'}
    system_name = 'Wregoe JS-K d8-38'
    system_value = getSystemEstimatedValue(system_name)
    print(system_value)
    print('nearby :')
    searchSystems(system_name, 40)




if __name__ == '__main__':
    #report_route()
    #watch_for_changes()
    lookup_system()