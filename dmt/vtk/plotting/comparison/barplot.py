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

    def plot(self, with_customiztion=None, save=True):
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
        compdata = self._data
        print("plot model data")
        print(self._data)
        datasets = self._comparison_data
        print("validation datasets")
        print(datasets)
        compared_values = self.compared_values
        comparison_level = self._comparison_level
        given = self._given_vars
        if compdata.shape[0] == 0:
            raise ValueError("Empty comparison data.")

        fig = golden_figure(height=self.height, width=self.width)

        nbar =  1 + len(compared_values)
        print("make {} bars".format(nbar))
        width = 1.0 / (1.0 + nbar)
        
        if given:
           if isinstance(given, list): 
               xs = datasets.index.levels[ datasets.index.names.index(given[0])]
           else:
               xs = datasets.index.levels[ datasets.index.names.index(given)]
        else:
            xs = datasets.index

        g = given[0] if isinstance(given, list) else given
        print("given ", g)
        i = datasets.index.names.index(g) if g else None
        xs = self._data.index if not given else datasets.index.levels[i]
        print("x axis will be ", xs)
        x = np.arange(len(xs))
        print("that resolves to ", x)
        x0 = x - (nbar / 2) * width
        def _plot_index(i, df, label):
            return plt.bar(x0 + index * width,
                           df["mean"].values,
                           width,
                           color=self.colors[(index-1) % len(self.colors)],
                           yerr=df["std"].values,
                           label=label)
        index = 1
        _plot_index(index, self._data, "in-silico")
        index += 1
        for cv in compared_values:
            df = datasets.xs(cv.name, level=comparison_level)
            print(cv)
            print(df)
            a_plot = _plot_index(index, df, cv.label)
            index += 1

        plt.title(self.title, fontsize=24)
        plt.xlabel(self.xlabel, fontsize=20)
        plt.xticks(x - width / 2., xs)
        plt.ylabel(self.ylabel, fontsize=20)

        fontP = FontProperties()
        fontP.set_size('small')
        plt.legend(prop=fontP, loc=self.legend_loc)

        if save:
            return self.save(fig)

        return fig
