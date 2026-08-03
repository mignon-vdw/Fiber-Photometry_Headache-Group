import random

from orexin_photometry.experiment.trial import Trial

def generate_trials():

    stimuli = [
        "airpuff",
        "airpuff",
        "airpuff",
        "light",
        "light",
        "light"
    ]

    random.shuffle(stimuli)

    trials = []

    for i, stimulus in enumerate(stimuli):

        trial = Trial(
            trial_number=i + 1,
            stimulus=stimulus, 
            duration_ms=100,
            iti_s=random.uniform(10,20)
        )

        trials.append(trial)

    return trials