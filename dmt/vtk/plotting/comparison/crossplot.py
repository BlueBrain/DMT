"""Crosses to compare two equivalent data."""
import numpy as np
import pandas as pd
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
        ydata = self._data
        xdata = self.compared_datasets[0].data
        given = self.given
        given_values = self.level_values(given) if given else self._data.index
        def __get_row(data_frame, given_val):
            """..."""
            print("get row {} of dataframe {}".format(given_val, data_frame))
            if given and isinstance(data_frame.index, pd.MultiIndex):
                return data_frame.xs(given_val, level=given)

            return data_frame.loc[given_val]

        print("xdata: ")
        print(xdata)
        print("ydata:")
        print(ydata)
            
        for v in given_values:
            print("for given {} xdata: {} ydata {}"\
                  .format(v, __get_row(xdata, v), __get_row(ydata, v)))

        ys = ydata["mean"].values
        yerr = ydata["std"].values
        ymax = np.max(ys + yerr)
        ymin = np.min(ys - yerr)

        xs = xdata.data["mean"].values
        xerr = xdata.data["std"].values
        xmax = np.max(xs + xerr)
        xmin = np.min(xs - xerr)

        plt.errorbar(xs, ys, fmt="o", xerr=xerr, yerr=yerr)

        min_val = min(xmin,  ymin)
        max_val = np.max(xmax, ymax)
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
