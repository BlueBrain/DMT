"""Class to help plot bars."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.plotting import golden_figure, Plot



class BarPlot(Plot):
    """Class to  plot bars."""

    def __init__(self,
            *args, **kwargs):
        """Initialize bar plot specific attributes."""
        super().__init__(
            *args, **kwargs)

    def plot(self,
            with_customization=None):
        """Make the bar plot.
        """
        dataframe=\
            self.get_plotting_dataframe()
        figure=\
            golden_figure(
                height=self._height,
                width=self._width)
        a_plot=\
            plt.bar(
                np.arange(dataframe.shape[0]),
                dataframe["mean"].values,
                color=self._colors[0],
                yerr=dataframe["std"].values)
        plt.title(
            self._title,
            fontsize=24)
        plt.xlabel(
            self._xlabel,
            fontsize=20)
        plt.xticks(
            np.arange(dataframe.shape[0]),
            dataframe.index)
        plt.ylabel(
            self._ylabel,
            fontsize=20)
        fontP=\
            FontProperties()
        plt.legend(
            prop=fontP,
            loc=self._legend_loc)
        return figure
