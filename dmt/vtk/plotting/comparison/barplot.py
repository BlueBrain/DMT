"""Vertical bar plot to compare datasets."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.plotting import golden_figure
from dmt.vtk.plotting.comparison import ComparisonPlot

class BarPlotComparison(ComparisonPlot):
    """Compare two or more datasets with a barplot."""

    def __init__(self, *args, **kwargs):
        """..."""
        super(BarPlotComparison, self).__init__(*args, **kwargs)

    @property
    def compared_datasets(self):
        for cv in self.compared_values:
            label = cv.label
            data = self.comparison_data.xs(cv.name, level=self.comparison_level)
            yield (label, data)

    def plot(self, with_customiztion=None):
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
        #self.logger.source_info()
        self.logger.debug(
            self.logger.get_source_info(),
            "{} instance will compare data:".format(self.__class__.__name__),
            "{}".format(self._data),
            "against validation data: ",
            "{}".format(self._comparison_data)
        )
        compdata = self._data
        datasets = self._comparison_data
        compared_values = self.compared_values
        comparison_level = self._comparison_level
        if compdata.shape[0] == 0:
            raise ValueError("Empty comparison data.")

        fig = golden_figure(height=self.height, width=self.width)

        nbar =  1 + len(compared_values)
        width = 1.0 / (1.0 + nbar)

        xs = self.given_variable_values
        x = np.arange(len(xs))
        x0 = x - (1 + nbar / 2) * width

        def _plot_index(i, df, label):
            return plt.bar(x0 + index * width,
                           df["mean"].values,
                           width,
                           color=self.colors[(index-1) % len(self.colors)],
                           yerr=df["std"].values,
                           label=label)
        index = 1

        if self._label in self._data:
            _plot_index(index, self._data[self._label], self._label)
        else:
            _plot_index(index, self._data, self._label)

        index += 1
        for data_label, data_frame in self.compared_datasets:
            a_plot = _plot_index(index, data_frame, data_label)
            index += 1

        plt.title(self.title, fontsize=24)
        plt.xlabel(self.xlabel, fontsize=20)
        plt.xticks(x - width / 2., xs)
        plt.ylabel(self.ylabel, fontsize=20)

        fontP = FontProperties()
        fontP.set_size('small')
        plt.legend(prop=fontP, loc=self.legend_loc)

        return fig
