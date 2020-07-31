import time
import json

from NavRouteWatcher import NavRouteWatcher
import EDSMInterface
from NavRouteForwarder import Sender

class EDScout:

    def __init__(self):
        self.navWatcher = NavRouteWatcher()
        self.navWatcher.set_callback(self.report_route)
        self.sender = Sender()

    def report_route(self, nav_route):
        print('New route: ')

        self.sender.send(json.dumps({'type':'NewRoute'}))

        for jump_dest in nav_route:
            #print(jump_dest)

            estimatedValue = EDSMInterface.get_system_estimated_value(jump_dest['StarSystem'])

            # IC 2602 Sector GC-T b4-8 (M) Charted: {'id': 10594826, 'id64': 18269314557401, 'name': 'IC 2602 Sector GC-T b4-8', 'url': 'https://www.edsm.net/en/system/bodies/id/10594826/name/IC+2602+Sector+GC-T+b4-8', 'estimatedValue': 2413, 'estimatedValueMapped': 2413, 'valuableBodies': []}

            unchartedCheck = not estimatedValue
            if unchartedCheck:
                chartedCheck = "Uncharted!"
            else:
                chartedCheck = "Charted   "

            value = None
            if estimatedValue:
                value = ": value: "+str(estimatedValue['estimatedValueMapped'])
            else:
                value = ""

            message = 'RouteItem: (%s) %s %s%s'%(jump_dest['StarClass'], chartedCheck, jump_dest['StarSystem'], value)
            print(message)

            report_content = {'type': 'System'}
            report_content.update(jump_dest)
            report_content.update(estimatedValue)
            report_content['charted'] = not unchartedCheck

            #print("type="+str(type(json_report)))

            self.sender.send(json.dumps(report_content))

            if not unchartedCheck:
                for body in estimatedValue['valuableBodies']:
                    print("\t\t"+str(body))

            # RouteItem: (F) Charted    Sifeae QE-Q d5-8: value: 1242216
            # 		{'bodyId': 226637348, 'bodyName': 'Sifeae QE-Q d5-8 4', 'distance': 847, 'valueMax': 505027}
            # 		{'bodyId': 226637338, 'bodyName': 'Sifeae QE-Q d5-8 5', 'distance': 1263, 'valueMax': 510505}

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

    def stop(self):
        self.navWatcher.stop()


if __name__ == '__main__':
    scout = EDScout()

    print('Scout is active; Waiting for next route change...')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('done')

    scout.stop()
