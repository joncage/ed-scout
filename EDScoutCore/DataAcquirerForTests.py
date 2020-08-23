import os
import glob
import pathlib


def test_acquire_scan_data_from_journals():
    journal_file_pattern = "Journal*.log"
    journal_path = os.path.join(str(pathlib.Path.home()), "Saved Games\\Frontier Developments\\Elite Dangerous")
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

    with open("..\\ExampleData\\ExampleScans.json", "w") as output:
        output.writelines(scan_lines)


if __name__ == '__main__':
    test_acquire_scan_data_from_journals()
