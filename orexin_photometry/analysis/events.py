import numpy as np
from collections import Counter
from .io import save_session_metadata

# Classify stimuli from data files based on pulse widths
# Pulse-width -> event-type mapping (ms), specific to your Arduino's TTL protocol.
# Calibrate these against real data before trusting them (see note below).
PULSE_WIDTH_BINS_DIGITAL_1 = {
    'airpuff':   (5, 20),
    'led_flash': (40, 60),
}

def get_pulses(digital_signal, time_ms):
    d = digital_signal.astype(int)
    rising = np.where(np.diff(d) == 1)[0] + 1
    falling = np.where(np.diff(d) == -1)[0] + 1
    if d[0] == 1:
        rising = np.r_[0, rising]
    if d[-1] == 1:
        falling = np.r_[falling, len(d) - 1]
    onset_ms, offset_ms = time_ms[rising], time_ms[falling]
    return onset_ms, offset_ms, offset_ms - onset_ms

def classify_pulses(duration_ms, width_bins):
    return [
        next((name for name, (lo, hi) in width_bins.items() if lo <= dur <= hi), 'unknown')
        for dur in duration_ms
    ]

def extract_events(session):
    onset_1, _, dur_1 = get_pulses(session.raw['digital_1'], session.raw['time_ms'])
    type_1 = classify_pulses(dur_1, PULSE_WIDTH_BINS_DIGITAL_1)
    onset_2, _, dur_2 = get_pulses(session.raw['digital_2'], session.raw['time_ms'])
    type_2 = ['tail_pinch'] * len(onset_2)

    events = (
        [{'time_s': t / 1000, 'type': ty, 'duration_ms': d, 'channel': 'digital_1'}
         for t, ty, d in zip(onset_1, type_1, dur_1)]
        + [{'time_s': t / 1000, 'type': ty, 'duration_ms': d, 'channel': 'digital_2'}
           for t, ty, d in zip(onset_2, type_2, dur_2)]
    )
    events.sort(key=lambda e: e['time_s'])

    n_unknown = sum(e['type'] == 'unknown' for e in events)
    if n_unknown:
        print(f"Warning: {n_unknown} digital_1 pulses matched no width bin.")

    session.events = events

    return session

def add_event_summary_to_metadata(session, meta_dir='metadata'):
    events = session.events
    session.metadata['event_counts'] = dict(Counter(e['type'] for e in events))
    session.metadata['event_order'] = [e['type'] for e in events]
    save_session_metadata(session, meta_dir)
    return session