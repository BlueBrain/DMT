"""
Plotting for DMT
"""
from abc import abstractmethod
from collections import OrderedDict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dmt.tk.field import Field, LambdaField,  ABCWithFields

golden_aspect_ratio = 0.5 * (1. + np.sqrt(5)) 

def golden_figure(width:int =None, height:int =None):
    """
    Figure with the golden-ratio as its aspect ratio.
    """
    golden_height = 10. if width is None else 2. * width / (1. + np.sqrt(5))
    height = golden_height if height is None else height
    width = golden_aspect_ratio * height if width is None else width

    fig, ax = plt.subplots()
    fig.set_size_inches(width, height)
    return fig, ax


class BasePlotter(ABCWithFields):
    """
    Abstract base class for plotting.
    """
    title = Field(
        """
        Title to be displayed on the figure produced.
        """,
        __default_value__="")
    xvar = Field(
        """
        Column in the data-frame to be plotted along the x-axis.
        """)
    xlabel = LambdaField(
        """
        The label to be displayed along the x-axis.
        """,
        lambda self: self.xvar)
    yvar = Field(
        """
        Column in the data-frame to be plotted along the y-axis.
        """)
    ylabel = LambdaField(
        """
        The label to be displayed along the y-axis.
        """,
        lambda self: self.yvar)
    gvar = Field(
        """
        Column in the data-frame that will be used to group data.
        (x, y) data for the same value of gvar will be plotted with the
        same decorations.
        A default value of empty string will indicate that there is no
        variable to group the data by.
        """,
        __default_value__="")
    fvar = Field(
        """
        Facet Variable: Column in the dataframe that will be plotted on several
        faces. A default value of empty string will be interpreted as not set,
        and hence there will be only one face in the figure.
        """,
        __default_value__="")
    number_columns = LambdaField(
        """
        Number of columns in the figure.
        """,
        lambda self: None if not self.fvar else 3)
    height_figure = Field(
        """
        Height of the figure.
        """,
        __default_value__ = 8.)
    aspect_ratio_figure = Field(
        """
        Aspect ratio width / height for the figure.
        """,
        __default_value__=golden_aspect_ratio)
    confidence_interval = Field(
        """
        float or “sd” or None, optional
        Size of confidence intervals to draw around estimated values.
        If “sd”, skip bootstrapping and draw the standard deviation of the
        observations. If None, no bootstrapping will be performed,
        and error bars will not be drawn.
        """,
        __default_value__="sd")

    @abstractmethod
    def get_figure(self, *args, **kwargds):
        """Every `Plotter` must implement."""
        raise NotImplementedError

    def get_figures(self, *args, **kwargs):
        """
        Package figure into an OrderedDict.
        """
        return OrderedDict([
            (self.yvar, self.get_figure(*args, **kwargs))])

    def __call__(self,
            *args, **kwargs):
        """
        Make this class a callable,
        so that it can masquerade as a function!
        """
        return self.get_figures(*args, **kwargs)


from .bars import Bars
from .crosses import Crosses
from .heatmap import HeatMap
from .lines import LinePlot
