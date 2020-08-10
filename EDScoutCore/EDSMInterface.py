import requests


def get_systems(system_name, radius):
    requestData = {
        "systemName": system_name,
        "radius": radius
    }

    data = requests.get("https://www.edsm.net/api-v1/sphere-systems", requestData)

    if data.status_code != 200:
        raise ("request returned bad response code %d" % (data.status_code))
    return data.json()


def get_system_estimated_value(system_name):
    requestData = {
        "systemName": system_name
    }

    data = requests.get("https://www.edsm.net/api-system-v1/estimated-value", requestData)

    if data.status_code != 200:
        raise ("request returned bad response code %d" % (data.status_code))

    return data.json()


def search_systems(system_name, radius):
    for item in get_systems(system_name, radius):
        data = get_system_estimated_value(item['name'])

        print(data)
        # for key in data.keys():
        #     print(key + ":" + str(data[key]))


def lookup_system():
    # {'StarSystem': 'Wregoe JS-K d8-38', 'SystemAddress': 1316231366987, 'StarPos': [380.375, 215.84375, -299.46875], 'StarClass': 'F'}
    system_name = 'Wregoe JS-K d8-38'
    system_value = get_system_estimated_value(system_name)
    print(system_value)
    print('nearby :')
    search_systems(system_name, 40)
