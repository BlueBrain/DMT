"""Parameters to measure phenomena as a function of space."""

from neuro_dmt.measurement.parameter\
    import BrainCircuitSpatialParameter

class SomaDistance(
        BinnedDistance):
    """Distance between soma of two cells,
    in bins."""
    label = "soma_distance"
