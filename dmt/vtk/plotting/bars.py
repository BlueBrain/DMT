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
        self.logger.debug(
            self.logger.get_source_info(),
            "{} instance will plot data: ".format(
                self.__class__.__name__),
            "{}".format(self._data))

        dataframe=\
            self._data[self._label]\
            if self._label in self._data\
               else self._data
        figure=\
            golden_figure(
                height=self.height,
                width=self.width)
        a_plot=\
            plt.bar(
                np.arange(dataframe.shape[0]),
                dataframe["mean"].values,
                color=self.colors[0],
                yerr=dataframe["std"].values)
        plt.title(
            self.title,
            fontsize=24)
        plt.xlabel(
            self.xlabel,
            fontsize=20)
        plt.xticks(
            np.arange(dataframe.shape[0]),
            dataframe.index)
        plt.ylabel(
            self.ylabel,
            fontsize=20)
        fontP=\
            FontProperties()
        plt.legend(
            prop=fontP,
            loc=self.legend_loc)
        return figure
