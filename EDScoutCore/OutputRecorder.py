from .ZmqWrappers import Receiver
import json
from logging import log


class OutputRecorder():

    def __init__(self, port):
        zmq_port_test = None
        self.r = Receiver(port=zmq_port_test)

    def run(self):
        while True:
            message = self.r.receive().decode('ascii')
            try:
                log.debug("Received:   '" + message + "'")
                content = dict(data=json.loads(message))
                log.debug("Forwarding: '" + str(content) + "'")
                # socketio.emit('log', content, broadcast=True)
            except Exception as pass_on_failure:
                log.exception(pass_on_failure)


# JournalInterface.JournalWatcher._on_journal_change
#     JournalChangeProcessor.process_journal_change
#         JournalChangeProcessor.binary_file_data_to_lines -> yields entries
#               EDScout.forward_journal_change
