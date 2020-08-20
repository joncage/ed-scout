import json
import time
import os
import glob
import logging

from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
from .FileSystemUpdatePrompter import FileSystemUpdatePrompter

journal_file_pattern = "journal.*.log"

logger = logging.getLogger('JournalInterface')


class JournalChangeProcessor:

    def __init__(self):
        self._new_journal_entry_callback = None

        self.latest_journal = None
        self.journal_size = 0

    def start_reading_journal(self, changed_file):
        # TODO: Scan though the file to find the last location, FSD target and if there's a navroute file, set that too.
        self.latest_journal = changed_file
        self.journal_size = os.stat(changed_file).st_size

    def process_journal_change(self, changed_file):
        new_size = os.stat(changed_file).st_size

        if changed_file != self.latest_journal:
            self.latest_journal = changed_file
            self.journal_size = 0

        new_data = None
        logger.debug(f'{changed_file} - Size change: {self.journal_size} to {new_size}')
        if new_size > 0:  # Don't  try and read it if this is the first notification (we seem to get two; one from the file being cleared).
            # Check how much it has grown and read the excess
            size_diff = new_size - self.journal_size
            if size_diff > 0:
                with open(changed_file, 'rb') as f:
                    f.seek(-size_diff, os.SEEK_END)  # Note minus sign
                    new_data = f.read()

        if new_data:
            new_journal_lines = JournalChangeProcessor.binary_file_data_to_lines(new_data)

            try:
                entries = []

                # Deal with all entries in one go in case the last one isn't complete and throws.
                # This ensures we treat it as one atomic operation - nex time round we'll re-read the data to try again.
                for line in new_journal_lines:
                    logger.debug(f'New journal entry detected: {line}')

                    entry = json.loads(line)

                    entry['type'] = "JournalEntry"  # Add an identifier that's common to everything we shove down the outgoing pipe so the receiver can distiguish.
                    entries.append(entry)

                logger.debug(f'Found {len(entries)} new entries')

                for entry in entries:
                    yield entry
                    self.journal_size = new_size

            except json.decoder.JSONDecodeError as e:
                logger.exception(e)

    @staticmethod
    def binary_file_data_to_lines(binary_data):
        as_ascii = binary_data.decode('UTF-8')
        all_lines = as_ascii.split("\r\n")
        all_lines.pop()  # Drop the last empty line
        return all_lines


class _EntriesChangeHandler(PatternMatchingEventHandler):

    def __init__(self):
        super(_EntriesChangeHandler, self).__init__(
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
        changed_file = str(event.src_path)
        logger.info("Journal created: " + changed_file)
        self.on_journal_change(changed_file)

    def on_deleted(self, event):
        file = str(event.src_path)
        logger.debug("Journal deleted: " + file)

    def on_moved(self, event):
        file = str(event.src_path)
        logger.debug("Journal moved: " + file)


class JournalWatcher:

    def __init__(self, path, force_polling=False):
        self.journal_path = path
        self.force_polling = force_polling
        self.prompter = None
        self.report_journal_change = None

        self._configure_watchers()

        self.latest_journal = self.identify_latest_journal()
        self.set_current_journal(self.latest_journal)

    def set_callback(self, on_journal_change):
        self.report_journal_change = on_journal_change

    def set_current_journal(self, current_journal):
        if self.prompter is None:
            self.prompter = FileSystemUpdatePrompter(current_journal)

        if current_journal != self.latest_journal:
            self.prompter.set_watch_file(current_journal)
            self.latest_journal = current_journal

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def _on_journal_change(self, event):
        self.report_journal_change(event)

    def _configure_watchers(self):
        if not os.path.exists(self.journal_path):
            raise Exception(f"Unable to start watching; Path does not exist: {self.journal_path}")

        self.event_handler = _EntriesChangeHandler()

        self.event_handler.set_callback(self._on_journal_change)

        if self.force_polling:
            self.observer = PollingObserver(0.25)  # Poll every quarter of a second
        else:
            self.observer = Observer()
        self.observer.schedule(self.event_handler, self.journal_path, recursive=False)
        self.observer.start()

    def identify_latest_journal(self):
        journal_files = glob.glob(os.path.join(self.journal_path, journal_file_pattern))
        journals = []
        for journal_file in journal_files:
            journals.append(journal_file)

        last_journal = sorted(journals)[-1]
        return last_journal


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
