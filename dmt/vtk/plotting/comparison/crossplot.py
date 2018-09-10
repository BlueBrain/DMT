"""Crosses to compare two equivalent data."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.plotting import golden_figure
from dmt.vtk.plotting.comparison import ComparisonPlot
from dmt.vtk.utils.logging import Logger
from dmt.vtk.utils.collections import Record

class CrossPlotComparison(ComparisonPlot):
    """Compare two datasets with cross plot.
    A ComparisonPlot will hold data that it will be plot against one or more
    other datasets.
    """

    def __init__(self, *args, **kwargs):
        """..."""
        self._logger = Logger(name="CrossPlotComparison Log")
        super(CrossPlotComparison, self).__init__(*args, **kwargs)

    @property
    def compared_datasets(self):
        """..."""
        cv = self.compared_values[0]
        try:
            data = self.comparison_data.xs(cv.name, level=self.comparison_level)
            return [Record(data=data, label=cv.label)]
        except Exception as e:
            self._logger.warning("""Could not get comparison data with
            name and level. Exception {}""".format(e))


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
        ys = list(self._data["mean"].values)
        xdata = self.compared_datasets[0]
        xs = list(xdata.data["mean"].values)
        plt.errorbar(xs, ys, fmt="o",
                     xerr=xdata.data["std"].values,
                     yerr=self._data["std"].values)
        min_val = np.min(xs + ys)
        max_val = np.max(xs + ys)
        plt.plot([min_val, max_val], [min_val, max_val], "-")

        plt.title(self.title, fontsize=24)
        plt.xlabel(self._label, fontsize=20)
        #plt.xticks(xs)
        plt.ylabel(xdata.label, fontsize=20)

        fontP = FontProperties()
        fontP.set_size('small')

        if save:
            return self.save(fig)

        return fig
