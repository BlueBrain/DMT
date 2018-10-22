"""Circuit composition measurements for Blue Brain circuits."""
import numpy as np
import pandas as pd
from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper

class CellDensity(
        measurement.Method):
    """..."""

    label = "in-silico"
    phenomenon = Phenomenon("Cell Density", "Number of cells in a unit volume")
    units = "1000/mm^3"

    def __init__(self,
            circuit,
            by_property=None,
            for_cell_type={},
            *args, **kwargs):
        """..."""
        self.__property = by_property
        self.__cell_type = for_cell_type
        self.__circuit = circuit
        self.__helper = BlueBrainModelHelper(circuit=circuit)
        self.__return_type = float if not by_property else pd.Series

    def __call__(self,
            region_of_interest):
        """Number of cells in a unit volume, [1000/mm^3]"""
        cell_counts\
            =  self.__helper.get_cell_counts(
                region_of_interest,
                by_cell_property=self.__property,
                for_given_cell_type=self.__cell_type)
        return 1.e6 * cell_counts / region_of_interest.volume


class CellRatio(measurement.Method):
    """..."""

    label = "in-silico"
    phenomenon = Phenomenon("cell_ratio",
                            "Fraction of inhibitory cells in the circuit.")
    units = "Count"

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

    
class InhibitorySynapseDensity(measurement.Method):
    """..."""

    label = "in-silico"
    phenomenon = Phenomenon("inhibitor_synapse_density",
                            "Number of inhibitory synapses in a unit volume")
    units = "1000/mm^3" #not sure... check 

    def __init__(self, circuit):
        """..."""
        self.__circuit = circuit
        self.__helper  = BlueBrainModelHelper(circuit = circuit)

    def __call__(self, roi):
        """Count the number of inhibitory synapses within a
        region of interest (roi), and divides the number by the roi's volume.
        """
        return self.__helper.synapse_density(roi, scale_factor=1.e-9)["INH"]


class ExtrinsicIntrinsicSynapseDensity(measurement.Method):
    """..."""

    label = "in-silico"
    phenomenon = Phenomenon("synapse_density",
                            "Number of synapses in a unit volume")
    units = "1000/mm^3" #not sure... check 

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
