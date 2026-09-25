"""
Complete fiber photometry processing pipeline

Workflow:
1. Load session
2. Create/Load metadata
3. Extract TTL events
4. Add event summary to metadata
5. Run preprocessing
6. Save preprocessing metadata
7. Generate QC figures
8. Run event analyses
9. Generate PSTHs and heatmaps
10. Save outputs
"""

import os
import numpy as  np
import matplotlib.pyplot as plt
import argparse

from orexin_photometry.io import (
    load_session,
    get_or_create_session_metadata,
    session_id,
    output_path,
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

from orexin_photometry.analysis import (
    run_all_event_analyses
)

from orexin_photometry.plotting import (
    plot_raw_signals,
    plot_denoised_signals,
    plot_bleach_correction,
    plot_motion_correction,
    plot_normalised_signals,
    plot_psth,
    plot_heatmap
)

#Command line arguments for input files

parser = argparse.ArgumentParser(
    description=(
        "Run complete fiber photometry"
        "processing and analysis pipeline"
    )
)

parser.add_argument(
    "--csv",
    required=True,
    help="Path to pyPhotometry .csv file"
)

parser.add_argument(
    "--json",
    required=True,
    help="Path to pyPhotometry .json file"
)

parser.add_argument(
    "--meta",
    default="metadata",
    help="Metadata directory"
)

parser.add_argument(
    "--out",
    default="output",
    help="Output directory"
)

parser.add_argument(
    "--signal",
    default="zscore",
    choices=[
        "zscore",
        "dff",
        "motion_corrected"
    ]
)

parser.add_argument(
    "--pre",
    type=float,
    default=3
)

parser.add_argument(
    "--post",
    type=float,
    default=3
)

args = parser.parse_args()

csv_path = args.csv
json_path = args.json
meta_dir = args.meta
output_dir = args.out
signal_name = args.signal
pre_window = args.pre
post_window = args.post

#Load session

session = load_session(
    csv_path,
    json_path
)

session = get_or_create_session_metadata(
    session,
    meta_dir=meta_dir
    )

#Extract TTL events

session = extract_events(session)

session = add_event_summary_to_metadata(
    session,
    meta_dir=meta_dir
    )

#Preprocessing

session = lowpass_filter(
    session,
    lowpass_cutoff_hz=10,
    order=2
    )

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

save_session_metadata(
    session, 
    meta_dir=meta_dir
    )

#Quality control figures 

fig = plot_raw_signals(session)

fig.savefig(
    output_path(
        session,
        "raw_signals",
        "png",
        out_dir=output_dir
    )
)

plt.close(fig)

fig = plot_denoised_signals(session)

fig.savefig(
    output_path(
        session,
        "denoised_signals",
        "png",
        out_dir=output_dir
    )
)

plt.close(fig)

fig = plot_bleach_correction(session)

fig.savefig(
    output_path(
        session,
        "bleach_correction",
        "png",
        out_dir=output_dir
    )
)

plt.close(fig)

fig = plot_motion_correction(session)

fig.savefig(
    output_path(
        session,
        "motion_correction",
        "png",
        out_dir=output_dir
    )
)

plt.close(fig)

fig = plot_normalised_signals(session)

fig.savefig(
    output_path(
        session,
        "normalised_signals",
        "png",
        out_dir=output_dir
    )
)

plt.close(fig)

#Event analyses

session = run_all_event_analyses(
    session,
    signal_name = signal_name,
    pre_window = pre_window, 
    post_window = post_window, 
    response_window=(0,2),
    baseline_method="zscore",
    baseline_window=(-2,0)
)

#Plot PSTH/Heatmap figures

for event_type in session.analysis.keys():

    fig = plot_psth(
        session, 
        event_type
    )

    fig.savefig(
        output_path(
            session,
            f"{event_type}_psth",
            "png",
            out_dir=output_dir
        )
    )

    plt.close(fig)

    fig = plot_heatmap(
        session,
        event_type
    )

    fig.savefig(
        output_path(
            session,
            f"{event_type}_heatmap",
            "png",
            out_dir=output_dir
        )
    )

    plt.close(fig)

#Summary

#Summary output
print(
    f"\nPipeline complete:"
    f"{session_id(session)}"
)

print("\nEvent types analysed:")

for event_type in session.analysis.keys():

    print(
        f" - {event_type}: "
        f"{session.analysis[event_type]['n_events']} events"
    )

print("\nResults stored in session.analysis")
    





