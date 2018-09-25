import logging
import threading
logger = logging.getLogger(__name__)

"""
- Scans the journal file
- Captures events
- Checks for validity
- Supplies data to the main window
- Shoves stuff into the database
"""


class JournalMonitor(threading.Thread):
    def __init__(self, journal_file):
        super(JournalMonitor, self).__init__()
        self.file = journal_file

    def run(self):
        # FINISH ME
        pass
