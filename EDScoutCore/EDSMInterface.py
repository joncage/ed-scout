import requests
import requests_cache
import os
import platform

# See https://www.edsm.net/en_GB/api-v1

# Setup the cache directory in the user area.
osname = platform.system()
if osname == 'Windows':
    cache_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'EDScout')
elif osname == 'Linux':
    cache_path = os.path.join(os.path.expanduser('~'), '.local', 'share', 'EDScout')
else:
    raise Exception(f"EDScout does not support {osname}")
os.makedirs(cache_path, exist_ok=True)
cache_name = 'edsm_cache'
requests_cache.install_cache(os.path.join(cache_path, cache_name))

# Configure the user agent so that it's clear which requests are coming from the scout.
headers = {
    'User-Agent': "EDScout"
}


class EDSMApiAccessException(Exception) :
    pass


def set_current_version(version):
    headers['User-Agent'] = f"EDScout {version}"


def make_request(url, request_data):
    attempts = 0
    data = None
    while data is None:
        attempts += 1
        try:
            data = requests.get(url, request_data, headers=headers)
            if data.status_code != 200:
                raise EDSMApiAccessException("Request returned bad response code %d" % data.status_code)
        except Exception:
            if attempts == 3:
                # We're out of chances so let this propagate.
                raise

    return data.json()


def get_system(system_name):
    request_data = {
        "systemName": system_name,
        "showID": 1,
        "showCoordinates": 1,
        "showPrimaryStar": 1
    }

    return make_request("https://www.edsm.net/api-v1/system", request_data)


def get_systems(system_name, radius):
    request_data = {
        "systemName": system_name,
        "radius": radius
    }

    return make_request("https://www.edsm.net/api-v1/sphere-systems", request_data)


def get_bodies(system_name):
    request_data = {
        "systemName": system_name
    }

    return make_request("https://www.edsm.net/api-system-v1/bodies", request_data)


def get_system_estimated_value(system_name):
    request_data = {
        "systemName": system_name
    }

    return make_request("https://www.edsm.net/api-system-v1/estimated-value", request_data)


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
