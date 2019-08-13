"""
Circuit composition analyses.
"""

import pandas
from .. import CompositionAnalysis
from ..interfaces import CellDensityAdapterInterface
from dmt.tk.plotting.bar import BarPlotter
from dmt.tk.phenomenon import Phenomenon


class ByLayerCellDensityAnalysis(
        CompositionAnalysis):
    """
    Analysis of cell density by layer.
    The `Field` values assigned below are the simplest applicable values.
    You may customize them.
    """
    phenomenon = Phenomenon(
        "Cell Density",
        "Count of cells in a unit volume.",
        group="composition")

    measurement_parameters = pandas\
        .DataFrame({
            "layer": 2 * [1, 2, 3, 4, 5, 6]})

    AdapterInterface =\
        CellDensityAdapterInterface

    plotting_parameters ={
        "x": "layer",
        "y": phenomenon.label}

    plotter = BarPlotter(
        xvar="layer",
        xlabel="Layer",
        yvar=phenomenon.label,
        ylabel=phenomenon.name)

    def get_measurement(self,
            *args, **kwargs):
        """
        This sticks in the method to measure the circuit_model
        """
        return self.adapter.get_cell_density( *args, **kwargs)
