from dataclasses import dataclass


@dataclass
class RouteSummary:
    origin: str
    destination: str
    distance_km: float
