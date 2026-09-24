"""
Run event-alinged analyses for fiber photometry recordings.

Workflow:
1. Load session
2. Load metadata
3. Extract TTL events
4. Run preprocessing
5. Run event analyses
6. Generate PSTHs and heatmaps
7. Save outputs
"""

import os

from orexin_photometry.io import (
    load_session, 
    load_session_metadata,
    session_id
)

from orexin_photometry.event import(
    extract_events
)


from orexin_photometry.preprocessing import (
    lowpass_filtering,
    correct_photobleaching,
    motion_correct,
    calculate_dff,
    calculate_zscore
)

from orexin_photometry.analysis import (
    run_all_event_analyses
)

#Input files

data_folder = "data"

csv_filename = "example_session.csv"
json_filename = csv_filename.replace(
    ".csv",
    ".json"
)

#Load session

session = load_session(
    os.path.join(data_folder, csv_filename),
    os.path.join(data_folder, json_filename)
)

session = load_session_metadata(session)

#Extract TTL events

session = extract_events(session) 

#Preprocessing

session = lowpass_filtering(session)

session = correct_photobleaching(session)

session = motion_correct(session)

session = calculate_dff(session)

session = calculate_zscore(session)

#Event analyses

session = run_all_event_analyses(
    session,
    signal_name = "zscore",
    pre_window = 3, 
    post_window =3, 
    response_window=(0,2),
    baseline_method="zscore",
    baseline_window=(-2,0)
)

#Summary output
print(
    f"\nAnalysis complete:"
    f"{session_id(session)}"
)

print("\nEvent types analysed:")

for event_type in session.analysis.keys():

    print(
        f" - {event_type}: "
        f"{session.analysis[event_type]['n_events']} events"
    )

print("\nStored in session.analysis")