from inspect import signature
import json
import time
import os
import glob
import logging

from pathlib import Path
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
from EDScoutCore.FileSystemUpdatePrompter import FileSystemUpdatePrompter

default_journal_path = os.path.join(str(Path.home()), "Saved Games\\Frontier Developments\\Elite Dangerous")
journal_file_pattern = "journal.*.log"

logger = logging.getLogger('JournalInterface')


class JournalChangeIdentifier:

    def __init__(self, journal_path=default_journal_path):
        pass
        self.journals = {}
        self.journal_path = journal_path

        logger.debug(f"watching for journal changes in {self.journal_path}")

        self._init_journal_lists()
        self._new_journal_entry_callback = None

        self.latest_journal = self.identify_latest_journal()

        # Prompter is required to force the file system to do updates on some systems so we get regular updates from the
        # journal watcher.
        self.prompter = FileSystemUpdatePrompter(self.latest_journal)

    def identify_latest_journal(self):
        if len(self.journals.keys()) == 0:
            return None

        keys = sorted(self.journals.keys())
        return keys[-1]

    def process_journal_change(self, changed_file):
        if changed_file != self.latest_journal:
            self.latest_journal = changed_file
            self.prompter.set_watch_file(self.latest_journal)

        new_size = os.stat(changed_file).st_size
        new_data = None

        # If the game was loaded after the scout it will start a new journal which we need to treat as unscanned.
        if changed_file not in self.journals:
            self.journals[changed_file] = 0

        logger.debug(f'{changed_file} - Size change: {self.journals[changed_file]} to {new_size}')
        if new_size > 0:  # Don't  try and read it if this is the first notification (we seem to get two; one from the file being cleared).
            # Check how much it has grown and read the excess
            size_diff = new_size - self.journals[changed_file]
            if size_diff > 0:
                with open(changed_file, 'rb') as f:
                    f.seek(-size_diff, os.SEEK_END)  # Note minus sign
                    new_data = f.read()

        entries = []

        if new_data:
            new_journal_lines = JournalChangeIdentifier.binary_file_data_to_lines(new_data)

            try:
                for line in new_journal_lines:
                    logger.debug(f'New journal entry detected: {line}')

                    entry = json.loads(line)

                    entry['type'] = "JournalEntry"  # Add an identifier that's common to everything we shove down the outgoing pipe so the receiver can distiguish.
                    entries.append(entry)

                logger.debug(f'Found {len(entries)} new entries')

                for entry in entries:
                    yield entry
                self.journals[changed_file] = new_size

            except json.decoder.JSONDecodeError as e:
                logger.exception(e)

    @staticmethod
    def binary_file_data_to_lines(binary_data):
        as_ascii = binary_data.decode('UTF-8')
        all_lines = as_ascii.split("\r\n")
        all_lines.pop()  # Drop the last empty line
        return all_lines

    def _init_journal_lists(self):
        journal_files = glob.glob(os.path.join(self.journal_path, journal_file_pattern))
        for journal_file in journal_files:
            self.journals[journal_file] = os.stat(journal_file).st_size


class JournalWatcher:

    def __init__(self, path=default_journal_path, force_polling=False):
        self.path = path
        self.force_polling = force_polling
        self._configure_watchers()

    def set_callback(self, on_journal_change):
        self.event_handler.set_callback(on_journal_change)

    def stop(self):
        self.observer.stop()
        self.observer.join()

    class _EntriesChangeHandler(PatternMatchingEventHandler):

        def __init__(self):
            super(JournalWatcher._EntriesChangeHandler, self).__init__(
                patterns=['*Journal*.log'],
                ignore_patterns=[],
                ignore_directories=True)

            self.on_journal_change = None

        def set_callback(self, on_new_journal_entry):
            self.on_journal_change = on_new_journal_entry

        def on_modified(self, event):
            changed_file = str(event.src_path)
            logger.debug("Journal change: " + changed_file)
            self.on_journal_change(changed_file)

        def on_created(self, event):
            file = str(event.src_path)
            logger.debug("Journal created: " + file)

        def on_deleted(self, event):
            file = str(event.src_path)
            logger.debug("Journal deleted: " + file)

        def on_moved(self, event):
            file = str(event.src_path)
            logger.debug("Journal moved: " + file)

    def _configure_watchers(self):
        self.event_handler = JournalWatcher._EntriesChangeHandler()

        if self.force_polling:
            self.observer = PollingObserver(0.25)  # Poll every quarter of a second
        else:
            self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=False)
        self.observer.start()


if __name__ == '__main__':

    def ReportJournalChange(journal_hange):
        print('New route detected:' + str(journal_hange))

    journalWatcher = JournalWatcher()
    journalWatcher.set_callback(ReportJournalChange)

    print('running')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('done')

    journalWatcher.stop()
