"""Circuit composition measurements for Blue Brain circuits."""

from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon

class CellDensityMeasurement(measurement.Method):
    """test cell density measurement to test Measurement!"""

    def __init__(self, circuit):
        """A scale for cell densities."""
        self.__circuit = circuit

    label = "cell_density"
    phenomenon = Phenomenon("cell_density", "Number of cells in a unit volume")

    def __call__(self, roi):
        """Random cell density"""
        return 1.e-3 * self.__circuit.stats.cell_density(roi)


class CellRatioMeasurement(measurement.Method):
    pass

class InhibitorySynapseRatioMeasurement(measurement.Method):
    pass

class SynapseDensityMeasurement(measurement.Method):
    pass
