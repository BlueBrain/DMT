"""Circuit composition measurements for Blue Brain circuits."""
import numpy as np
import pandas as pd
from bluepy.v2.enums import Cell
from dmt.vtk import measurement
from dmt.vtk.phenomenon import Phenomenon
from dmt.vtk.utils.collections import Record
from neuro_dmt.utils.cell_type import CellType
from neuro_dmt.models.bluebrain.circuit import BlueBrainModelHelper

class CompositionMeasurementMethd(
        measurement.Method):
    """Common attributes of composition measurement.Method"""


    def __init__(self,
            circuit,
            by_property=None,
            for_cell_type=CellType.Any,
            *args, **kwargs):
        """..."""
        self._property = by_property
        self._cell_type = for_cell_type
        self._circuit = circuit
        self._helper = BlueBrainModelHelper(circuit=circuit)

        if "label" not in kwargs:
            self.label = "in-silico"
        if "return_type" not in kwargs:
            kwargs["return_type"]\
                = float if not by_property else pd.Series
        super().__init__(
            *args, **kwargs)


class CellDensity(
        CompositionMeasurementMethd):
    """..."""

    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        super().__init__(
            circuit,
            phenomenon=Phenomenon(
                "Cell Density",
                "Number of cells in a unit volume"),
            units="1000/mm^3",
            *args, **kwargs)

    def __call__(self,
            region_of_interest):
        """Number of cells in a unit volume, [1000/mm^3]"""
        cell_counts\
            =  self._helper.get_cell_counts(
                region_of_interest,
                by_cell_property=self._property,
                for_given_cell_type=self._cell_type)
        return 1.e6 * cell_counts / region_of_interest.volume


class CellRatio(
        CompositionMeasurementMethd):
    """..."""

    def __init__(self,
            circuit,
            *args, **kwargs):
        """..."""
        super().__init__(
            circuit,
            by_property=Cell.SYNAPSE_CLASS,
            phenomenon=Phenomenon(
                "cell_ratio",
                "Fraction of inhibitory cells in the circuit."),
            units="Count",
            return_type=float,
            *args, **kwargs)

    def __call__(self,
            region_of_interest):
        """Ratio of the number of inhibitory cells to
        the number of excitatory cells in a region of interest
        of the circuit.
        """
        cell_counts\
            = self._helper.get_cell_counts(
                region_of_interest,
                by_cell_property=self._property,
                for_given_cell_type=self._cell_type)
        return (1.0 + cell_counts['INH']) / (1.0 + np.sum(cell_counts))



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
