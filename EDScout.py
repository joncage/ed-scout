import time

from NavRouteWatcher import NavRouteWatcher


class EDScout:

    def __init__(self):
        self.navWatcher = NavRouteWatcher()


if __name__ == '__main__':
    navWatcher = NavRouteWatcher()

    print('running')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('done')

    navWatcher.stop()
