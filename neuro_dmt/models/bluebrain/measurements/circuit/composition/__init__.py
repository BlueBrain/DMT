"""Circuit composition measurements for Blue Brain circuits."""

from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.models.bluebrain import BlueBrainModelHelper

class CellDensityMeasurement(measurement.StatisticalMethod):
    """..."""
    

    label = "in-silico"
    phenomenon = Phenomenon("cell_density", "Number of cells in a unit volume")

    def __call__(self, circuit):
        return 1.e-3 * circuit.stats.cell_density(roi)

    def __call__(self, roi):
        """Number of cells in a unit volume, [1000/mm^3]"""
        return 1.e-3 * self.__circuit.stats.cell_density(roi)


class CellRatioMeasurement(measurement.Method):
    """..."""

    label = "in-silico"
    phenomenon = Phenomenon("cell_ratio",
                            "Fraction of inhibitory cells in the circuit.")

    def __init__(self, circuit):
        """..."""
        self.__circuit = circuit
        self.__helper  = BlueBrainModelHelper(circuit=circuit)

    def __call__(self, roi):
        """Ratio of the number of inhibitory cells to
        the number of excitatory cells in a region of interest (roi)
        of the circuit.
        """
        ccounts = self.__helper.cell_counts(roi)
        return (1.0 + ccounts['INH']) / (1.0 + ccounts['TOT'])

    
class InhibitorySynapseDensityMeasurement(measurement.Method):
    """..."""

    label = "in-silico"
    phenomenon = Phenomenon("inhibitor_synapse_density",
                            "Number of inhibitory synapses in a unit volume")

    def __init__(self, circuit):
        """..."""
        self.__circuit = circuit
        self.__helper  = BlueBrainModelHelper(circuit = circuit)

    def __call__(self, roi):
        """Count the number of inhibitory synapses within a
        region of interest (roi), and divides the number by the roi's volume.
        """
        return self.__helper.synapse_density(roi, scale_factor=1.e-9)["INH"]


class ExtrinsicIntrinsicSynapseDensityMeasurement(measurement.Method):
    """..."""

    label = "in-silico"
    phenomenon = Phenomenon("synapse_density",
                            "Number of synapses in a unit volume")

    _spine_density_per_unit_length = Record(mean = 1.05, std = 0.35)

    def __init__(self, circuit):
        """..."""
        self.__circuit = circuit
        self.__helper  = BlueBrainModelHelper(circuit = circuit)

    def __call__(self, roi):
        """Compute the expected synapse density
        in a region of interest (roi) of the
        circuit by multiplying the total dendrite
        length in the roi with the known synapse
        density per unit length.
        """
        mean = self._spine_density_per_unit_length.mean
        std  = self._spine_density_per_unit_length.std

        return self.__helper\
                   .spine_count_density(roi,
                                         spine_density_per_unit_len_mean=mean,
                                         spine_density_per_unit_len_std=std)
