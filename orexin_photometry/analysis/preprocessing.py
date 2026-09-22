"""
Signal preprocessing functions for fiber photometry data

Workflow:
1. Low-pass filter
2. Photobleach correction 
3. Motion correction
4. dF/F calculation
5. Z-score calculation
"""
import numpy as np
from scipy.signal import butter, filtfilt
from scipy.optimize import curve_fit
from scipy.stats import linregress

# Lowpass filter - zero phase filtering (with filtfilt) is used to avoid distorting the signal.
def lowpass_filter(
    session,
    lowpass_cutoff_hz=10,
    order=2
    
    ):

    #Low-pass filter GCaMP and TdTomato signals
    fs = session.metadata["sampling_rate"]
    nyquist = fs/2
    b, a = butter(
        order,
        lowpass_cutoff_hz / nyquist,
        btype="low"
    )   

    gcamp_filtered = filtfilt(
        b,
        a,
        session.raw["gcamp"]
    )

    tdtom_filtered = filtfilt(
        b,
        a,
        session.raw["tdtom"]
    )

    session.processed["gcamp_denoised"] = gcamp_filtered
    session.processed["tdtom_denoised"] = tdtom_filtered

    return session


#Photobleaching correction

def double_exponential(
    t,
    const,
    amp_fast,
    amp_slow,
    tau_fast,
    tau_slow
):

    return (
        const
        + amp_slow * np.exp(-t / tau_slow)
        + amp_fast * np.exp(-t / tau_fast)
    )

def correct_photobleaching(session):

    t = session.raw["time_s"]

    for signal_name in [
        "gcamp_denoised",
        "tdtom_denoised"
    ]:

        signal = session.processed[signal_name]

        p0 = [
            np.median(signal),
            np.max(signal) * 0.1, 
            np.max(signal) * 0.9, 
            100,
            1000
        ]

    params, _ = curve_fit(
        double_exponential,
        t,
        signal,
        p0=p0,
        maxfev=10000
    )

    fit = double_exponential(
        t,
        *params
    )

    corrected = signal - fit

    session.processed[f"{signal_name}_bleach_fit"] = fit
    session.processed[f"{signal_name}_bleach_corrected"] = corrected

    return session

#Remove motion-related fluctuations using TdTomato regression
def motion_correct(session):
    gcamp = session.processed[
        "gcamp_denoised_bleach_corrected"
    ]

    tdtom = session.processed[
        "tdtom_denoised_bleach_corrected"
    ]

    slope, intercept, _, _, _ = linregress(
        tdtom,
        gcamp
    )

    fitted_motion = (
        intercept
        + slope * tdtom
    )

    motion_corrected = (
        gcamp
        - fitted_motion
    )

    session.processed["motion_fit"] = fitted_motion
    session.processed["motion_corrected"] = motion_corrected

    return session

#Calculate dF/F
def calculate_dff(session):
    signal = session.processed["motion_corrected"]

    baseline = np.percentile(
        signal,
        50
    )

    dff = (
        (signal - baseline)
        / baseline
    ) * 100

    session.processed["dff"] = dff

    return session

#Calculate session wide z-score
def calculate_zscore(session):

    dff = session.processed["dff"]

    zscore = (
        dff - np.mean(dff)
    ) / np.std(dff)

    session.processed["zscore"] = zscore

    return session

