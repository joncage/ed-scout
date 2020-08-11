import pytest
import tempfile
import os
from shutil import copyfile
import json


from EDScoutCore.JournalWatcher import JournalChangeIdentifier, JournalWatcher


class TestFastUpdates:

    def setup_method(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.jw = JournalWatcher(self.test_dir.name)
        self.jw.set_callback(self.on_journal_change)
        self.jci = JournalChangeIdentifier(self.test_dir.name)
        self.file_to_watch = "Journal.200725210202.01.log"
        self.path_to_watch = os.path.join(self.test_dir.name, self.file_to_watch)
        self.entries_identified = []
        self.example_data_file = '..\\ExampleData\\Journal.FastWritesOnStartup.log'
        self.example_data_line_count = 0

    def teardown_method(self):
        # Close the file, the directory will be removed after the test
        self.test_dir.cleanup()

    def get_write_sequences(self):
        # Read an example journal file line by line and group into chunks that look like they were written at the same
        # time. This should help us verify the system is capable of reading the rapid updates the game shoves out (my
        # first attempt using os file stat seemed to miss chuiks of info.

        file_chunks = []
        last_timestamp = None
        at_least_one_read = False
        with open(self.example_data_file, "r") as f:
            current_chunk = ""
            for line in f.readlines():
                self.example_data_line_count += 1
                current_timestamp = json.loads(line)["timestamp"]
                if current_timestamp != last_timestamp:
                    if len(current_chunk) > 0:
                        file_chunks.append(current_chunk)
                if at_least_one_read:
                    current_chunk += "\r\n"
                current_chunk += line
                at_least_one_read = True

        if len(current_chunk) > 0:
            file_chunks.append(current_chunk)

        return file_chunks

    def on_journal_change(self, altered_journal):
        updates = list(self.jci.process_journal_change(altered_journal))
        print(f"got: {len(updates)}")
        self.entries_identified.extend(updates)

    def test_extract_new_entries_from_file(self):
        #
        test_data_chunks = self.get_write_sequences()


        # simulate a file change event
        for data_chunk in test_data_chunks:
            with open(self.path_to_watch, "a") as output_file:
                output_file.write(data_chunk)

        # Check we captured it all
        assert self.example_data_line_count == len(self.entries_identified)







