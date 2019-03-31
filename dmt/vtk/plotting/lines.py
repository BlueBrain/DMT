"""Class to help plot lines."""

import numbers
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
            with_customization={}):
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

        def __is_numeric_axis(axis_values):
            """.."""

        def __get_axis_extrema(
                axis_label,
                axis_values):
            """..."""
            self._logger.debug(
                self._logger.get_source_info(),
                "get axis {} extreme values from self.axis {}: or data "\
                .format(
                    axis_label,
                    self.axis))
            axis_values_ordered=\
                np.sort(axis_values)
            axis_min=\
                self.axis\
                    .get(
                        "{}min".format(axis_label),
                        axis_values_ordered[0] - (
                            axis_values_ordered[1]-axis_values_ordered[0])/2.)
            axis_max=\
                self.axis\
                    .get(
                        "{}max".format(axis_label),
                        axis_values_ordered[-1] + (
                            axis_values_ordered[-1]-axis_values_ordered[-2])/2.)
            return (axis_min, axis_max)

        y_values=\
            dataframe["mean"].values
        yerr_values=\
            dataframe["std"].values
        try:
            x_values=\
                dataframe.index.values
            self._logger.debug(
                self._logger.get_source_info(),
                "problematic lengths ? X: {}, Y: {}"\
                .format(x_values, y_values),
                "lengths are {}, {}"\
                .format(
                    len(x_values),
                    len(y_values)))
            a_plot=\
                axes.errorbar(
                    x_values,
                    y_values,
                    yerr=yerr_values,
                    fmt=self._colors[0] + self.line_point_types[0])
            x_ticks_rotation=\
                0
        except ValueError as value_error:
            self._logger.alert(
                self._logger.get_source_info(),
                "Value error raised {}".format(value_error),
                "Possible the index is not an Array of floats",
                "We do have some cases where the index are intervals",
                "that is they are (flaot, float) tuples",
                "will try assuming that")
            x_values=[
                np.mean(x_interval)
                for x_interval in dataframe.index.values]
            a_plot=\
                axes.errorbar(
                    x_values,
                    y_values,
                    yerr=yerr_values,
                    fmt=self._colors[0] + self.line_point_types[0])
            x_ticks_rotation=\
                90
        if len(x_values) > 1 and isinstance(x_values[0], numbers.Number):
            xmin, xmax=\
                __get_axis_extrema(
                    "x",
                    x_values)
            self._logger.debug(
                self._logger.get_source_info(),
                "plot with x-axis range {}, {}"\
                .format(
                    xmin, xmax))
            plt.xlim(
                xmin, xmax)
        if len(y_values) > 1:
            ymin, ymax=\
                __get_axis_extrema(
                    "y",
                    y_values + yerr_values)
            self._logger.debug(
                self._logger.get_source_info(),
                "plot with y-axis range {}, {}"\
                .format(
                    ymin, ymax))
            plt.ylim(
                ymin, ymax)
                
        plt.xticks(
            x_values,
            dataframe.index.values,
            rotation=x_ticks_rotation)
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
