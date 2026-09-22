import numpy as np

def _margin(x, frac=0.05):
    lo, hi = np.min(x), np.max(x)
    pad = (hi - lo) * frac
    return lo - pad, hi + pad

    GCaMP8s_raw = session.raw["gcamp"]
TdTom_raw = session.raw["tdtom"]
time_seconds = session.raw["time_s"]
sampling_rate = session.metadata["sampling_rate"]

#set default plot properties
plt.rcParams['figure.figsize'] = [14, 12] # Make default figure size larger.
plt.rcParams['axes.xmargin'] = 0          # Make default margin on x axis zero.
plt.rcParams['axes.labelsize'] = 12     #Set default axes label size 
plt.rcParams['axes.titlesize']=15
plt.rcParams['axes.titleweight']='heavy'
plt.rcParams['ytick.labelsize']= 10
plt.rcParams['xtick.labelsize']= 10
plt.rcParams['legend.fontsize']=12
plt.rcParams['legend.markerscale']=2

#Plot raw signals 
fig,ax1=plt.subplots()  # create a plot to allow for dual y-axes plotting
plot1=ax1.plot(time_seconds, GCaMP8s_raw, 'g', label='GCaMP8s') #plot GCaMP8s on left y-axis
ax2=ax1.twinx()# create a right y-axis, sharing x-axis on the same plot
plot2=ax2.plot(time_seconds, TdTom_raw, 'r', label='TdTomato') # plot TdTomato on right y-axis

# Plot event times as ticks.
ax1.set_ylim(*_margin(GCaMP8s_raw))
ax2.set_ylim(*_margin(TdTom_raw))

event_colors = {'airpuff': 'tab:orange', 'led_flash': 'tab:blue', 'tail_pinch': 'tab:purple', 'unknown': 'gray'}
tick_y = ax1.get_ylim()[1] - 0.05 * np.ptp(ax1.get_ylim())

event_lines = []
for ev_type in sorted(set(e['type'] for e in session.events)):
    times = [e['time_s'] for e in session.events if e['type'] == ev_type]
    event_lines += ax1.plot(times, np.full(len(times), tick_y), label=ev_type,
                             color=event_colors.get(ev_type, 'k'), marker='|', linestyle='None')

ax1.set_xlabel('Time (seconds)')
ax1.set_ylabel('GCaMP8s Signal (V)', color='g')
ax2.set_ylabel('TdTomato Signal (V)', color='r')
ax1.set_title(f"Raw signals — {session_id(session)}")

lines = plot1 + plot2 +event_lines #line handle for legend
labels = [l.get_label() for l in lines]  #get legend labels
ax1.legend(lines, labels, loc='upper right', bbox_to_anchor=(0.98, 0.93))
fig.savefig(output_path(session, 'raw_signals', 'png'))

~~~~~~~
"""
Plotting functions for fiber photometry preprocessing.
 
Functions
---------
plot_raw_signals()
plot_denoised_signals()
plot_bleach_correction()
plot_motion_correction()
plot_normalised_signals()
"""
 
import numpy as np
import matplotlib.pyplot as plt

def _margin(signal, frac=0.05):
"""
Add a small margin around y-axis limits.
"""
 
span = np.ptp(signal)
 
return (
np.min(signal) - frac * span,
np.max(signal) + frac * span
)

def plot_raw_signals(session):
 
time = session.raw["time_s"]
 
gcamp = session.raw["gcamp"]
 
tdtom = session.raw["tdtom"]
 
fig, ax1 = plt.subplots()
 
line1 = ax1.plot(
time,
gcamp,
color="green",
label="GCaMP8s"
)
 
ax2 = ax1.twinx()
 
line2 = ax2.plot(
time,
tdtom,
color="red",
label="tdTomato"
)
 
ax1.set_ylim(*_margin(gcamp))
ax2.set_ylim(*_margin(tdtom))
 
event_lines = []
 
event_colors = {
"airpuff": "tab:orange",
"led_flash": "tab:blue",
"tail_pinch": "tab:purple",
"unknown": "gray"
}
 
tick_y = (
ax1.get_ylim()[1]
- 0.05 * np.ptp(ax1.get_ylim())
)
 
for ev_type in sorted(
set(e["type"] for e in session.events)
):
 
times = [
e["time_s"]
for e in session.events
if e["type"] == ev_type
]
 
event_lines += ax1.plot(
times,
np.full(len(times), tick_y),
marker="|",
linestyle="None",
color=event_colors.get(
ev_type,
"black"
),
label=ev_type
)
 
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("GCaMP8s (V)")
ax2.set_ylabel("tdTomato (V)")
 
ax1.set_title("Raw Photometry Signals")
 
lines = line1 + line2 + event_lines
 
labels = [
l.get_label()
for l in lines
]
 
ax1.legend(lines, labels)
 
fig.tight_layout()
 
return fig
def plot_denoised_signals(session):
 
time = session.raw["time_s"]
 
gcamp = session.processed[
"gcamp_denoised"
]
 
tdtom = session.processed[
"tdtom_denoised"
]
 
fig, axes = plt.subplots(
2,
1,
sharex=True
)
 
axes[0].plot(
time,
gcamp,
color="green"
)
 
axes[0].set_ylabel(
"GCaMP8s"
)
 
axes[0].set_title(
"Low-pass Filtered GCaMP"
)
 
axes[1].plot(
time,
tdtom,
color="red"
)
 
axes[1].set_ylabel(
"tdTomato"
)
 
axes[1].set_title(
"Low-pass Filtered tdTomato"
)
 
axes[1].set_xlabel(
"Time (s)"
)
 
fig.tight_layout()
 
return fig

def plot_bleach_correction(session):
 
time = session.raw["time_s"]
 
fig, axes = plt.subplots(
2,
1,
figsize=(14, 10)
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
session.processed[
"gcamp_denoised_bleach_fit"
],
color="black",
label="Double exponential fit"
)
 
axes[0].plot(
time,
session.processed[
"gcamp_denoised_bleach_corrected"
],
color="blue",
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
session.processed[
"tdtom_denoised_bleach_fit"
],
color="black",
label="Double exponential fit"
)
 
axes[1].plot(
time,
session.processed[
"tdtom_denoised_bleach_corrected"
],
color="blue",
label="Corrected"
)
 
axes[1].legend()
 
axes[1].set_title(
"tdTomato Bleaching Correction"
)
 
axes[1].set_xlabel(
"Time (s)"
)
 
fig.tight_layout()
 
return fig

def plot_motion_correction(session):
 
time = session.raw["time_s"]
 
fig, axes = plt.subplots(
2,
1,
figsize=(14, 10)
)
 
axes[0].plot(
time,
session.processed[
"gcamp_denoised_bleach_corrected"
],
label="GCaMP"
)
 
axes[0].plot(
time,
session.processed[
"motion_fit"
],
label="Motion fit"
)
 
axes[0].legend()
 
axes[0].set_title(
"Motion Regression"
)
 
axes[1].plot(
time,
session.processed[
"motion_corrected"
],
color="blue"
)
 
axes[1].set_title(
"Motion Corrected Signal"
)
 
axes[1].set_xlabel(
"Time (s)"
)
 
fig.tight_layout()
 
return fig
def plot_normalised_signals(session):
 
time = session.raw["time_s"]
 
dff = session.processed["dff"]
 
zscore = session.processed["zscore"]
 
fig, axes = plt.subplots(
2,
1,
sharex=True,
figsize=(14, 10)
)
 
axes[0].plot(
time,
dff,
color="green"
)
 
axes[0].set_ylabel(
"dF/F (%)"
)
 
axes[0].set_title(
"Normalised dF/F"
)
 
axes[1].plot(
time,
zscore,
color="blue"
)
 
axes[1].set_ylabel(
"Z-score"
)
 
axes[1].set_xlabel(
"Time (s)"
)
 
axes[1].set_title(
"Session-wide Z-score"
)
 
fig.tight_layout()
 
return fig