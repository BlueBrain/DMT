"""Measurement of cell density."""

from dmt.vtk.measurement import Measurement
from neuro_dmt.phenomoena.circuit.composition \
    import CellDensity as CellDensityPhenomenon

class CellDensityMeasurement(Measurement):
    """Measurement of Cell Density in a brain region."""

