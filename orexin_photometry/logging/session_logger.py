"""
session_logger.py


"""

import csv
from datetime import datetime

class SessionLogger:

    def __init__(self, filename):

        self.filename = filename

        with open(self.filename, "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "trial_number",
                "stimulus",
                "stimulus_duration_ms",
                "ttl_duration_ms",
                "arduino_command",
                "iti_s",
                "timestamp"
            ])

    def log_trial(self, trial):

        with open(self.filename, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
            trial.trial_number,
            trial.stimulus,
            trial.stimulus_duration_ms,
            trial.arduino_command,
            trial.iti_s,
            datetime.now().isoformat()
            ])