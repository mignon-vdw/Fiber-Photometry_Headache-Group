"""
Plotting functions for fiber photometry preprocessing and 
event-aligned analyses.

Functions:
plot_raw_signals()
plot_denoised_signals()
plot_bleach_correction()
plot_motion_correction()
plot_normalised_signals()
plot_psth()
plot_heatmap()
"""

import numpy as np
import matplotlib.pyplot as plt
from orexin_photometry.io import session_id

def _margin(signal, frac=0.05):
    """
    Add a small margin around y-axis limits
    """
    span = np.ptp(signal)

    return (
        np.min(signal) - frac * span,
        np.max(signal) + frac * span
    )

#Plot raw signals

def plot_raw_signals(session):

    time = session.raw["time_s"]

    gcamp = session.raw["gcamp"]

    tdtom = session.raw["tdtom"]

    fig,ax1=plt.subplots(
        figsize=(14,8)
    ) # create a plot to allow for dual y-axes plotting

    line1 = ax1.plot(
        time, 
        gcamp, 
        color="green", 
        label='GCaMP8s'
    ) #plot GCaMP8s on left y-axis

    ax2=ax1.twinx()# create a right y-axis, sharing x-axis on the same plot

    line2 = ax2.plot(
        time, 
        tdtom, 
        color="red", 
        label='TdTomato'
    ) #plot TdTomato on right y-axis

    # Plot event times as ticks.
    ax1.set_ylim(*_margin(gcamp))
    ax2.set_ylim(*_margin(tdtom))

    event_lines = []

    event_colours = {
        "airpuff": "tab:orange",
        "led_flash": "tab:blue",
        "tail_pinch": "tab:purple",
        "unknown": "gray"
    }

    tick_y = (
        ax1.get_ylim()[1]
        -0.05 * np.ptp(ax1.get_ylim())
    )

    for event_type in sorted(
        set(e["type"] for e in session.events)
    ):

        times = [
            e["time_s"]
            for e in session.events
            if e["type"] == event_type
        ]

        event_lines += ax1.plot(
            times, 
            np.full(len(times), tick_y), 
            label=event_type,
            color=event_colours.get(event_type, 'black'),
            marker='|', 
            linestyle='None'
        )

    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('GCaMP8s Signal (V)', color='g')
    ax2.set_ylabel('TdTomato Signal (V)', color='r')

    ax1.set_title(f"Raw signals — {session_id(session)}")

    lines = line1 + line2 +event_lines #line handle for legend
    labels = [line.get_label() for line in lines]  #get legend labels
    ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(0.98, 0.93))

    fig.tight_layout()

    return fig
    
#Plot denoised signals 
def plot_denoised_signals(session):

    time = session.raw["time_s"]

    fig, axes = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(14,8)
    )

    axes[0].plot(
        time,
        session.processed["gcamp_denoised"],
        color="green"
    )

    axes[0].set_title(
        "Low-pass Filtered GCaMP"
    )

    axes[0].set_ylabel(
        "GCaMP"
    )

    axes[1].plot(
        time, 
        session.processed["tdtom_denoised"],
        color="red"
    )

    axes[1].set_title(
        "Low-pass Filtered TdTomato"
    )

    axes[1].set_ylabel(
        "TdTomato"
    )

    axes[1].set_xlabel(
        "Time (s)"
    )

    fig.tight_layout()

    return fig

#Plot bleaching correction
def plot_bleach_correction(session):

    time = session.raw["time_s"]

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(14,10)
    )

    axes[0].plot(
        time,
        session.processed["gcamp_denoised"],
        color="green",
        alpha=0.5,
        label="Signal"
    )

    axes[0].plot(
        time,
        session.processed["gcamp_denoised_bleach_fit"],
        label="Double Exp Fit"
    )

    axes[0].plot(
        time,
        session.processed["gcamp_denoised_bleach_corrected"],
        label="Corrected"
    )

    axes[0].legend()

    axes[0].set_title(
        "GCaMP Bleaching Correction"
    )

    axes[1].plot(
        time,
        session.processed["tdtom_denoised"],
        color="red",
        alpha=0.5,
        label="Signal"
    )

    axes[1].plot(
        time,
        session.processed["tdtom_denoised_bleach_fit"],
        label="Double Exp Fit"
    )

    axes[1].plot(
        time,
        session.processed["tdtom_denoised_bleach_corrected"],
        label="Corrected"
    )

    axes[1].legend()

    axes[1].set_title(
        "TdTomato Bleaching Correction"
    )

    axes[1].set_xlabel(
        "Time (s)"
    )

    fig.tight_layout()

    return fig

#Plot motion-corrected signals

def plot_motion_correction(session):

    time = session.raw["time_s"]

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(14,10)
    )

    axes[0].plot(
        time,
        session.processed["gcamp_denoised_bleach_corrected"],
        label="GCaMP"
    )

    axes[0].plot(
        time,
        session.processed["motion_fit"],
        label="Motion Fit"
    )

    axes[0].legend()

    axes[0].set_title(
        "Motion Regression"
    )

    axes[1].plot(
        time,
        session.processed["motion_corrected"],
        color="blue"
    )

    axes[1].set_title(
        "Motion Corrected Signal"
    )

    fig.tight_layout()

    return fig

#Normalised signals

def plot_normalised_signals(session):

    time = session.raw["time_s"]

    fig, axes = plt.subplots(
        2,
        1,
        sharex=True,
        figsize=(14,10)
    )

    axes[0].plot(
        time,
        session.processed["dff"],
        color="green"
    )

    axes[0].set_title("dF/F")

    axes[0].set_ylabel(
        "dF/F (%)"
    )

     axes[1].plot(
        time,
        session.processed["zscore"],
        color="blue"
    )

    axes[1].set_title("Session-wide Z-score")

    axes[1].set_ylabel(
        "Z-score"
    )

    axes[1].set_xlabel(
        "Time (s)"
    )

    fig.tight_layout()

    return fig

#Plot event-aligned PSTH

def plot_psth(
    session,
    event_type
):

    result = session.analysis[
        event_type
    ]

    time_axis = result[
        "time_axis"
    ]

    mean_trace = result[
        "mean_trace"
    ]

    sem_trace = result[
        "sem_trace"
    ]

    fig, ax = plt.subplots(
        figsize=(8,5)
    )

    ax.plot(
        time_axis,
        mean_trace,
        color="black",
        linewidth=2
    )

    ax.fill_between(
        time_axis,
        mean_trace - sem_trace,
        mean_trace + sem_trace,
        alpha=0.3,
        color="gray"
    )

    ax.axvline(
        0,
        color="red",
        linestyle="--"
    )

    ax.set_xlabel(
        "Time from event (s)"
    )

    ax.set_ylabel(
        result["signal_used"]
    )

    ax.set_title(
        f"PSTH: {event_type}\n"
        f"{session_id(session)}"
    )

    fig.tight_layout()

    return fig

#Plot event-aligned heatmap

def plot_heatmap(
    session,
    event_type
):

    result = session.analysis[
        event_type
    ]

    traces = result[
        "trace_matrix"
    ]

    time_axis = result[
        "time_axis"
    ]

    fig, ax = plt.subplots(
        figsize=(8,6)
    )

    image = ax.imshow(
        traces, 
        aspect = "auto",
        origin="lower",
        extent=[
            time_axis[0],
            time_axis[-1],
            0,
            traces.shape[0]
        ],
        cmap="viridis"
    )

    ax.axvline(
        0,
        color="white",
        linestyle="--",
        linewidth=1
    )

    ax.set_xlabel(
        "Time from event (s)"
    )

    ax.set_ylabel(
        "Event Number"
    )

    ax.set_title(
        f"Heatmap: {event_type}\n"
        f"{session_id(session)}"
    )

    cbar = fig.colorbar(
        image,
        ax=ax
    )

    cbar.set_label(
        result["signal_used"]
    )

    fig.tight_layout()

    return fig