import requests
import requests_cache
import logging
import re

from EDScoutWebUI import version

current_version = version.version
log = logging.getLogger('VersionChecker')


def get_version_parts(version):
    regex = r"[vV]?(\d)+\.(\d)+\.(\d)+\.?(\d)?"
    match = re.search(regex, version)
    if match is not None:
        return [int(x) for x in match.groups(default="0")]
    else:
        return None


def check_version_diff(current_version, latest_version):
    current_parts = get_version_parts(current_version)
    latest_parts = get_version_parts(latest_version)
    new_version_detected = False
    for i in range(0, min(len(current_parts), len(latest_parts))):
        if current_parts[i] < latest_parts[i]:
            new_version_detected = True
            break
    return new_version_detected


def check_version():
    latest_release_url = 'https://github.com/joncage/ed-scout/releases/latest'
    try:
        # Even though we don't need caching here, the EDSMInterace uses it and patches things so we have to explicitly
        # disable the cache.
        with requests_cache.disabled():
            r = requests.get(latest_release_url)
    except Exception as pass_on_failure:
        log.exception(pass_on_failure)
        return None

    latest_version = r.url.split('/')[-1]

    new_version_available = check_version_diff(current_version, latest_version)
    content = {
        'current_version': current_version,
        'latest_version': latest_version,
        'new_release_detected': new_version_available,
        'url': latest_release_url
    }

    version_check_description = 'New version available: '+latest_version if new_version_available else 'Up to date'
    log.info(f"Version check: {version_check_description}")

    return content


if __name__ == '__main__':
    import time
    formatter = logging.Formatter('%(asctime)s.%(msecs)03dZ - %(name)s-%(module)s - %(levelname)s - %(message)s',
                                  datefmt='%Y-%m-%dT%H:%M:%S')
    logging.Formatter.converter = time.gmtime
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    log.addHandler(ch)
    log.setLevel(logging.DEBUG)

    version = check_version()
    log.info(version)
