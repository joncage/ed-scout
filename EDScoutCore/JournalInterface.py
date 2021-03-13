import json
import time
import os
import glob
import logging

from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
from .FileSystemUpdatePrompter import FileSystemUpdatePrompter

journal_file_pattern = "Journal.*.log"

logger = logging.getLogger('JournalInterface')


class JournalChangeProcessor:

    def __init__(self):
        self._new_journal_entry_callback = None

        self.latest_journal = None
        self.journal_size = 0

    def start_reading_journal(self, changed_file):
        self.latest_journal = changed_file

        # Start at zero; If we have zero as the size, we'll process the whole file but just use the last entry.
        self.journal_size = 0

    @staticmethod
    def find_latest_navigation_entries(journal_lines):
        nav_events = {
            'NavRoute': None,
            'FSDTarget': None,
            'Location': None,
            'FSDJump': None,
            # No point processing these as it should only matter if JSD jump i.e. arriving was there.
            # 'StartJump': None
        }

        # Scan though the file to find the last location, FSD target and if there's a navroute file, set that too.
        for journal_entry_str in journal_lines:
            journal_entry = JournalChangeProcessor.entry_from_journal_line(journal_entry_str)
            event_type = journal_entry['event']
            if event_type in nav_events.keys():
                needs_storing = (nav_events[event_type] is None) or \
                                (nav_events[event_type]['timestamp'] < journal_entry['timestamp'])
                if needs_storing:
                    nav_events[event_type] = journal_entry

        # If there's a location and any other event, we can ditch the location as it will be superceded by the later
        # events.
        values = [x for x in nav_events.values() if x]
        if nav_events['Location']:
            if len(values) > 1:
                nav_events['Location'] = None
                values = [x for x in nav_events.values() if x]

        # If there's a jump or target after the last navroute, we should send them. Otherwise they should be ignored.
        nav_events_to_return = []
        if len(values) > 0:
            chronological_values = sorted(values, key=lambda k: k['timestamp'])
            last_event = chronological_values[-1]
            if last_event['event'] == 'NavRoute':
                nav_events_to_return = [last_event]
            else:
                nav_events_to_return = chronological_values

        return nav_events_to_return

    @staticmethod
    def entry_from_journal_line(line):
        logger.debug(f'New journal entry identified: {line}')
        entry = json.loads(line)
        entry['type'] = "JournalEntry"  # Add an identifier that's common to everything we shove down the outgoing pipe so the receiver can distiguish.
        return entry

    def process_journal_change(self, changed_file):
        new_size = os.stat(changed_file).st_size

        if changed_file != self.latest_journal:
            self.start_reading_journal(changed_file)

        new_data = None
        logger.debug(f'{changed_file} - Size change: {self.journal_size} to {new_size}')
        if new_size > 0:  # Don't  try and read it if this is the first notification (we seem to get two; one from the file being cleared).
            # Check how much it has grown and read the excess
            size_diff = new_size - self.journal_size
            if size_diff > 0:
                with open(changed_file, 'rb') as f:
                    f.seek(-size_diff, os.SEEK_END)  # Note minus sign
                    new_data = f.read()

        entries = []

        try:
            if new_data:
                new_journal_lines = JournalChangeProcessor.binary_file_data_to_lines(new_data)

                if self.journal_size == 0:
                    entries = JournalChangeProcessor.find_latest_navigation_entries(new_journal_lines)
                    logger.debug(f'New journal detected; Picked out {len(entries)} entries')
                else:
                    # Deal with all entries in one go in case the last one isn't complete and throws.
                    # This ensures we treat it as one atomic operation.
                    # Next time round we'll re-read the data to try again.
                    for line in new_journal_lines:
                        entry = JournalChangeProcessor.entry_from_journal_line(line)
                        entries.append(entry)

                    logger.debug(f'Found {len(entries)} new entries')

                self.journal_size = new_size
        except json.decoder.JSONDecodeError as e:
            logger.exception(e)

        return entries

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

    def trigger_current_journal_check(self):
        self._on_journal_change(self.latest_journal)

    def _on_journal_change(self, altered_file):
        self.set_current_journal(altered_file)  # Make sure we keep the prompter pointed at the current file.
        try:
            self.report_journal_change(altered_file)
        except Exception as e:
            # Capture and report.
            # Hopefully this will prevent the background watcher from going down permanently.
            logger.exception(e)

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

        if len(journals) > 0:
            return sorted(journals)[-1]
        else:
            return None


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
