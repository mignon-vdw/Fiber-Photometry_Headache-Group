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

def _margin(x, frac=0.05):
    """
    Add a small marginaround y-axis limits
    """
    span = np.ptp(signal)

    return (
        np.min(signal) - frac * span
        np.max(signal) + frac * span
    )

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

