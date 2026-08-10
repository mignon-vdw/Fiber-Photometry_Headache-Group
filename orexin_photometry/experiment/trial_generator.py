"""
trial.generator.py

Creates pseudorandomised trial sequences for fiber photometry sessions.

The output is a list of Trial objects that can later be used by the 
experiment runner.
"""

import random

from orexin_photometry.experiment.trial import Trial

#Generates a list of pseudorandomised trials
def generate_trials():

    #Define available stimuli
    stimuli = [
        "airpuff",
        "airpuff",
        "airpuff",
        "light",
        "light",
        "light"
    ]

    #Randomise stimulus order
    random.shuffle(stimuli)

    trials = []

    #Converts stimulus names into Trial objects
    for i, stimulus in enumerate(stimuli):

        trial = Trial(
            trial_number=i + 1,
            stimulus=stimulus, 
            stimulus_duration_ms=100,
            iti_s=random.uniform(10,20)
        )

        trials.append(trial)

    return trials