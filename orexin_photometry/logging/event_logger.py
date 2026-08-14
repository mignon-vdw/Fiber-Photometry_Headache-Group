import csv
from datetime import datetime

class EventLogger:

    def __init__(self, filename):

        self.filename = filename

        with open(self.filename, "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "event_name",
                "timestamp"
            ])

    def log_event(self, event_name):

        with open(self.filename, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                event_name,
                datetime.now().isoformat()
            ])