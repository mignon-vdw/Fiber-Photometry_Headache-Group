from dataclasses import dataclass

@dataclass
class Trial:
    trial_number: int
    stimulus: str
    duration_ms: int
    iti_s: float
    