import time
import json
import logging

from EDScoutCore.NavRouteWatcher import NavRouteWatcher
import EDScoutCore.EDSMInterface as EDSMInterface
from EDScoutCore.NavRouteForwarder import Sender
from EDScoutCore.JournalWatcher import JournalWatcher, JournalChangeIdentifier

logger = logging.getLogger("EDScoutLogger")

class EDScout:

    def __init__(self):
        # Set up the nav route watcher
        self.navWatcher = NavRouteWatcher()
        self.navWatcher.set_callback(self.on_new_route)

        # Setup the journal watcher
        self.journalWatcher = JournalWatcher()
        self.journalWatcher.set_callback(self.on_journal_change)
        self.journalChangeIdentifier = JournalChangeIdentifier()

        # Setup the ZMQ forwarder that'll pass on the log file changes
        self.sender = Sender()
        self.port = self.sender.port

    def on_journal_change(self, altered_journal):
        excluded_event_types = ["NavRoute", "Music", "ReceiveText", "FuelScoop"]

        for new_entry in self.journalChangeIdentifier.process_journal_change(altered_journal):
            if new_entry["event"] not in excluded_event_types:
                self.report_new_info(new_entry)


    def on_new_route(self, nav_route):
        logger.debug('New route: ')

        self.report_new_info({'type': 'NewRoute'})

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
            logger.debug(message)

            report_content = {'type': 'System'}
            report_content.update(jump_dest)
            report_content.update(estimatedValue)
            report_content['charted'] = not unchartedCheck

            self.report_new_info(report_content)

            if not unchartedCheck:
                for body in estimatedValue['valuableBodies']:
                    logger.debug("\t\t"+str(body))

    def report_new_info(self, new_info):
        self.sender.send(json.dumps(new_info))


    def stop(self):
        self.navWatcher.stop()


if __name__ == '__main__':
    scout = EDScout()

    logger.info('Scout is active; Waiting for next route change...')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('done')

    scout.stop()
