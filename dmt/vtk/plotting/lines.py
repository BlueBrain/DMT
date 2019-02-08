"""Class to help plot lines."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.plotting import golden_figure, Plot



class LinePlot(Plot):
    """Class to help plot lines."""

    def __init__(self,
            *args, **kwargs):
        """Initialize bar plot specific attributes."""
        self.line_point_types=\
            kwargs.get(
                'line_point_types',
                ['-o', '--o', '-s', '--s'])
        super().__init__(
            *args, **kwargs)

    def plot(self,
            with_customization=None):
        """Make the line plot.
        """

        self._logger.debug(
            self._logger.get_source_info(),
            "{} instance will plot data: ".format(
                self.__class__.__name__),
            "{}".format(self._data))

        dataframe=\
            self.get_plotting_dataframe()
        figure=\
            golden_figure(
                height=self._height,
                width=self._width)
        axes=\
            figure.add_subplot(
                111)
        a_plot=\
           axes.errorbar(
               dataframe.index,
               dataframe['mean'].values,
               yerr=dataframe['std'].values,
               fmt=self._colors[0] + self.line_point_types[0])
        plt.title(
            self._title,
            fontsize=24)
        plt.xlabel(
            self._xlabel,
            fontsize=20)
        # plt.xticks(
        #     np.arange(dataframe.shape[0]),
        #     dataframe.index)
        plt.ylabel(
            self._ylabel,
            fontsize=20)
        fontP=\
            FontProperties()
        plt.legend(
            prop=fontP,
            loc=self._legend_loc)
        return figure
