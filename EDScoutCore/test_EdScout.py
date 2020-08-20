import pytest
import tempfile
from .EDScout import EDScout
from .JournalInterface import JournalWatcher
from . import EDSMInterface


class TestEdScout:
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
    #     self.test_response = example_journal_entry
    #
    #     def mock_get_system_estimated_value(system_name):
    #         return {'id': 560233253227, 'id64': 18269314557401, 'name': "HIP 64420", 'url': 'https://www.edsm.net/en/system/bodies/id/10594826/name/IC+2602+Sector+GC-T+b4-8', 'estimatedValue': 2413, 'estimatedValueMapped': 2413, 'valuableBodies': []}
    #
    #     monkeypatch.setattr(EDSMInterface, "get_system_estimated_value", mock_get_system_estimated_value)
    #
    #     watcher = JournalWatcher(self.test_dir.name, force_polling=False)
    #     scout = EDScout(journal_watcher=watcher)
    #     # mock out the bit that would normally pass on the result so we can capture it
    #     scout.report_new_info = self.mock_report_new_info
    #     # mock out the identifier that accesses the filesystem
    #     scout.journalChangeIdentifier = self
    #
    #     # ACT
    #     journal_that_changed = 'dummyValue'
    #     scout.on_journal_change(journal_that_changed)
    #
    #     # ASSERT
    #     assert len(self.new_entry) == 2, "There should be one report for the FSD target command then another for the system report"
    #     assert self.new_entry[0] is not None
