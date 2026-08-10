"""
main.py

Entry point for the experiment.

Workflow:
1. Generate trial schedule.
2. Connect to Arduino.
3. Run experiment.
4. Close Arduino connection.
"""

from orexin_photometry.experiment.trial_generator import generate_trials

from orexin_photometry.experiment.runner import run_session

from orexin_photometry.hardware.arduino import Arduino

trial_list = generate_trials()

arduino = Arduino("COM10") #change port if needed

run_session(
    trials=trial_list, 
    arduino=arduino
)

arduino.close()

