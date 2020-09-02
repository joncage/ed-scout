import pytest
import tempfile
from .EDScout import EDScout


class TestEdScoutJournalProcessing:
    test_data = [
        {"timestamp": "2020-07-17T21:49:18Z", "event": "FSDTarget", "Name": "HIP 64420", "SystemAddress": 560233253227,
         "StarClass": "F", "RemainingJumpsInRoute": 1},
        {"timestamp": "2020-07-17T21:48:48Z", "event": "Location", "Docked": False,
         "StarSystem": "Mel 111 Sector HH-V c2-1", "SystemAddress": 358663590610,
         "StarPos": [-60.71875, 318.40625, 5.03125], "SystemAllegiance": "", "SystemEconomy": "$economy_None;",
         "SystemEconomy_Localised": "None", "SystemSecondEconomy": "$economy_None;",
         "SystemSecondEconomy_Localised": "None", "SystemGovernment": "$government_None;",
         "SystemGovernment_Localised": "None", "SystemSecurity": "$GAlAXY_MAP_INFO_state_anarchy;",
         "SystemSecurity_Localised": "Anarchy", "Population": 0, "Body": "Mel 111 Sector HH-V c2-1", "BodyID": 0,
         "BodyType": "Star"},
        {"timestamp": "2020-07-17T21:50:36Z", "event": "FSDJump", "StarSystem": "HIP 64420",
         "SystemAddress": 560233253227, "StarPos": [-49.87500, 317.75000, -0.56250], "SystemAllegiance": "",
         "SystemEconomy": "$economy_None;", "SystemEconomy_Localised": "None", "SystemSecondEconomy": "$economy_None;",
         "SystemSecondEconomy_Localised": "None", "SystemGovernment": "$government_None;",
         "SystemGovernment_Localised": "None", "SystemSecurity": "$GAlAXY_MAP_INFO_state_anarchy;",
         "SystemSecurity_Localised": "Anarchy", "Population": 0, "Body": "HIP 64420", "BodyID": 0, "BodyType": "Star",
         "JumpDist": 12.219, "FuelUsed": 0.947167, "FuelLevel": 12.835925}
    ]

    def setup_method(self, test_data):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.new_entry = []

    def teardown_method(self):
        # Close the file, the directory will be removed after the test
        self.test_dir.cleanup()

    def mock_report_new_info(self, new_entry):
        self.new_entry.append(new_entry)

    def process_journal_change(self, altered_journal):
        return [{'event': 'Music'}, self.test_response]

    @pytest.mark.parametrize("example_journal_entry", test_data)
    def test_music_changes_not_forwarded(self, monkeypatch, example_journal_entry):
        pass


class DummyWatcher():
    def __init__(self):
        pass

    def set_callback(self, callback):
        pass


class DummyJournalChangeProcessor():
    def __init__(self):
        pass


class TestEdScoutEntryProcessing:
    def setup_method(self, test_data):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.new_entry = []
        # { "timestamp":"2020-08-20T23:57:05Z", "event":"Scan", "ScanType":"Detailed", "BodyName":"Pro Eurl MO-H d10-11 2", "BodyID":27, "Parents":[ {"Star":0} ], "StarSystem":"Pro Eurl MO-H d10-11", "SystemAddress":388770122203, "DistanceFromArrivalLS":5502.835374, "TidalLock":false, "TerraformState":"", "PlanetClass":"Sudarsky class III gas giant", "Atmosphere":"", "AtmosphereComposition":[ { "Name":"Hydrogen", "Percent":74.636978 }, { "Name":"Helium", "Percent":25.363026 } ], "Volcanism":"", "MassEM":1115.081787, "Radius":76789080.000000, "SurfaceGravity":75.373241, "SurfaceTemperature":272.228607, "SurfacePressure":0.000000, "Landable":false, "SemiMajorAxis":1634133458137.512207, "Eccentricity":0.018997, "OrbitalInclination":-4.741432, "Periapsis":30.585864, "OrbitalPeriod":1122406125.068665, "RotationPeriod":113532.553386, "AxialTilt":-0.182964, "Rings":[ { "Name":"Pro Eurl MO-H d10-11 2 A Ring", "RingClass":"eRingClass_MetalRich", "MassMT":1.8852e+12, "InnerRad":1.1586e+08, "OuterRad":3.61e+08 } ], "ReserveLevel":"PristineResources", "WasDiscovered":false, "WasMapped":false }

    def mock_report_new_info(self, new_entry):
        self.new_entry.append(new_entry)

    def test_process_scan_entry(self):
        # Input data
        new_entry = {"timestamp": "2020-08-20T23: 56: 51Z",
                     "event": "Scan",
                     "ScanType": "AutoScan",
                     "BodyName": "Pro Eurl MO-H d10-11 B Belt Cluster 10",
                     "BodyID": 17,
                     "Parents": [{"Ring": 7}, {"Star": 0}],
                     "StarSystem": "Pro Eurl MO-H d10-11",
                     "SystemAddress": 388770122203,
                     "DistanceFromArrivalLS": 1728.885092,
                     "WasDiscovered": False,
                     "WasMapped": False}

        # ARRANGE
        scout = EDScout(journal_watcher=DummyWatcher(), journal_change_processor=DummyJournalChangeProcessor())
        scout.report_new_info = self.mock_report_new_info

        # ACT
        scout.process_journal_change(new_entry)

        # ASSERT
        assert len(self.new_entry) == 1, "There should be one report for the FSD target command then another for the " \
                                         "system report"
        reported_entry = self.new_entry[0]
        assert reported_entry is not None
        assert 'MappedValue' in reported_entry
        assert 'BodyName' in reported_entry
        assert 'StarSystem' in reported_entry
