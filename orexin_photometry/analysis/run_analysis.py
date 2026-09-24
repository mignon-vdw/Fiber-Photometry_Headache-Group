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

import os

from orexin_photometry.io import ()

session = load_session()

session = load_session_metadata(session)

session = extract_events(session)

session = run_all_event_analyses(
    session,
    signal_name = "zscore",
    pre_window = 3, 
    post_window =3
)