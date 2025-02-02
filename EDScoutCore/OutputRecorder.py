import json
import os
import platform
from pathlib import Path
from datetime import datetime, timezone


class OutputRecorder:

    def __init__(self, file_name_prefix):
        osname = platform.system()
        if osname == 'Windows':
            recording_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'EDScout', 'StreamRecords')
        elif osname == 'Linux':
            recording_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'EDScout', 'StreamRecords')
        else:
            raise Exception(f"EDScout does not support {osname}")

        if not os.path.isdir(recording_dir):
            Path(recording_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%S')
        file_name = file_name_prefix + '-' + timestamp + ".json"
        file_path = os.path.join(recording_dir, file_name)
        self.output = open(file_path, "w")

    def record(self, stream_point, new_entry):
        new_record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'stream_point': stream_point,
            'entry': new_entry
        }
        str_record = json.dumps(new_record)
        self.output.write(str_record + "\n")
        self.output.flush()

    def close(self):
        self.output.close()
