from dataclasses import dataclass, field

@dataclass
class PhotometrySession:
metadata: dict
raw: dict
processed: dict
events: list
analysis: dict