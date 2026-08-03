from orexin_photometry.experiment.trial_generator import generate_trials

trial_list = generate_trials()

for trial in trial_list:
    print(trial)

