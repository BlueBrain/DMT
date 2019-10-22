"""Class to help plot bars."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import pylab
from matplotlib.font_manager import FontProperties
from dmt.vtk.plotting import golden_figure, Plot, MultiPlot



class BarPlot(Plot):
    """Class to  plot bars."""

    def __init__(self,
            *args, **kwargs):
        """Initialize bar plot specific attributes."""
        super().__init__(
            *args, **kwargs)

    def plot(self,
            with_customization={}):
        """Make the bar plot.
        """
        print(with_customization)
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
                color=with_customization.get(
                    "color", self._colors[0]),
                yerr=dataframe["std"].values)
        plt.title(
            self.title,
            fontsize=24)
        plt.xlabel(
            self.xlabel,
            fontsize=24)
        plt.xticks(
            np.arange(dataframe.shape[0]),
            dataframe.index,
            fontsize=12,
            rotation=with_customization.get("xticks_rotation", 0))
        plt.ylabel(
            self.ylabel,
            fontsize=20)
        fontP=\
            FontProperties()
        try:
            plt.legend(
                **with_customization["legend"])
        except:
            plt.legend(
                prop=fontP, loc=self._legend_loc)
        return figure


class MultiBarPlot(
        MultiPlot):
    """Multiple bar plots"""
    BasePlotType= BarPlot

# class MultiBarPlot(
#         MultiPlot):
#     """plot several bar plots"""
#     def __init__(self,
#             measurement,
#             *args, **kwargs):
#         """..."""
#         super().__init__(
#             measurement,
#             BasePlotType=BarPlot)

