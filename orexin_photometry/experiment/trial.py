"""
trial.py

Defines the Trial data structure used throughout the experiment.

Each Trial object represents a single experimental event,
including the stimulus type and timing information.

This abstraction allows trial generation, hardware control,
and logging code to use the same trial definition.

Attributes:
trial_number: int
Unique identifier for the trial.

stimulus: str
Stimulus delivered during the trial.
(e.g. 'light', 'airpuff')

stimulus_duration_ms: int
Duration of the stimulus delivery in milliseconds.

ttl_duration_ms: int
Duration of the TTL generated in milliseconds.

iti_s: float
Inter-trial interval before the next trial.
"""

from dataclasses import dataclass

@dataclass
class Trial:
    trial_number: int
    stimulus: str
    stimulus_duration_ms: int
    ttl_duration_ms: int
    arduino_command: str
    iti_s: float
    