import time
import json
import logging
from .SavedGamesLocator import get_saved_games_path

from .NavRouteIntegrator import NavRouteIntegrator
from . import EDSMInterface
from .ZmqWrappers import Sender
from .JournalInterface import JournalWatcher, JournalChangeProcessor
from . import BodyAppraiser
from .OutputRecorder import OutputRecorder

logger = logging.getLogger('EDScoutCore')

default_journal_path = get_saved_games_path()


class EDScout:

    def __init__(
            self,
            force_polling=False,
            journal_watcher=None,
            journal_change_processor=JournalChangeProcessor(),
            record_output=False):

        if journal_watcher is None:
            journal_watcher = JournalWatcher(default_journal_path, force_polling=force_polling)

        if record_output:
            self.journal_stream_recorder = OutputRecorder('ScoutStreamRecord')
        else:
            self.journal_stream_recorder = None

        self.navRouteIntegrator = NavRouteIntegrator()

        # Setup the journal watcher
        self.journal_change_processor = journal_change_processor
        self.journalWatcher = journal_watcher
        self.journalWatcher.set_callback(self.on_journal_change)

        # Setup the ZMQ forwarder that'll pass on the log file changes
        self.sender = Sender()
        self.port = self.sender.port

        self.star_cache = {}

    def trigger_current_journal_check(self):
        self.journalWatcher.trigger_current_journal_check()

    @staticmethod
    def requires_system_lookup(new_event):
        return new_event["event"] in ["FSDTarget", "Location", "FSDJump"]

    @staticmethod
    def requires_body_investigation(new_event):
        return new_event["event"] in ["FSSDiscoveryScan", "FSSAllBodiesFound"]

    def add_to_star_cache(self, journal_entry):
        if "SystemAddress" and "StarClass" in journal_entry:
            logger.info(f"Storing {journal_entry['SystemAddress']} => {journal_entry['StarClass']}")
            self.star_cache[journal_entry['SystemAddress']] = journal_entry["StarClass"]

    def lookup_star_class(self, journal_entry):
        logger.info(f"Looking up system {journal_entry['SystemAddress']}")
        return self.star_cache.get(journal_entry["SystemAddress"], "?")


    @staticmethod
    def identify_system_name(journal_entry):
        if "StarSystem" in journal_entry:
            system_name = journal_entry["StarSystem"]
        elif "Name" in journal_entry:
            # FSD Target uses Name instead of StarSystem to name this for some reason.
            system_name = journal_entry["Name"]
        elif "SystemName" in journal_entry:
            # FSSDiscoveryScan
            system_name = journal_entry["SystemName"]
        else:
            raise Exception("Failed to find system name from " + str(journal_entry))

        return system_name

    def create_system_report(self, journal_entry):
        # Simulating something like a nav event:
        # { "timestamp":"2020-08-12T00:19:35Z", "event":"NavRoute", "Route":[
        # { "StarSystem":"Col 285 Sector GL-T b18-4", "SystemAddress":9470537180601, "StarPos":[259.00000,3.62500,36.81250], "StarClass":"M" },
        # { "StarSystem":"Col 285 Sector ZE-V b17-3", "SystemAddress":7270708618673, "StarPos":[209.00000,4.40625,22.53125], "StarClass":"M" },
        # { "StarSystem":"Antliae Sector JR-W b1-4", "SystemAddress":9469195068841, "StarPos":[163.56250,18.03125,1.31250], "StarClass":"M" },
        # { "StarSystem":"Col 285 Sector QD-X b16-5", "SystemAddress":11667949888937, "StarPos":[137.06250,15.00000,-3.53125], "StarClass":"M" }
        #  ] }

        # ..from...

        # { "timestamp":"2020-07-17T21:49:18Z", "event":"FSDTarget", "Name":"HIP 64420", "SystemAddress":560233253227, "StarClass":"F", "RemainingJumpsInRoute":1 }
        # { "timestamp":"2020-07-17T21:48:48Z", "event":"Location", "Docked":false, "StarSystem":"Mel 111 Sector HH-V c2-1", "SystemAddress":358663590610, "StarPos":[-60.71875,318.40625,5.03125], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"Mel 111 Sector HH-V c2-1", "BodyID":0, "BodyType":"Star" }
        # { "timestamp":"2020-07-17T21:50:36Z", "event":"FSDJump", "StarSystem":"HIP 64420", "SystemAddress":560233253227, "StarPos":[-49.87500,317.75000,-0.56250], "SystemAllegiance":"", "SystemEconomy":"$economy_None;", "SystemEconomy_Localised":"None", "SystemSecondEconomy":"$economy_None;", "SystemSecondEconomy_Localised":"None", "SystemGovernment":"$government_None;", "SystemGovernment_Localised":"None", "SystemSecurity":"$GAlAXY_MAP_INFO_state_anarchy;", "SystemSecurity_Localised":"Anarchy", "Population":0, "Body":"HIP 64420", "BodyID":0, "BodyType":"Star", "JumpDist":12.219, "FuelUsed":0.947167, "FuelLevel":12.835925 }

        system_name = EDScout.identify_system_name(journal_entry)
        if "StarClass" in journal_entry:
            star_class = journal_entry["StarClass"]
        else:
            # Rely on edsm to fill this in
            system = EDSMInterface.get_system(system_name)
            logger.debug(system)

            if system and system["primaryStar"]:
                star_class = system["primaryStar"]["type"].split(maxsplit=1)[0]
            else:
                star_class = self.lookup_star_class(journal_entry)

        additional_info = {
            'StarSystem': system_name,
            'SystemAddress': journal_entry["SystemAddress"],
            'StarClass': star_class
        }

        # print(f"SystemName={systemName}")
        edsm_info = EDScout.get_edsm_system_report(system_name, journal_entry['event'])
        edsm_info.update(additional_info)

        return edsm_info

    def append_info_to_scan(self, new_entry):
        # { "timestamp":"2020-08-20T23:57:05Z", "event":"Scan", "ScanType":"Detailed", "BodyName":"Pro Eurl MO-H d10-11 2", "BodyID":27, "Parents":[ {"Star":0} ], "StarSystem":"Pro Eurl MO-H d10-11", "SystemAddress":388770122203, "DistanceFromArrivalLS":5502.835374, "TidalLock":false, "TerraformState":"", "PlanetClass":"Sudarsky class III gas giant", "Atmosphere":"", "AtmosphereComposition":[ { "Name":"Hydrogen", "Percent":74.636978 }, { "Name":"Helium", "Percent":25.363026 } ], "Volcanism":"", "MassEM":1115.081787, "Radius":76789080.000000, "SurfaceGravity":75.373241, "SurfaceTemperature":272.228607, "SurfacePressure":0.000000, "Landable":false, "SemiMajorAxis":1634133458137.512207, "Eccentricity":0.018997, "OrbitalInclination":-4.741432, "Periapsis":30.585864, "OrbitalPeriod":1122406125.068665, "RotationPeriod":113532.553386, "AxialTilt":-0.182964, "Rings":[ { "Name":"Pro Eurl MO-H d10-11 2 A Ring", "RingClass":"eRingClass_MetalRich", "MassMT":1.8852e+12, "InnerRad":1.1586e+08, "OuterRad":3.61e+08 } ], "ReserveLevel":"PristineResources", "WasDiscovered":false, "WasMapped":false }

        if 'Belt Cluster' in new_entry["BodyName"]:
            new_entry["BodyName"] = new_entry["BodyName"].replace("Belt Cluster ", "")
            new_entry["BodyClass"] = "Belt Cluster"

        new_entry["MappedValue"] = BodyAppraiser.appraise_body(new_entry)
        return new_entry

    def append_info_to_fsdjump(self, new_entry):
        new_entry["StarClass"] = self.lookup_star_class(new_entry)

        edsm_report = EDScout.get_edsm_system_report(new_entry['StarSystem'], 'FSDJump')
        new_entry["valuableBodies"] = edsm_report.get("valuableBodies",[])
        new_entry["estimatedValueMapped"] = edsm_report.get("estimatedValueMapped",0)

        return new_entry

    def get_info_tacker_method(self, event_type):
        tacker_method = None
        if event_type == "Scan":
            tacker_method = self.append_info_to_scan
        elif event_type == "FSDJump":
            tacker_method = self.append_info_to_fsdjump
        return tacker_method

    def tack_on_additional_info(self, new_entry):
        tacker = self.get_info_tacker_method(new_entry["event"])
        if tacker:
            new_entry = tacker(new_entry)
        return new_entry

    def process_journal_change(self, new_entry):

        # Some stuff we don't care about
        excluded_event_types = ["Music", "ReceiveText", "FuelScoop"]
        if new_entry["event"] in excluded_event_types:
            return

        if new_entry["event"] == "NavRoute":
            self.on_new_route(new_entry)
        else:
            new_entry = self.tack_on_additional_info(new_entry)

            # Spit out the event
            self.report_new_info(new_entry)

            # If it needed a detailed system lookup, add that as well
            if EDScout.requires_system_lookup(new_entry):
                self.report_new_info(self.create_system_report(new_entry))

            # if EDScout.requires_system_lookup(new_entry) or EDScout.requires_body_investigation(new_entry):
            #     with requests_cache.disabled():
            #         logger.info(f"BODY INFO: {EDSMInterface.get_bodies(EDScout.identify_system_name(new_entry))}")

    @staticmethod
    def check_system_content(new_entry):
        bodies = EDSMInterface.get_bodies(EDScout.identify_system_name(new_entry))
        logger.info("Body check: ", bodies)

    def on_journal_change(self, altered_journal):
        entries = self.journal_change_processor.process_journal_change(altered_journal)

        entries_with_populated_nav_route = self.navRouteIntegrator.process_new_journal_entries(entries)

        self.process_new_journal_entries(entries_with_populated_nav_route)

    def process_new_journal_entries(self, entries):
        for new_entry in entries:
            if self.journal_stream_recorder:
                self.journal_stream_recorder.record('journal_output', new_entry)
            self.add_to_star_cache(new_entry)
            self.process_journal_change(new_entry)

    @staticmethod
    def get_edsm_system_report(star_system, association):

        # print(f"EVALUATING={star_system}")

        estimated_value = EDSMInterface.get_system_estimated_value(star_system)

        # IC 2602 Sector GC-T b4-8 (M) Charted:
        #   {'id': 10594826, 'id64': 18269314557401, 'name': 'IC 2602 Sector GC-T b4-8', 'url': 'https://www.edsm.net/en/system/bodies/id/10594826/name/IC+2602+Sector+GC-T+b4-8', 'estimatedValue': 2413, 'estimatedValueMapped': 2413, 'valuableBodies': []}

        # print(f"estimated_value={estimated_value}")

        report_content = {'type': 'System-' + association}
        report_content.update(estimated_value)
        is_uncharted = not estimated_value
        report_content['charted'] = not is_uncharted
        # print(f"report_content['charted']={report_content['charted']}, is_uncharted={is_uncharted}")

        return report_content

    def on_new_route(self, nav_route):
        logger.debug('New nav route detected; forwarding and looking up systems')

        nav_route['type'] = 'NewRoute'

        self.report_new_info(nav_route)

        for jump_dest in nav_route['Route']:
            self.add_to_star_cache(jump_dest)
            report_content = EDScout.get_edsm_system_report(jump_dest['StarSystem'], 'NavRoute')
            report_content.update(jump_dest)
            self.report_new_info(report_content)

    def report_new_info(self, new_info):
        json_to_send = json.dumps(new_info)
        logger.info("Reporting: " + str(json_to_send))
        if self.journal_stream_recorder:
            self.journal_stream_recorder.record('core_output', new_info)
        self.sender.send(json_to_send)

    def stop(self):
        self.journalWatcher.stop()


if __name__ == '__main__':
    scout = EDScout()

    logger.info('Scout is active; Waiting for next route change...')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('done')

    scout.stop()
