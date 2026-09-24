"""
Event-aligned analyses for fiber photometry data

Workflow:
1. Peri-event trace extraction
2. PSTH calculation
3. Area under the curve (AUC) calculation
4. Peak response analysis
5. Response latency analysis

Results are stored in session.analysis[event_type]
"""

import numpy as np
from scipy.stats import sem 


def get_signal(
    session,
    signal_name="zscore" #can also be "dff" pr "motion_corrected"
):
    """
    Retrieve a signal from session.processed
    Parameters
    -----
    session: PhotometrySession
    signal_name: str (#name of signal to extract)

    Returns
    -----
    np.ndarray (#requested signal)
    """

    if signal_name not in session.processed:
        raise ValueError(
            f"Signal '{signal_name}' not found."
        )

    return session.processed[signal_name]

def extract_perievent_traces(
    session,
    event_type,
    signal_name="zscore",
    pre_window=3,
    post_window=3, 
    baseline_method="subtract",
    baseline_window=(-2,0)
):

    """
    Extract fixed windows around every event.
    Parameters
    -----
    session: PhotometrySession
    event_type: str
    signal_name: str
    pre_window: float (#seconds before event)
    post_window: float (#seconds after event)
    baseline_method: str (#non, "subtract" or "zscore")
    baseline_window: tuple (#baseline period used for normalisation)

    Returns
    -----
    dict
    """

    signal = get_signal(session, signal_name)

    fs = session.metadata["sampling_rate"]

    time_s = session.raw["time_s"]

    samples_before = int(pre_window * fs)
    samples_after = int(post_window * fs)

    n_samples = samples_before + samples_after

    selected_events = [
        event
        for event in session.events
        if event["type"] == event_type
    ]

    trace_list = [] 
    excluded_events = 0

    time_axis = np.linspace(
        -pre_window,
        post_window,
        n_samples,
        endpoint=False
    )

    baseline_mask = (
        (time_axis >= baseline_window[0]) &
        (time_axis < baseline_window[1])
    )

    for event in selected_events:

        event_time = event["time_s"]

        event_times_used = []

        event_times_used.append(event_time)

        center_idx = np.argmin(
            np.abs(time_s - event_time)
        )

        start_idx = center_idx - samples_before
        end_idx = center_idx + samples_after

        if start_idx < 0:
            excluded_events += 1
            continue
         
        if end_idx >= len(signal):
            excluded_events += 1
            continue

        trace = signal[start_idx:end_idx]

        if len(trace) != n_samples:
            excluded_events += 1
            continue 

        baseline_data = trace[baseline_mask]

        baseline_mean = np.mean(baseline_data)

        baseline_std = np.std(baseline_data)

        if baseline_method is None:
            pass

        elif baseline_method == "subtract":

            trace = trace - baseline_mean

        elif baseline_method == "zscore":

            if baseline_std == 0:
                excluded_events += 1
                continue

            trace = (
                trace - baseline_mean
            ) / baseline_std

        else:

            raise ValueError(
                f"Unknown baseline method: "
                f"{baseline_method}"
            )
            
        trace_list.append(trace)
    
    if len(trace_list) == 0:
        raise ValueError(
            f"No valid peri-event traces found for {event_type}"
        )
    
    trace_matrix = np.vstack(trace_list)

    return {
        "trace_matrix": trace_matrix,
        "time_axis": time_axis,
        "n_events": len(trace_list),
        "n_events_excluded": excluded_events
        "event_times": event_times_used
    }

def calculate_psth(
    trace_matrix
):

    """
    Calculate trial mean and SEM
    """

    mean_trace = np.nanmean(
        trace_matrix,
        axis=0
    )

    sem_trace = sem(
        trace_matrix,
        axis=0,
        nan_policy="omit"
    )

    return {
        "mean_trace": mean_trace,
        "sem_trace": sem_trace
    }

def calculate_auc(
    trace_matrix,
    time_axis,
    response_window=(0,2)
):

    """
    Calculate area under the curve in post-event response window
    """

    mask = (
        (time_axis >= response_window[0]) &
        (time_axis <= response_window[1])
    )
    
    auc_per_trial = np.trapz(
        trace_matrix[:, mask],
        x=time_axis[mask],
        axis=1
    )
    

    return {
        "auc_per_trial": auc_per_trial,
        "mean_auc": np.mean(auc_per_trial),
        "sem_auc": sem(auc_per_trial)
    }

def calculate_peak_response(
    trace_matrix,
    time_axis,
    response_window=(0,2)
):

    """
    Calculate peak amplitude and timing
    """

    mask = (
        (time_axis >= response_window[0]) &
        (time_axis <= response_window[1])
    )

    window_traces = trace_matrix[:, mask]
    window_time = time_axis[mask]

    peak_values = []
    peak_times = []

    for trial in window_traces:

        peak_idx = np.argmax(trial)

        peak_values.append(
            trial[peak_idx]
        )

        peak_times.append(
            window_time[peak_idx]
        )
    
    peak_values = np.asarray(peak_values)
    peak_times = np.asarray(peak_times)
 
    return {
        "peak_values": peak_values,
        "peak_times": peak_times,
        "mean_peak": np.mean(peak_values),
        "mean_peak_time": np.mean(peak_times)
    }

def calculate_response_latency(
    trace_matrix,
    time_axis,
    threshold_std=2
):

    """
    Calculate latency to threhold crossing

    Threshold:
    baseline mean + threshold_std * baseline_std
    """

    baseline_mask = time_axis < 0
    response_mask = time_axis >= 0

    latencies = []

    for trial in trace_matrix:
        baseline = trial[baseline_mask]

        baseline_mean = np.mean(baseline)
        baseline_std = np.std(baseline)

        threshold = (
            baseline_mean +
            (threshold_std * baseline_std)
        )

        response_signal = trial[response_mask]
        response_time = time_axis[response_mask]

        crossings = np.where(
            response_signal > threshold
        ) [0]

        if len(crossings) == 0:
            latencies.append(np.nan)
        else: 
            latencies.append(
                response_time[crossings[0]]
            )
    
    latencies = np.asarray(latencies)

    return {
        "latencies": latencies,
        "mean_latency": np.nanmean(latencies) 
    }

def run_event_analysis(
    session,
    event_type,
    signal_name="zscore",
    pre_window=3,
    post_window=3,
    response_window=(0,2),
    baseline_method="subtract",
    baseline_window=(-2,0)
):

    """
    Run complete analysis for one event type
    """

    extracted = extract_perievent_traces(
        session = session,
        event_type = event_type,
        signal_name = signal_name,
        pre_window = pre_window,
        post_window = post_window,
        baseline_method = baseline_method,
        baseline_window = baseline_window
    )

    trace_matrix = extracted["trace_matrix"]
    time_axis = extracted["time_axis"]

    psth = calculate_psth(trace_matrix)

    auc = calculate_auc(
        trace_matrix,
        time_axis,
        response_window
    )

    peaks = calculate_peak_response(
        trace_matrix,
        time_axis,
        response_window
    )

    latency = calculate_response_latency(
        trace_matrix,
        time_axis,
    )

    session.analysis[event_type] = {

        "signal_used": signal_name,

        "n_events": extracted["n_events"],

        "time_axis": time_axis,

        "trace_matrix": trace_matrix,

        "mean_trace": psth["mean_trace"],

        "sem_trace": psth["sem_trace"],

        "auc_per_trial": auc["auc_per_trial"],

        "mean_auc": auc["mean_auc"],

        "sem_auc": auc["sem_auc"],

        "peak_values": peaks["peak_values"],

        "peak_times": peaks["peak_times"],

        "mean_peak": peaks["mean_peak"],

        "mean_peak_time": peaks["mean_peak_time"],

        "latencies": latency["latencies"],

        "mean_latency": latency["mean_latency"],

        "baseline_method": baseline_method,

        "baseline_window_s": baseline_window,

        "n_events_excluded": extracted["n_events_excluded"],

        "event_times": extracted["event_times"]
    }

    return session

def run_all_event_analyses(
    session,
    signal_name="zscore",
    pre_window=3,
    post_window=3,
    response_window=(0,2),
    baseline_method="subtract",
    baseline_window=(-2,0)
):

    """
    Analyse every event type present in session.events 
    """   

    event_types = sorted(
        set(
            event["type"]
            for event in session.events
        )
    )

    for event_type in event_types:

        session = run_event_analysis(
            session = session,
            event_type = event_type,
            signal_name = signal_name,
            pre_window = pre_window,
            post_window = post_window,
            response_window = response_window,
            baseline_method = baseline_method,
            baseline_window = baseline_window
        )

    session.metadata.setdefault(
        "analysis", {}
    )

    session.metadata["analysis"].update({

        "signal_used": signal_name,

        "pre_window_s": pre_window,

        "post_window_s": post_window,

        "response_window_s": response_window,

        "baseline_method": baseline_method,

        "baseline_window_s": baseline_window
    })

    return session