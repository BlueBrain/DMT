"""
Circuit composition analyses.
"""

import pandas
from .. import CompositionAnalysis
from ..interfaces import CellDensityAdapterInterface
from dmt.tk.field import lazyproperty
from dmt.tk.plotting.bar import BarPlot
from dmt.tk.phenomenon import Phenomenon


class ByLayerCompositionAnalysis(
        CompositionAnalysis):
    """
    Common attributes of all by layer `CompositionAnalysis` types.
    """
    measurement_parameters = pandas\
        .DataFrame({
            "layer": [1, 2, 3, 4, 5, 6]})

    @lazyproperty
    def plot(self):
        return BarPlot(
            xvar="layer",
            xlabel="Layer",
            yvar=self.phenomenon.label,
            ylabel=self.phenomenon.name)

cell_density_phenomenon = Phenomenon(
    "Cell Density",
    "Count of cells in a unit volume.",
    group="composition")

class ByLayerCellDensityAnalysis(
        ByLayerCompositionAnalysis):
    """
    Analysis of cell density by layer.
    The `Field` values assigned below are the simplest applicable values.
    You may customize them.
    """
    phenomenon = cell_density_phenomenon

    AdapterInterface =\
        CellDensityAdapterInterface

    # def get_measurement(self,
    #         *args, **kwargs):
    #     """
    #     This sticks in the method to measure the circuit_model
    #     """
    #     return self.adapter.get_cell_density( *args, **kwargs)
