"""
This script runs preprocessing of fiber photometry data recorded using pyPhotometry
Preprocessing consists of the following steps:
1. Load photometry session
2. Load/create metadata
3. Extract TTL events
4. Add event summary to metadata
5. Run preprocessing
6. Generate quality control figures
7. Save outputs
"""

import os
import numpy as  np
import matplotlib.pyplot as plt

from orexin_photometry.io import (
    load_session,
    get_or_create_session_metadata,
    session_id,
    output_path
    save_session_metadata
)

from orexin_photometry.events import (
    extract_events, 
    add_event_summary_to_metadata,)

from orexin_photometry.preprocessing import (
    lowpass_filter,
    correct_photobleaching,
    motion_correct,
    calculate_dff,
    calculate_zscore
)

from orexin_photometry.plotting import (
    plot_raw_signals,
    plot_denoised_signals,
    plot_bleach_correction,
    plot_motion_correction,
    plot_normalised_signals,
)

#Input files
data_folder = "data"
csv_filename = ".csv" #need to replace with a filename!!!!
json_filename = csv_filename.replace(
    ".csv",
    ".json"
)

#Load session
session = load_session(
    os.path.join(data_folder, csv_filename),
    os.path.join(data_folder, json_filename),
)

session = get_or_create_session_metadata(session)

#Extract TTL events
session = extract_events(session)

session = add_event_summary_to_metadata(session)

#Preprocessing
session = lowpass_filter(session)

session = correct_photobleaching(session)

session = motion_correct(session)

session = calculate_dff (session)

session = calculate_zscore(session)

#Save metadata after processing

session.metadata["processing"] = {
    "lowpass_filter": 10,

    "filter_order": 2,

    "photobleaching_correction": "double_exponential",

    "motion_correction": "linear_regression",

    "dff_method": "median_baseline",

    "zscore_method": "session"
}

save_session_metadata(session)

#Quality control figures 

fig = plot_raw_signals(session)

fig.savefig(
    output_path(
        session,
        "raw_signals",
        "png"
    )
)

plt.close(fig)

fig = plot_denoised_signals(session)

fig.savefig(
    output_path(
        session,
        "denoised_signals",
        "png"
    )
)

plt.close(fig)

fig = plot_bleach_correction(session)

fig.savefig(
    output_path(
        session,
        "bleach_correction",
        "png"
    )
)

plt.close(fig)

fig = plot_motion_correction(session)

fig.savefig(
    output_path(
        session,
        "motion_correction",
        "png"
    )
)

plt.close(fig)

fig = plot_normalised_signals(session)

fig.savefig(
    output_path(
        session,
        "normalised_signals",
        "png"
    )
)

plt.close(fig)

print(
    f"Preprocessing complete: "
    f"{session_id(session)}"
)

