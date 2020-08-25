import requests
import requests_cache
import os

# See https://www.edsm.net/en_GB/api-v1

# Setup the cache directory in the user area.
cache_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'EDScout')
os.makedirs(cache_path, exist_ok=True)
cache_name = 'edsm_cache'
requests_cache.install_cache(os.path.join(cache_path, cache_name))

# Configure the user agent so that it's clear which requests are coming from the scout.
headers = {
    'User-Agent': "EDScout"
}


def set_current_version(version):
    headers['User-Agent'] = f"EDScout {version}"


def get_system(system_name):
    requestData = {
        "systemName": system_name,
        "showID": 1,
        "showCoordinates": 1,
        "showPrimaryStar": 1
    }

    data = requests.get("https://www.edsm.net/api-v1/system", requestData, headers=headers)

    if data.status_code != 200:
        raise ("request returned bad response code %d" % (data.status_code))
    return data.json()


def get_systems(system_name, radius):
    requestData = {
        "systemName": system_name,
        "radius": radius
    }

    data = requests.get("https://www.edsm.net/api-v1/sphere-systems", requestData, headers=headers)

    if data.status_code != 200:
        raise ("request returned bad response code %d" % (data.status_code))
    return data.json()


def get_bodies(system_name):
    requestData = {
        "systemName": system_name
    }

    data = requests.get("https://www.edsm.net/api-system-v1/bodies", requestData, headers=headers)

    if data.status_code != 200:
        raise ("request returned bad response code %d" % (data.status_code))

    return data.json()


def get_system_estimated_value(system_name):
    requestData = {
        "systemName": system_name
    }

    data = requests.get("https://www.edsm.net/api-system-v1/estimated-value", requestData, headers=headers)

    if data.status_code != 200:
        raise ("request returned bad response code %d" % (data.status_code))

    return data.json()


def search_systems(system_name, radius):
    for item in get_systems(system_name, radius):
        data = get_system_estimated_value(item['name'])

        print(data)


def lookup_system(system_name):
    # {'StarSystem': 'Wregoe JS-K d8-38', 'SystemAddress': 1316231366987, 'StarPos': [380.375, 215.84375, -299.46875], 'StarClass': 'F'}
    system_value = get_system_estimated_value(system_name)
    print(system_value)
    print('nearby :')
    search_systems(system_name, 40)
