import tempfile
import os
from shutil import copyfile


from .JournalInterface import JournalWatcher


class TestJournalWatcher():

    def setup_method(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.callback_arg = None

    def teardown_method(self):
        # Close the file, the directory will be removed after the test
        self.test_dir.cleanup()

    def receive_callback(self, callback_arg):
        self.callback_arg = callback_arg

    @staticmethod
    def get_test_file_path(filename):
        script_path = os.path.dirname(__file__)
        data_dir = "..\\ExampleData\\"
        return os.path.abspath(os.path.join(script_path, data_dir, filename))

    def test_extract_new_entries_from_file(self):

        # setup the test area
        file_to_watch = "Journal.200725210202.01.log"
        test_input_file_path = os.path.join(self.test_dir.name, file_to_watch)

        pre_change_file_path = TestJournalWatcher.get_test_file_path("FileChangeTest-PreChange.log")
        copyfile(pre_change_file_path, test_input_file_path)

        # initialise the watcher
        jw = JournalWatcher(self.test_dir.name)
        jw.set_callback(self.receive_callback)

        # simulate a file change event
        post_change_file_path = TestJournalWatcher.get_test_file_path("FileChangeTest-PostChange.log")
        with open(post_change_file_path, "rb") as input_file:
            with open(test_input_file_path, "wb") as output_file:
                output_file.write(input_file.read())

        assert test_input_file_path == self.callback_arg
