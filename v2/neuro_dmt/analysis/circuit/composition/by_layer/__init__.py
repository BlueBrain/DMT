"""
Circuit composition analyses.
"""

import pandas
from .. import CompositionAnalysis
from ..interfaces import CellDensityAdapterInterface
from dmt.tk.phenomenon import Phenomenon


class ByLayerCellDensityAnalysis(
        CompositionAnalysis):
    """
    Analysis of cell density by layer.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="composition")

    measurement_parameters = pandas\
        .Index([1, 2, 3, 4, 5, 6], name="layer")

    AdapterInterface =\
        CellDensityAdapterInterface

    plotting_parameters ={
        "x": "layer",
        "y": phenomenon.label}

    def get_measurement(self,
            *args, **kwargs):
        """
        This sticks in the method to measure the circuit_model
        """
        return self.adapter.get_cell_density( *args, **kwargs)
