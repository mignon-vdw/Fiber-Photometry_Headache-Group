"""
main.py

Entry point for the experiment.

Workflow:
1. Generate trial schedule.
2. Connect to Arduino.
3. Run experiment.
4. Close Arduino connection.
"""
from datetime import datetime

from orexin_photometry.experiment.trial_generator import generate_trials

from orexin_photometry.experiment.runner import run_session

from orexin_photometry.hardware.arduino import Arduino

#Create session_specific filenames
timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

filename = f"session{timestamp}.csv"

#Generate trial schedule
trial_list = generate_trials()

#Connect to Arduino
arduino = Arduino("COM10") #change port if needed

#Run experiment
run_session(
    trials=trial_list, 
    arduino=arduino
)

#Close Arduino connection
arduino.close()

