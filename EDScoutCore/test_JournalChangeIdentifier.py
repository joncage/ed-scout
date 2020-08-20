import tempfile
import os
from shutil import copyfile

from .JournalInterface import JournalChangeIdentifier


class TestJournalWatcher:

    @staticmethod
    def get_test_file_path(filename):
        script_path = os.path.dirname(__file__)
        data_dir = "../ExampleData/"
        return os.path.abspath(os.path.join(script_path, data_dir, filename))

    def setup_method(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()

    def teardown_method(self):
        # Close the file, the directory will be removed after the test
        self.test_dir.cleanup()

    def test_extract_new_entries_from_file(self):
        # setup the test area
        file_to_watch = "Journal.200725210202.01.log"
        path_to_watch = os.path.join(self.test_dir.name, file_to_watch)
        copyfile(TestJournalWatcher.get_test_file_path("FileChangeTest-PreChange.log"), path_to_watch)

        # initialise the watcher
        jci = JournalChangeIdentifier(self.test_dir.name)

        # simulate a file change event
        with open(TestJournalWatcher.get_test_file_path("FileChangeTest-PostChange.log"), "rb") as input_file:
            with open(path_to_watch, "wb") as output_file:
                output_file.write(input_file.read())

        changed_lines = list(jci.process_journal_change(path_to_watch))

        # Expecting the following as a json object
        #    { "timestamp":"2020-07-25T20:12:47Z", "event":"FSDTarget", "Name":"Plio Eurl JA-K c10-1", "SystemAddress":360878510682, "StarClass":"K", "RemainingJumpsInRoute":12 }'
        assert 1 == len(changed_lines)
        json_entry = changed_lines[0]
        assert isinstance(json_entry, dict)
