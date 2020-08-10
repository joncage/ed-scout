import tempfile
import os
from shutil import copyfile


from EDScoutCore.JournalWatcher import JournalWatcher


class TestJournalWatcher():

    def setup_class(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.callback_arg = None

    def teardown_class(self):
        # Close the file, the directory will be removed after the test
        self.test_dir.cleanup()

    def receive_callback(self, callback_arg):
        self.callback_arg = callback_arg

    def test_extract_new_entries_from_file(self):
        # setup the test area
        file_to_watch = "Journal.200725210202.01.log"
        test_input_file_path = os.path.join(self.test_dir.name, file_to_watch)
        copyfile("..\\ExampleData\\FileChangeTest-PreChange.log", test_input_file_path)

        # initialise the watcher
        jw = JournalWatcher(self.test_dir.name)
        jw.set_callback(self.receive_callback)

        # simulate a file change event
        with open("..\\ExampleData\\FileChangeTest-PostChange.log", "rb") as input_file:
            with open(test_input_file_path, "wb") as output_file:
                output_file.write(input_file.read())

        assert test_input_file_path == self.callback_arg
