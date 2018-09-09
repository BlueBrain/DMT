"""Crosses to compare two equivalent data."""

import numpy as np
from matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.plotting import golden_figure
from dmt.vtk.plotting.comparison import ComparisonPlot

class CrossPlotComparison(ComparisonPlot):
    """Compare two datasets with cross plot.
    A ComparisonPlot will hold data that it will be plot against one or more
    other datasets.
    """

    def __init__(self, *args, **kwargs):
        """..."""
        super(CrossPlotComparison, self).__init__(*args, **kwargs)

    @property
    def compared_datasets(self):
        if self._comparison_level is  None: #comparison_level not set



    def plot(self, with_customization=None, save=True):
        """
        Compare this ComparisonPlot's data against those in datasets.

        Parameters
        ------------------------------------------------------------------------
        datasets  :: Either[ DataFrame[mean :: Double, std  :: Double],
        ~                    DataFrame[mean :: Double]] ]#with Multindex
        comparison_level  :: Either[String, Integer], #Level in datasets to be compared
        compared_values :: List[Record[ label :: T,     #values to be compared,
        ~                               name :: String]]#can be any non-Nonetype
        ~                      
        given :: List[Either[Integer, String]] #other levels to show the result for
        """
        fig = golden_figure(height=self.height, width=self.width)
        xs = self._comparison_data.xs(self.compared_values[0],
                                      level=self.comparison_)
        plt.plot(
            self.compared_datasets[0]["mean"].values,
            self._data["mean"].values,
            "o",
            xerr=self.compared_datasets[0]["std"].values
            yerr=self._data["std"].values,
        )
