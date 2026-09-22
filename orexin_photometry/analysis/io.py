"""
Responsible for creating and saving/loading the sessions
"""

import os
import json
import numpy as np

from .session import PhotometrySession

#Load pyPhotometry acquisition settings from JSON file
def load_acquisition_settings(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

#Load pyPhotometry CSV and JSON files into a PhotometrySession object
def load_session(csv_path, json_path):
    settings = load_acquisition_settings(json_path)
    
    vpd = settings["volts_per_division"]
    
    if isinstance(vpd, (list, tuple)):
        vpd1, vpd2 = vpd
    else:
        vpd1 = vpd2 = vpd
    
    sampling_rate = settings["sampling_rate"]
    
    raw = np.loadtxt(
        csv_path,
        delimiter=",",
        skiprows=1
        )
    
    analog_1_raw, analog_2_raw, digital_1, digital_2 = raw.T
    
    n_samples = raw.shape[0]
    
    time_ms = np.arange(n_samples) / sampling_rate * 1000
    
    session = PhotometrySession()
    
    session.metadata = {
        "subject_ID": settings.get("subject_ID"),
        "date_time": settings.get("date_time"),
        "sampling_rate": sampling_rate,
        "source_csv": os.path.basename(csv_path),
        "source_json": os.path.basename(json_path)
    }
    
    session.raw = {
        "gcamp": analog_1_raw * vpd1,
        "tdtom": analog_2_raw * vpd2,
        "digital_1": digital_1.astype(bool),
        "digital_2": digital_2.astype(bool),
        "time_ms": time_ms,
        "time_s": time_ms/ 1000
    }

    session.processed = {} #to be added to

    session.events = [] #to be added to

    session.analysis = {} #to be added to
        
    return session

#Generate unique session identifiers
def session_id(session):
    dt= session.metadata['date_time']
    dt = dt.replace(':','').replace('T','-')
    
    return (
        f"sub-{session.metadata['subject_ID']}_{dt}"
    )

#Generate session identifiers including stimulus
def full_session_id(session):
    sid = session_id(session)

    stimulus = session.metadata.get(
        "stimulus",
        "unknown"
    )

    return f"{sid}_stim-{stimulus}"

#Metadata paths 
def _meta_path(session, meta_dir="metadata"):

    os.makedirs(meta_dir, exist_ok=True)

    return os.path.join(meta_dir, f"{session_id(session)}_session_meta.json")

#Metadata management
def get_or_create_session_metadata(session, meta_dir='metadata'):
    """Preprocessing-side: load metadata if present, else prompt and create interactively."""
    
    meta_path = _meta_path(session, meta_dir)

    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        session.metadata.update(meta)
        print(
            f"Loaded metadata for "
            f"{session_id(session)}"
        )
        return session
    
    stimulus = input(
        f"Stimulus type for {session_id(session)}: "
    ).strip()

    meta = {
        "stimulus": stimulus,
        "processing": {
            "lowpass_cutoff_hz": None, 
            "bleach_correction": None,
            "motion_correction": None,
            "dff_method": None,
            "zscore_method": None           
        }
    }

    session.metadata.update(meta)

    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    return session

def load_session_metadata(session, meta_dir='metadata'):
    """Analysis-side: load existing metadata for analysis."""

    meta_path = _meta_path(session, meta_dir)
    if not os.path.exists(meta_path):
        raise FileNotFoundError(
            f"No metadata found for:\n{meta_path} "
            f"Run preprocessing on this session first."
        )
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    session.metadata.update(meta)

    return session

#Save session metadata
def save_session_metadata(session, meta_dir='metadata'):
    os.makedirs(meta_dir, exist_ok=True)

    with open(_meta_path(session, meta_dir), 'w') as f:
        json.dump(session.metadata, f, indent=2)

#Output paths and generation of standard output filenames
def output_path(session, stage, ext, out_dir='output'):
   
   os.makedirs(out_dir, exist_ok=True)

   return os.path.join(
    out_dir,
    f"{full_session_id(session)}_{stage}.{ext}"
   )
    