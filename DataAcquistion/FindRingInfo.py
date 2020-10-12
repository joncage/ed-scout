import os
import glob
import json
from EDScoutCore.SavedGamesLocator import get_saved_games_path


def find_rings(journal_lines):
    max_len = 0
    ring_types = set()
    for line in journal_lines:
        if 'rings' in line.lower():
            data = json.loads(line)
            rings = data['Rings']
            ring_count = len(rings)
            if ring_count > max_len:
                max_len = ring_count
            print()
            for ring in rings:
                ring_composition = ring['RingClass'].replace('eRingClass_', '')
                print('\t'+ring_composition)
                ring_types.add(ring_composition)
    print(f"Max rings: {max_len}")
    print(f"Types: {ring_types}")


def test_acquire_scan_data_from_journals():
    journal_file_pattern = "Journal*.log"
    journal_path = get_saved_games_path()
    search_pattern = os.path.join(journal_path, journal_file_pattern)
    print(f"Searching with '{search_pattern}'")
    journal_files = glob.glob(search_pattern)
    print(f"Found {len(journal_files)} journals")

    scan_lines = []
    for journal_file in journal_files:
        with open(journal_file, "r", encoding='UTF-8') as journal:
            relevant_lines = [line for line in journal.readlines() if '"Scan"' in line]
            print(f"{len(relevant_lines)} found in {journal_file}")
            scan_lines.extend(relevant_lines)

    rings = find_rings(scan_lines)

    #extremes_at_uniques = identify_extremes(uniques)

    #with open("..\\ExampleData\\ExampleScans.json", "w") as output:
    #    output.writelines(s + '\n' for s in extremes_at_uniques)


if __name__ == '__main__':
    test_acquire_scan_data_from_journals()
