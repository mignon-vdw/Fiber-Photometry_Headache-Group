from dataclasses import dataclass, field

@dataclass
class PhotometrySession:
metadata: dict = field(default_factory=dict)
raw: dict = field(default_factory=dict)
processed: dict = field(default_factory=dict)
events: list = field(default_factory=dict)
analysis: dict = field(default_factory=dict)