"""
Circuit composition analyses.
"""
import pandas
from .. import CompositionAnalysis
from ..interfaces import CellDensityAdapterInterface
from dmt.tk.field import lazyproperty
from dmt.tk.plotting.bars import Bars
from dmt.tk.reporting import Report
from dmt.tk.phenomenon import Phenomenon
from dmt.tk.parameters import Parameters

class ByLayerCompositionAnalysis(
        CompositionAnalysis):
    """
    Common attributes of all by layer `CompositionAnalysis` types.
    """
    measurement_parameters = Parameters(
        pandas.DataFrame({"layer": [1, 2, 3, 4, 5, 6]}))

    @lazyproperty
    def plotter(self):
        return Bars(
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

    def get_report(self,
            circuit_model,
            *args, **kwargs):
        """
        Get a report for the given `circuit_model`.

        `get_report` method appears in this sub-class because
        some `Fields` of a `Report` depend on the final `Analysis` class.
        """
        return Report(
            figures={
                "cell_density": self.get_figure(circuit_model=circuit_model)},
            introduction="Cell density of a brain circuit, measured by layer.",
            methods=self.adapter_method.__doc__,
            results="Results are presented in the figure.",
            discussion="To be provided after a review of the results")

